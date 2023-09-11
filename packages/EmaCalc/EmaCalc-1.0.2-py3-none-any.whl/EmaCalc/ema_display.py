"""This module defines classes and functions to display analysis results
given an ema_model.EmaModel instance,
learned from a set of data from an EMA study.

Results are shown as figures and tables.
Figures can be saved in any file format allowed by Matplotlib, e.g.,
    'pdf', 'png', 'jpg', 'eps'.
Tables can be saved in any file format allowed by Pandas, e.g.,
    'txt', 'tex', 'csv', 'xlsx'.
Thus, both figures and tables can be easily imported into a LaTeX or other word-processing document.

Plot properties may be controlled in detail by keyword arguments to
    method EmaDisplaySet.show(...), either as
1: keyword argument 'mpl_style' with previously defined matplotlib style sheet(s)
2: keyword argument 'mpl_params' as a dict with specific matplotlib parameters
3: setting specific parameters in ema_display.FMT, or ema_display_format.FMT,
    e.g., 'colors' and 'markers'.


*** Main Class:

EmaDisplaySet = a structured container for all display results

Each display element can be accessed and modified by the user, before saving.

The display set can include data for three types of predictive distributions:
*: a random individual in the Population from which a group of respondents was recruited,
    (most relevant for an experiment aiming to predict the success of a new product,
    among individual potential future customers in a population)
*: the mean (=median) in the Population from which a group of test participants were recruited
    (with interpretation most similar to a conventional significance test)
*: each individual respondent in a Group of test participants, with observed EMA data


*** Usage Example:
    See main scripts run_ema and run_sim

Figures and tables are automatically assigned descriptive names,
and saved in a directory tree with names constructed from labels of Groups,
and requested population / participant results.

Thus, after saving, the display files are stored as, e.g.,
result_path / group / 'random_individual' / attributes / ....
result_path / group / 'random_individual' / situations / ....
result_path / group / 'participants' / participant_id / attributes / ....
result_path / group / 'participants' / participant_id / situations / ....
result_path / 'group_effects' / 'population_mean' / attributes / ...  (if more than one group)

*** Version History:
* Version 1.0.2:
2023-09-10, removed work-around for a Pandas bug which was fixed in Pandas v. 2.1.0
2023-09-09, fixed a KeyError bug in CountDisplay.show(), for the case with several situation dimensions.

* Version 1.0.1:
2023-05-23, logger warning in EmaDisplaySet.show for requested count with no data

* Version 1.0.0:
2023-04-29, AttributeProfile, SituationProfile work-around for Pandas groupby sort bug, reported,
            to be fixed in Pandas v. 2.0.2 or 2.1 ?
2023-04-22, adapted to simplified group-key representation in ema_data classes

* Version 0.9.6:
2023-04-13, code cleanup: SituationProfile, AttributeProfile, SituationDiff, AttributeDiff
            using Pandas access to model results via new ema_base methods
2023-03-29, include percentile plots and tables in SituationDiff and AttributeDiff objects

* Version 0.9.5:
2023-03-07, include observed and model-estimated grade-count profiles,
            as requested by one reviewer for the Frontiers (2023) paper.
2023-02-27, allow user to set n_samples for population-model display calculations

* Version 0.9.4:
2023-01-22, added default subdirectory names to FMT dict, to allow user control

* Version 0.9.3:
2022-07-27, changed 'subject' -> 'participant',
    'population_individual' -> 'random_individual' in EmaDisplaySet arguments and output.
2022-07-27, allow matplotlib style sheet(s) and individual matplotlib params
    as keyword arguments to EmaDisplaySet.show(...)
2022-07-13, adapted to use new name scenario -> situation

* Version 0.9.2:
2022-06-17, enforce y_min=0 in situation probability percentile plot
2022-06-04, removed FMT['and_head'], not used in ema_display_format.tab_credible_diff

* Version 0.9.1:
2022-04-04, no NAP calculations here, done by ema_data.EmaDataSet instead
2022-04-04, no module-global formatting parameters in ema_display_format, only here
2022-04-04, EmaDisplaySet.save(...) takes file-format arguments
2022-04-04, make result tables as pandas DataFrame objects
2022-03-20, adapted to using Pandas CategoricalDtype instances in EmaFrame

* Version 0.8:
2022-02-15, minor cleanup of scenario profile tables

* Version 0.7:
2021-12-19, include table(s) of individual subject NAP results
2021-12-17, display aggregated Attribute effects weighted by Scenario probabilities

* Version 0.6:
2021-12-08, minor checks against numerical overflow

* Version 0.5.1
2021-11-27, allow NO Attributes in model, check display requests, minor cleanup

* Version 0.5
2021-11-05, copied from PairedCompCalc, modified for EmaCalc
2021-11-09, first functional version
"""
# ***** local superclass for pretty-printed repr() ?
# ***** allow several Attributes in single plot ?

import numpy as np
from pathlib import Path
import logging
import string
import pandas as pd

from . import ema_display_format as fmt
from .ema_data import group_dir_str

from samppy import credibility_pd as cred_pd

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST

# ---------------------------- Default display parameters
FMT = {'situations': (),    # sequence of situation dimensions or dimension-tuples to display
       'attributes': (),    # sequence of (attribute, situation_effect) to display
                            # situation_effect is a single situation key or tuple of such keys
       'grade_counts': (),  # sequence of (attribute, situation_effect) to display as histogram
       'percentiles': [5., 50., 95.],  # allowing 1, 2, 3, or more percentiles
       'credibility_limit': 0.7,  # min probability of jointly credible differences
       'grade_thresholds': True,  # include median response thresholds in plots
       'random_individual': True,  # show result for random individual in population
       'population_mean': True,  # show result for population mean
       'participants': False,   # show results for each respondent
       'scale_unit': '',  # scale unit for attribute plot axis
       'sit_probability': 'Situation Probability',  # label in figs and tables
       'credibility': 'Credibility',  # heading in difference table
       'population_mean_dir': 'population_mean',  # directory name
       'random_individual_dir': 'random_individual',  # directory name
       'participants_dir': 'participants',  # directory name
       'group_join_str': '_',   # between group dimension and category in path string
       'group_effects_dir': 'group_effects',  # directory name
       'n_samples': 1000,  # number of samples for percentile calculations
       }

DEFAULT_FIGURE_FORMAT = 'pdf'
DEFAULT_TABLE_FORMAT = 'txt'


def set_format_param(**kwargs):
    """Set / modify format parameters
    Called before any displays are generated.
    :param kwargs: dict with any formatting variables
    :return: None
    """
    other_fmt = dict()
    for (k, v) in kwargs.items():
        k = k.lower()
        if k in FMT:
            FMT[k] = v
        else:
            other_fmt[k] = v
    FMT['percentiles'].sort()  # ensure increasing values
    if len(other_fmt) > 0:
        # may include 'mpl_style' and 'mpl_params', and more...
        fmt.set_format_param(**other_fmt)


# ------------------------------------------------ Elementary Display Class:
class Profile:
    """Container for ONE requested profile display
    for ONE tuple of one or more situation dimensions,
    OR for ONE (attribute, situation_effect) request.
    """
    def __init__(self, plot=None, tab=None, diff=None,
                 path=None):
        """
        :param plot: (optional) ema_display_format.ResultPlot instance with profile plot
        :param tab: (optional) ema_display_format.ResultTable instance with same results tabulated.
        :param diff: (optional) ema_display_format.DiffTable instance with credible differences.
        :param path: (optional) Path to directory containing saved files from this Profile,
            assigned by save() method.
            File names are defined by sub-objects.
        """
        self.plot = plot
        self.tab = tab
        self.diff = diff
        self.path = path

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    def save(self, path,
             figure_format=None,
             table_format=None,
             **kwargs):
        """Save plot and table displays to files.
        May be called repeatedly with different file formats and kwargs.
        :param path: path to directory for saving files
        :param figure_format: (optional) single figure-file format string
        :param table_format: (optional) single table-file format string
        :param kwargs: (optional) additional parameters passed to ResultTable.save() method.
            NOTE: NO extra kwargs allowed for plot.save() method!
        :return: None
        """
        if figure_format is None and table_format is None:
            figure_format = DEFAULT_FIGURE_FORMAT
            table_format = DEFAULT_TABLE_FORMAT
        # One of them may be None -> only the other type of data are saved.
        path.mkdir(parents=True, exist_ok=True)
        self.path = path
        if figure_format is not None:
            if self.plot is not None:
                self.plot.save(path, figure_format=figure_format)
        if table_format is not None:
            if self.tab is not None:
                self.tab.save(path, table_format=table_format, **kwargs)
            if self.diff is not None:
                self.diff.save(path, table_format=table_format, **kwargs)


# ---------------------------------------------------------- Top Display Class:
class EmaDisplaySet:
    """Root container for all displays
    of selected predictive situation and attribute results
    from one ema_model.EmaModel instance learned from one ema_data.EmaDataSet instance.

    All display elements can be saved as files in a selected directory three.
    The complete instance can also be serialized and dumped to a pickle file,
    then re-loaded, edited, and re-saved, if user needs to modify some display element(s).
    """
    def __init__(self, group_head, groups, group_effects=None):
        """
        :param group_head: tuple group dimension labels, copied form EmaFrame instance
        :param groups: dict with (group_id, GroupDisplaySet) elements
        :param group_effects: (optional) single GroupEffectSet instance,
            showing jointly credible differences between groups,
            IFF there is more than one group
        """
        self.group_head = group_head  # copy from EmaModel.emf.group_head()
        self.groups = groups
        self.group_effects = group_effects

    def __repr__(self):  # *** general superclass for repr?
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    def save(self, dir_top, **kwargs):
        """Save all displays in a directory tree
        :param dir_top: Path or string with top directory for all displays
        :param kwargs: (optional) dict with any additional format parameters, e.g.,
            figure_format, table_format, and any Pandas file-writer parameters.
        :return: None
        """
        dir_top = Path(dir_top)
        for (g, g_display) in self.groups.items():
            # g = _dir_name(self.group_head, g, sep='/')
            g = group_dir_str(self.group_head, g, sep=FMT['group_join_str'])
            if len(g) == 0 or all(s in string.whitespace for s in g):
                g_display.save(dir_top, **kwargs)
            else:
                g_display.save(dir_top / g, **kwargs)
        if self.group_effects is not None:
            self.group_effects.save(dir_top / FMT['group_effects_dir'], **kwargs)

    @classmethod
    def show(cls, emm,
             situations=None,
             attributes=None,
             grade_counts=None,
             **kwargs):
        """Create requested displays for results from an EMA study,
        and store all display elements in a single structured object.
        :param emm: an ema_model.EmaModel instance, where
            emm.groups[group] is an ema_model.EmaGroupModel instance,
            emm.groups[group][participant_id] is an ema_model.EmaRespondentModel instance
        :param situations: (optional) list with selected situation dimensions to be displayed.
            situations[i] = a selected key in emm.emf.situation_dtypes, or a tuple of such keys.
        :param attributes: (optional) list with selected attribute displays to be displayed.
            attributes[i] = a tuple (attribute_key, sit_effect), where
                attribute_key is one key in emm.emf.attribute_grades,
                sit_effect is a situation dimension in emm.emf.situation_dtypes, or a tuple of such keys.
                A single key will yield the main effect of the named situation dimension.
                An effect tuple will also show interaction effects between situation dimensions,
                IFF the regression model has been set up to estimate such interaction effects.
        :param grade_counts: (optional) list with selected attribute grade counts to be displayed,
                given as single attribute key, or tuple (attribute_key, situation) .
        :param: kwargs: (optional) dict with any other display formatting parameters
            for ema_display.FMT and / or ema_display_format.FMT and / or matplotlib
        :return: a cls instance filled with display objects
        """
        # get default scale_unit from emm, if not in kwargs:
        if 'scale_unit' not in kwargs:
            kwargs['scale_unit'] = emm.base.rv_class.unit_label
        if situations is None:
            situations = [*emm.base.emf.situation_dtypes.keys()]
            # default showing only main effects for each situation dimension
        situations = [(sit,) if isinstance(sit, str) else sit
                      for sit in situations]  # ensure tuple elements
        # *** check that requested situations exist in model:
        missing_sit = [sit_tuple for sit_tuple in situations
                       if any(sit_ij not in emm.base.emf.situation_dtypes.keys()
                              for sit_ij in sit_tuple)]
        for sit in missing_sit:
            logger.warning(f'Situation dimension in {sit} unknown in the learned model.')
            situations.remove(sit)
        if attributes is None:
            attributes = []
        attributes = [(a, sit) if type(sit) is tuple else (a, (sit,))
                      for (a, sit) in attributes]
        # *** check that requested attribute effects exist in model
        missing_attr = [a_sit for a_sit in attributes
                        if a_sit[0] not in emm.base.emf.attribute_dtypes.keys()]
        for a_sit in missing_attr:
            logger.warning(f'Attribute effect {a_sit} unknown in the learned model.')
            attributes.remove(a_sit)
        if grade_counts is None:
            grade_counts = []
        grade_counts = [(gc,) if isinstance(gc, str) else gc
                        for gc in grade_counts]
        missing_counts = [c_sit for c_sit in grade_counts
                          if c_sit[0] not in emm.base.emf.attribute_dtypes.keys()]
        for c_sit in missing_counts:
            logger.warning(f'Requested count {c_sit} unknown in the data set.')
            grade_counts.remove(c_sit)
        set_format_param(situations=situations,
                         attributes=attributes,
                         grade_counts=grade_counts,
                         **kwargs)
        # display separate results for each group
        group_head = emm.base.emf.group_head()
        groups = {g: GroupDisplaySet.display(emm_g)
                  for (g, emm_g) in emm.groups.items()}

        if len(groups) > 1:
            group_effects = GroupEffectSet.display(emm)
        else:
            group_effects = None
        logger.info(fig_comments())
        logger.info(table_comments())
        return cls(group_head, groups, group_effects)


class GroupDisplaySet:
    """Container for all quality displays related to ONE study group:
    Predictive results for the population from which the participants were recruited,
    and for each individual participant, if requested by user.
    """
    def __init__(self,
                 population_mean=None,
                 random_individual=None,
                 participants=None,
                 counts=None):
        """
        :param population_mean: EmaDisplay instance, for population mean,
        :param random_individual: EmaDisplay instance, for random individual,
        :param participants: dict with elements (s_id: EmaDisplay instance) for participants in one group
            with situation and attribute results.
        :param counts: CountDisplay instance, for observed and model-estimated count profiles
        """
        self.population_mean = population_mean
        self.random_individual = random_individual
        self.participants = participants
        self.counts = counts

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    def save(self, path, **kwargs):
        """Save all stored display objects in their corresponding subdirectories
        """
        if self.population_mean is not None:
            self.population_mean.save(path / FMT['population_mean_dir'], **kwargs)
        if self.random_individual is not None:
            self.random_individual.save(path / FMT['random_individual_dir'], **kwargs)
        if self.participants is not None:
            for (s, s_disp) in self.participants.items():
                s_disp.save(path / FMT['participants_dir'] / str(s), **kwargs)
        if self.counts is not None:
            self.counts.save(path / 'counts', **kwargs)  # *****************

    @classmethod
    def display(cls, emm_g):
        """Generate all displays for ONE group
        :param emm_g: dict with elements (a_label: ema_group.EmaGroupModel)
        :return: cls instance with all displays for this group
        """
        pop_ind = None
        pop_mean = None
        participants = None
        counts = None
        if FMT['random_individual']:
            pop_ind = EmaDisplay.display(emm_g.predictive_population_ind())
        if FMT['population_mean']:
            pop_mean = EmaDisplay.display(emm_g.predictive_population_mean())
        if FMT['participants']:
            # logger.debug('Displaying participants:')
            participants = {s: EmaDisplay.display(s_model)
                            for (s, s_model) in emm_g.participants.items()}
        if FMT['grade_counts'] is not None and len(FMT['grade_counts']) > 0:
            counts = CountDisplay.show(emm_g)
        return cls(population_mean=pop_mean,
                   random_individual=pop_ind,
                   participants=participants,
                   counts=counts)


# ------------------------------------- Secondary-level displays
class EmaDisplay:
    """Container for all situation and attribute displays of model-estimated parameters
    for ONE (Sub-)Population, either random-individual or mean,
    OR for ONE participant.
    """
    def __init__(self, situations, attributes):
        """
        :param situations: dict with (situation_tuple, profile), where
            profile is a Profile instance for the selected situation_tuple
        :param attributes: dict with (attr_effect, profile), where
            profile is a Profile instance for the selected attr_effect
        """
        self.situations = situations
        self.attributes = attributes

    def save(self, path, **kwargs):
        """Save all stored display objects in specified (sub-)tree
        :param path: path to directory for saving
        :return: None
        """
        if len(self.situations) > 0:
            for (d, sit_display) in self.situations.items():
                sit_display.save(path / 'situations', **kwargs)
        if len(self.attributes) > 0:
            for (d, a_display) in self.attributes.items():
                a_display.save(path / 'attributes', **kwargs)

    @classmethod
    def display(cls, m_xi):
        """
        :param m_xi: probability model for ema_model parameter vector xi
            either for random individual, population mean, or individual participant
        :return: a cls instance
        """
        xi = m_xi.rvs(size=FMT['n_samples'])
        logger.debug(f'Using {len(xi)} samples')
        situations = {sit: SituationProfile.display(xi, m_xi, sit)
                      for sit in FMT['situations']}
        attributes = {a_effect: AttributeProfile.display(xi, m_xi, a_effect)
                      for a_effect in FMT['attributes']}
        return cls(situations, attributes)


class CountDisplay:
    """Container for attribute displays of grade-count distributions,
    including both observed and model-estimated EMA-counts,
    for ONE (Sub-)Population, (OR for ONE participant ? ********).
    """
    def __init__(self, attributes):
        """
        :param attributes: dict with (attr_effect, count-profile), where
            profile is a Profile instance for the selected attr_effect
        """
        self.attributes = attributes

    def save(self, path, **kwargs):
        """Save all stored display objects in specified (sub-)tree
        :param path: path to directory for saving
        :return: None
        """
        if len(self.attributes) > 0:
            for a_display in self.attributes.values():
                a_display.save(path, **kwargs)

    @classmethod
    def show(cls, g_model):
        """
        :param g_model: probability model for ema_model parameter vector xi
            either for random individual, population mean, or individual participant
        :return: a cls instance
        """
        def show_histogram(a_effect):
            if len(a_effect) == 1:
                (a, sit_case) = (a_effect[0], None)
            else:
                (a, sit_case) = a_effect
            # ******** check that sit_case includes only existing sitution keys ? ******
            df_obs = g_model.attribute_grade_count(a, groupby=sit_case)
            df_mod = g_model.rvs_grade_count(a, groupby=sit_case)
            q = np.array(FMT['percentiles']) / 100
            if sit_case is None:
                # df_obs is a Series object, make it a DataFrame with one row
                df_obs = df_obs.to_frame().T
                df_q = df_mod.quantile(q, numeric_only=True)
                fill_value = df_obs.index.values[0]
                i = ((fill_value, q) for q in df_q.index.values)
                df_q = df_q.set_index(keys=i)
            else:
                df_q = df_mod.groupby(level=sit_case,
                                      sort=False, group_keys=True).quantile(q,
                                                                            numeric_only=True)
            return Profile(plot=fmt.fig_category_barplot(df=df_obs, df_q=df_q,
                                                         x_label=a + ': Ordinal Grades',
                                                         y_label='EMA counts',
                                                         file_label=a)
                           )
        # ------------------------------------------

        attributes = {a_effect: show_histogram(a_effect)
                      for a_effect in FMT['grade_counts']}
        return cls(attributes)


# ----------------------------------------------------------------------
class SituationProfile(Profile):
    """Container for all displays of situation probability profiles
    in ONE (Sub-)Population, OR for ONE respondent.
    NOTE: situation profiles are displayed as
    CONDITIONAL probability of categories in ONE situation dimension,
    GIVEN categories in other dimension(s), if requested.
    """
    @classmethod
    def display(cls, xi, m_xi, sit_keys):
        """Generate a probability-profile display for selected distribution and factor
        :param xi: 2D array of parameter-vector samples drawn from m_xi
        :param m_xi: a population or individual model instance
        :param sit_keys: tuple of one or more key(s) selected from emf.situation_dtypes.keys()
        :return: single cls instance showing CONDITIONAL probabilities
            for sit_keys[0], GIVEN each combination (j1,..., jD) for sit_keys[1], ...
        """
        u_ds = m_xi.base.situation_prob_df(xi, groupby=sit_keys)
        # = pd.Series object with MultiIndex axes [sample, *sit_keys]
        quantiles = np.array(FMT['percentiles']) / 100.
        q_ds = u_ds.groupby(level=list(sit_keys),
                            sort=False, group_keys=True).quantile(quantiles,
                                                                  numeric_only=True)
        # = pd.Series object with MultiIndex axes [*sit_keys, quantiles]
        # q_ds_fix = _series_quantile_fix(u_ds, sit_keys)  # *** TEMP fix for Pandas bug
        # (u_mean, uh_q) = _entropy_quantiles(u_ds)  # Experiment 2023-06-xx. No useful results ***
        # # u_mean = mean conditional prob.mass for sit_keys[0], given each category in sit_keys[1:]
        # # uh_q = _entropy_quantiles(u_ds)
        # # = situation prob.mass vectors sorted by entropy quantiles.
        # fig_prob = fmt.fig_probmass(u_mean=u_mean, y_label=FMT['sit_probability'], u_q=uh_q)
        tab_perc = fmt.tab_percentiles(q_ds)
        fig_perc = fmt.fig_percentiles(tab_perc, y_label=FMT['sit_probability'], file_label='', y_min=0.)
        # ---------------------------------------- sit_keys differences
        # NOTE: Comparing CONDITIONAL probabilities of categories in FIRST sit_keys dimension,
        # GIVEN categories in other dimensions.
        d_pd = cred_pd.cred_diff(u_ds, diff_axis=sit_keys[0], case_axis=sit_keys[1:], p_lim=FMT['credibility_limit'])
        tab_diff = fmt.tab_credible_diff(d_pd, diff_head=sit_keys[0:1], cred_head=FMT['credibility'],
                                         case_head=sit_keys[1:], y_label=FMT['sit_probability'])
        # ---------------------------------------------------------------------
        # return cls(plot=fig_perc, tab=tab_perc, diff=tab_diff)
        return cls(plot=fig_perc, tab=tab_perc, diff=tab_diff)


class AttributeProfile(Profile):
    """Container for displays of ONE attribute value effect of situation(s),
    in ONE (Sub-)Population, OR for ONE respondent.

    NOTE: Latent-variable results are displayed for each Attribute,
    GIVEN Situation categories in requested Situation dimensions,
    averaged across all OTHER Situation dimensions,
    weighted by Situation probabilities in those dimensions.
    """
    # **** allow several attributes in one display ? *****
    @classmethod
    def display(cls, xi, m_xi, a_effect):
        """Create displays for a single attribute and requested situation effects
        :param xi: 2D array of parameter-vector samples drawn from m_xi
        :param m_xi: a population or individual model instance
        :param a_effect: tuple(attribute_key, sit_keys)
        :return: single cls instance with all displays
        """
        (a, sit_keys) = a_effect
        # --------------------------------------- thresholds, optional:
        if FMT['grade_thresholds']:
            tau = np.median(m_xi.base.attribute_tau(xi, a), axis=0)
            # tau[l] = l-th median rating threshold for attribute a, SAME for all situations
        else:
            tau = None
        # --------------------------------------- percentile table:
        theta_ds =  m_xi.base.attribute_theta_df(xi, a, groupby=sit_keys)
        # = pd.Series with MultiIndex [samples, *sit_keys]
        # ***** with UN-sorted sit_keys
        quantiles = np.array(FMT['percentiles']) / 100.
        theta_q = theta_ds.groupby(level=sit_keys,
                                   sort=False, group_keys=True).quantile(quantiles)
        # theta_q_fix = _series_quantile_fix(theta_ds, sit_keys)  # *** TEMP fix for Pandas bug
        tab_perc = fmt.tab_percentiles(theta_q, file_label=a)
        fig_perc = fmt.fig_percentiles(tab_perc, y_label=a + ' (' + str(FMT['scale_unit']) + ')',
                                       file_label=a,
                                       cat_limits=tau)
        # ---------------------------------------- attr differences
        # NOTE: comparing all situation-categories, in all requested sit_keys dimensions
        d_pd = cred_pd.cred_diff(theta_ds, diff_axis=sit_keys, p_lim=FMT['credibility_limit'])
        tab_diff = fmt.tab_credible_diff(d_pd, diff_head=sit_keys, cred_head=FMT['credibility'],
                                         y_label=a,
                                         file_label=a)
        return cls(plot=fig_perc, tab=tab_perc, diff=tab_diff)


# --------------------------------- classes for differences between groups
class GroupEffectSet:
    """Container for displays of differences between populations,
    as represented by participants in separate groups
    """
    def __init__(self, population_mean=None, random_individual=None):
        """
        :param population_mean: EmaGroupDiff instance
        :param random_individual: EmaGroupDiff instance
            both with results separated by groups
        """
        self.population_mean = population_mean
        self.random_individual = random_individual

    def save(self, path, **kwargs):
        """Save all stored display objects in their corresponding sub-trees
        """
        if self.population_mean is not None:
            self.population_mean.save(path / FMT['population_mean_dir'], **kwargs)
        if self.random_individual is not None:
            self.random_individual.save(path / FMT['random_individual_dir'], **kwargs)

    @classmethod
    def display(cls, emm):
        """Generate all displays for ONE group
        :param emm: ema_model.EmaModel instance with several groups
        :return: cls instance with all displays of differences
            between predictive distributions for
            population random individual, AND/OR
            population mean
        """
        pop_ind = None
        pop_mean = None
        if FMT['random_individual']:
            pop_ind = EmaGroupDiff.display(emm,
                                           {g: emm_g.predictive_population_ind()
                                            for (g, emm_g) in emm.groups.items()})
        if FMT['population_mean']:
            pop_mean = EmaGroupDiff.display(emm,
                                            {g: emm_g.predictive_population_mean()
                                             for (g, emm_g) in emm.groups.items()})
        return cls(population_mean=pop_mean,
                   random_individual=pop_ind)


class EmaGroupDiff:
    """Container for displays of differences between (Sub-)Populations
    represented by separate ema_model.EmaGroupModel instances.
    """
    def __init__(self, situations, attributes):
        """
        :param situations: dict with (situation_tuple, SituationDiff instance)
        :param attributes: dict with (attr_effect, AttributeDiff instance), where
        """
        self.situations = situations
        self.attributes = attributes

    def save(self, path, **kwargs):
        """Save all stored display objects in specified (sub-)tree
        """
        if len(self.situations) > 0:
            for (d, sit_display) in self.situations.items():
                sit_display.save(path / 'situations', **kwargs)
        if len(self.attributes) > 0:
            for (d, a_display) in self.attributes.items():
                a_display.save(path / 'attributes', **kwargs)

    @classmethod
    def display(cls, emm, groups):
        """
        :param emm: ema_model.EmaModel instance with several groups
        :param groups: dict with elements (g_id, g_model), where
            g_id is a tuple of one or more tuple(group_factor, factor_category),
            g_model is a predictive ema_model.PredictivePopulationModel instance
            i.e. NOT emm.groups
        :return: single cls instance
        """
        xi = [g_model.rvs(size=FMT['n_samples'])
              for g_model in groups.values()]
        # xi[g][s, :] = s-th sample of parameter vector for g-th group
        situations = {sc: SituationDiff.display(xi, emm, sc)
                      for sc in FMT['situations']}
        attributes = {a_effect: AttributeDiff.display(xi, emm, a_effect)
                      for a_effect in FMT['attributes']}
        return cls(situations, attributes)


class SituationDiff(Profile):
    @classmethod
    def display(cls, xi, emm, sit_keys):
        """Generate a probability-profile display for selected distribution and factor
        :param xi: list of 2D arrays of parameter-vector samples
            len(xi) == len(emm.groups)
        :param emm: ema_model.EmaModel object
        :param sit_keys: tuple of one or more key(s) selected from emf.situation_dtypes.keys()
        :return: single cls instance
        """
        # --------------------------------- situation prob. vs (sit_keys, groups):
        group_head = emm.base.emf.group_head()  # ********************
        group_cat = list(emm.groups.keys())
        u_groups = {g: emm.base.situation_prob_df(xi_g, groupby=sit_keys)
                    for (g, xi_g) in zip(group_cat, xi)}
        # = dict of pd.Series objects, each with MultiIndex [sample, *sit_keys]
        u_ds = pd.concat(u_groups, axis=0, names=list(group_head))
        quantiles = np.array(FMT['percentiles']) / 100.
        u_q = u_ds.groupby(level=list(sit_keys) + list(group_head),
                           sort=False, group_keys=True).quantile(quantiles,
                                                                 numeric_only=True)
        # = pd.Series with MultiIndex [*sit_keys, quantiles]
        tab_perc = fmt.tab_percentiles(u_q)
        fig_perc = fmt.fig_percentiles(tab_perc, y_label=FMT['sit_probability'], file_label='', y_min=0.)
        # ---------------------------------------- group differences by sit_keys
        # NOTE: Comparing CONDITIONAL probabilities of categories in FIRST sit_keys dimension,
        # GIVEN categories in other dimensions.
        d_pd = cred_pd.cred_group_diff(u_groups, group_axis=group_head,
                                       case_axis=sit_keys,
                                       p_lim=FMT['credibility_limit'])
        tab_diff = fmt.tab_credible_diff(d_pd, diff_head=group_head, cred_head=FMT['credibility'], case_head=sit_keys,
                                         y_label=FMT['sit_probability'])
        return cls(plot=fig_perc, tab=tab_perc, diff=tab_diff)


class AttributeDiff(Profile):
    """Container for all displays of group differences in ONE Attribute-by-Situation effect
    """
    @classmethod
    def display(cls, xi, emm, a_effect):
        """Create displays for a single attribute and requested situation effects
        :param xi: list of 2D arrays of parameter-vector samples
            len(xi) == len(emm.groups)
        :param a_effect: tuple (attr_key, sit_keys), where
            sit_keys is a tuple of one or more key(s) selected from emf.situation_dtypes.keys()
        :param emm: ema_model.EmaModel object
        :return: single cls instance
        """
        (a, sit_keys) = a_effect
        if FMT['grade_thresholds']:
            tau = np.array([emm.base.attribute_tau(xi_g, a)
                     for xi_g in xi])
            # tau[g, s, :] = s-th sample of threshold array for g-th group
            tau = tau.reshape((-1, tau.shape[-1]))
            # tau[gs, :] = gs-th sample across all groups
            tau = np.median(tau, axis=0)
            # tau[l] = l-th median rating threshold for attribute a
        else:
            tau = None
        # --------------------------------------- percentile table
        group_head = emm.base.emf.group_head()
        group_cat = list(emm.groups.keys())
        theta_groups = {g: emm.base.attribute_theta_df(xi_g, a, groupby=sit_keys)
                        for (g, xi_g) in zip(group_cat, xi)}
        theta_ds = pd.concat(theta_groups, axis=0, names=list(group_head))
        quantiles = np.array(FMT['percentiles']) / 100.
        theta_q = theta_ds.groupby(level=list(sit_keys) + list(group_head),
                                   sort=False, group_keys=True).quantile(quantiles,
                                                                         numeric_only=True)
        tab_perc = fmt.tab_percentiles(theta_q, file_label=a)
        fig_perc = fmt.fig_percentiles(tab_perc, y_label=a + ' (' + str(FMT['scale_unit']) + ')', file_label=a,
                                       cat_limits=tau)
        # ---------------------------------------- attribute differences between groups
        # NOTE: comparing all situation-categories, in all requested sc dimensions
        d_pd = cred_pd.cred_group_diff(theta_groups,
                                       group_axis=group_head,
                                       case_axis=sit_keys,
                                       p_lim=FMT['credibility_limit'])
        tab_diff = fmt.tab_credible_diff(d_pd, diff_head=group_head,
                                         cred_head=FMT['credibility'],
                                         case_head=sit_keys,
                                         y_label=a, file_label=a)
        return cls(plot=fig_perc, tab=tab_perc, diff=tab_diff)


# ---------------------------------- Help functions:

# def _entropy_quantiles(u):  # *** Experiment 2023-06-xx: No useful new results ************
#     """Mean of situation probability-mass vectors,
#     and ranges of situation probabilities in separate entropy regions,
#     with low entropy (more peaks) and high entropy (flatter distribution)
#     :param u: pd.Series instance with MultiIndex (sample, *sit_keys)
#         values for sit_keys[0].categories are conditional situation probabilities, given sit_keys[1:]
#     :return: tuple (u_mean, u_q) where
#         u_mean is a pd.Series or DataFrame with Index sit_keys[0].
#         u_q is a pd.Series or DataFrame with MultiIndex (quantile, sit_keys[0]).
#         If more than one situation dimension, i.e., len(sit_keys) > 1,
#         one column for each category in dimension(s) sit_keys[1:], i.e.,
#         one column for each situation sub-category on which the
#         probability-mass distribution in sit_keys[0] may depend.
#
#         Percentile values come in pairs, such that the corresponding
#         situation value is the maximum or minimum marginal situation probability
#         within the entropy range defined by the percentile pair.
#     """
#     def entropy(s):
#         """Entropy of input series
#         :param s: pd.Series with probability-mass values
#             sum(s) == 1.
#         :return: scalar entropy in nats units
#         """
#         return - np.dot(s, np.log(s + np.finfo(float).tiny))
#
#     def entropy_range(s, hp):
#         """Range of prob values within given entropy range
#         :param s: pd.Series with samples of prob.mass vectors,
#             with MultiIndex (sample, sit_dim)
#         :param hp: sequence with (min, max) entropy percentiles
#         :return: pd.Series with MultiIndex (perc, sit_dim)
#             showing (min, max) situation probabilities
#         """
#         ind_range = (np.array(hp) * len(s.index.levels[0]) / 100.).astype(int)
#         h_index = s.groupby(level=[0]).aggregate(entropy).sort_values().index
#         # = index labels sorting s by increasing entropy
#         h_index = h_index.array[ind_range[0]:ind_range[1]]
#         s = s.loc[h_index]
#         s_range = pd.DataFrame([s.groupby(level=[1]).min(),
#                                 s.groupby(level=[1]).max()],
#                                index=hp, columns=s.index.levels[1])
#         return s_range
#     # --------------------------------------------
#     entropy_perc = np.array([(5., 15.), (80., 100.)])
#     q_index = np.rint(np.array(FMT['percentiles']) * len(u.index.levels[0]) / 100.).astype(int)
#     # = integer rank indices where entropy quantiles are stored
#     # new_index = pd.MultiIndex.from_product([FMT['percentiles'], u.index.levels[1]],
#     #                                        names=['prob_key', u.index.names[1]])
#
#     new_index = pd.MultiIndex.from_product([entropy_perc.flat, u.index.levels[1]],
#                                            names=['prob_key', u.index.names[1]])
#     sit_keys = u.index.names[1:]
#     if len(sit_keys) == 1:
#         u = pd.DataFrame(u)
#     else:
#         u = u.unstack(sit_keys[1:])
#
#     u_mean = u.groupby(level=[1]).mean()
#
#     u_q = {u_key: pd.concat([entropy_range(u_val, hp)
#                              for hp in entropy_perc], axis=0).stack()
#            for (u_key, u_val) in u.items()}
#     u_q = pd.DataFrame(u_q)
#     u_q.index.set_names(['prob_key', u.index.names[1]], inplace=True)
#     if len(sit_keys) == 1:
#         u_q = u_q[0]
#     else:
#         u_q.columns.set_names(u.columns.names, inplace=True)
#     return u_mean, u_q


# def _series_quantile_fix(ds, sit_keys):  # *** Not needed after bug fix in Pandas >= 2.1
#     """Work-around for possible Pandas bug in groupby with sort=False
#     :param ds: pandas.Series instance with Multi-index [_sample, *sit_keys]
#     :param sit_keys: tuple with one or more index levels in ds
#     :return: series with Multi-Index levels [*sit_keys, quantiles]
#     """
#     quantiles = np.array(FMT['percentiles']) / 100.
#     if len(sit_keys) > 1:
#         q = ds.groupby(level=sit_keys,
#                        sort=False, group_keys=True).quantile(quantiles)
#     # *** -> SORTED index.levels for sit_key if only one dimension. Pandas v 2.0.0, 2.0.1
#     # *** -> OK UN-sorted index.levels, if sit_keys is more than one level ***
#     else:  # *** work-around for Pandas bugg ***
#         q = pd.concat({s: q.quantile(quantiles)
#                        for (s, q) in ds.groupby(level=sit_keys, sort=False)},
#                       names=list(sit_keys))
#     return q


def fig_comments():
    """Generate figure explanations.
    :return: comment string
    """
    p_min = np.amin(FMT['percentiles'])
    p_max = np.amax(FMT['percentiles'])
    c = f"""Figure Explanations:
    
Figure files with names like
someSituationName_xxx.pdf, someAttributeName_xxx.pdf or xxx.jpg, or similar,
display user-requested percentiles (markers) and credible intervals (vertical bars) 
The vertical bars show the range between {p_min:.1f}- and {p_max:.1f}- percentiles.

Median ordinal grade thresholds for perceptual Attributes, if requested,
are indicated by thin lines extending horizontally across the graph.

The displayed ranges include all uncertainty
caused both by real inter-individual perceptual differences
and by the limited number of responses by each individual.
"""
    if FMT['grade_counts'] is not None and len(FMT['grade_counts']) > 0:
        c += f"""
Attribute grade-counts are shown as bar plots for RECORDED EMA data.
A vertical line on top of each bar shows the range 
between {p_min:.1f}- and {p_max:.1f}- percentiles of corresponding MODEL-PREDICTED grade-counts.
"""
    return c


def table_comments():
    c = """Table Explanations:

*** Tables of Percentiles:
Files with names like someSituationName_xxx.tex, someAttributeName_xxx.tex or *.txt
show numerical versions of the information in corresponding percentile plots.
Percentiles, credible ranges, and marginal probabilities for negative and positive values are shown.

*** Tables of Credible Differences:
Files with names like someAttribute-diff_xxx.tex or *.txt 
show a list of Attribute (in Situation) pairs
which are ALL JOINTLY credibly different
with the tabulated credibility.
The credibility value in each row is the JOINT probability
for the pairs in the same row and all rows above it.
Thus, the joint probability values already account for multiple comparisons,
so no further adjustments are needed.
"""
    return c
