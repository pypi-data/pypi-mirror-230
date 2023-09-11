"""This module defines classes for a Bayesian probabilistic model of EMA data,
for ONE group of respondents representing ONE population.

*** Class Overview:

EmaGroupModel: Container for individual response-probability models,
    implemented by an ema_respondent.EmaRespondentModel instance for each participant
    in ONE group of test participants, assumed recruited from ONE population.
    Also contains a PopulationModel instance representing the population
    from which the participants were recruited.

PopulationModel: Defines a Gaussian Mixture Model (GMM)
    for the parameter distribution in ONE population,
    from which participants in ONE group were recruited.
    Part of EmaGroupModel, used as prior for all participants in the group.

PredictivePopulationModel: marginal distribution of parameters
    in ONE population represented by ONE EmaGroupModel.
    Specifies a mixture of Student-t distributions,
    used for result displays.

*** Version History:
* Version 1.0.0:
2023-05-17, EmaGroupModel.initialize(...,n_participants_per_comp,...) to set initial number of GMM components
2023-05-15, logger.info participant GMM weights after pruning

* Version 0.9.3:
2022-07-27, changed 'subject' -> 'participant' or 'respondent'

* Version 0.8.3:
2022-03-07, changed class name GroupModel -> EmaGroupModel
2022-03-07, changed class name ProfileMixtureModel -> PredictivePopulationModel
2022-03-07, separate class for GMM: EmaGroupModel.pop_gmm = a PopulationModel instance

* Version 0.8.2:
2022-03-03, allow multi-processing Pool in EmaGroupModel.adapt, parallel across subjects
2022-03-02, test prepare to allow multiprocesing Pool.imap
            allow multi-processing Pool in EmaGroupModel.adapt, parallel across subjects

* Version 0.8.1
2022-02-26, complete separate GMM for each group, GMM components -> EmaGroupModel property comp
"""
# *** test multiprocessing start method fork? Does not work in windows ! *********
# *** Future: try using shared_memory or Ray to reduce multiprocessing overhead?
import copy
import logging
import os
from multiprocessing.pool import Pool

import numpy as np
from scipy.special import logsumexp, softmax
# import pandas as pd

from EmaCalc.dirichlet import DirichletVector
from EmaCalc.dirichlet import JEFFREYS_CONC
from EmaCalc.ema_respondent import EmaRespondentModel

MixtureWeight = DirichletVector

# -------------------------------------------------------------------
__ModelVersion__ = "2022-03-08"

PRIOR_MIXTURE_CONC = JEFFREYS_CONC
# = prior conc for population mixture weights.

N_SAMPLES = 1000
# = default number of parameter samples in PredictivePopulationModel.rvs() calculation

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST

usePool = True
# usePool = False # for TEST
# multi-processing speeds up the learning, but the Pool causes some overhead,
# so the time reduction is only about a factor 2 with 4 CPU cores.


# -------------------------------------------------------------------
class EmaGroupModel:
    """Container for EmaRespondentModel instances for all test participants
    in ONE group of respondents,
    and a PopulationModel instance defining
    a Gaussian Mixture Model (GMM) for the parameter distribution in
    the population from which participants were recruited.
    The GMM is prior for the parameter distribution in all EmaRespondentModel instances.
    """
    def __init__(self, base, participants, pop_gmm):
        """
        :param base: single common EmaParamBase object, used by all model parts
        :param participants: dict with (participant_id, EmaRespondentModel) elements
        :param pop_gmm: a PopulationModel instance representing a Gaussian Mixture Model (GMM)
            for the parameter distribution in the population from which participants were recruited.
        """
        self.base = base
        self.participants = participants
        # *** might be just a list, not dict, as each participant has ID as property ***
        self.pop_gmm = pop_gmm
        for s in self.participants.values():
            s.prior = self.pop_gmm

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                f'\n\tparticipants= {len(self.participants)} individuals,' +
                f'\n\tpop_gmm={repr(self.pop_gmm)})'
                )

    @classmethod
    def initialize(cls, n_participants_per_comp, base, group_data, seed_seq, rng):
        """Crude initial group model given group EMA data
        :param n_participants_per_comp: scalar integer = desired number of participants per GMM component
        :param base: single common EmaParamBase object, used by all model parts
        :param group_data: a dict with elements (s_id, s_ema), where
            s_id = a participant key,
            s_ema = a Pandas.DataFrame with EMA records from an ema_data.EmaDataSet object.
        :param seed_seq: SeedSequence object to spawn children for participants of this group
        :param rng: random Generator for this group, used by self.pop_gmm
        :return: a cls instance crudely initialized
        """
        participant_rng_list = [np.random.default_rng(s)
                                for s in seed_seq.spawn(len(group_data))]
        s_models = {s_id: EmaRespondentModel.initialize(base, s_ema, s_rng, id=s_id)
                    for ((s_id, s_ema), s_rng) in zip(group_data.items(),
                                                      participant_rng_list)}
        n_participants = len(s_models)
        # if max_n_comp is None:
        #     max_n_comp = n_participants // 2
        # else:
        #     max_n_comp = min(n_participants // 2, max_n_comp)
        n_comp = max(1, n_participants // n_participants_per_comp)
        pop_gmm = PopulationModel.initialize(n_comp, s_models, base, rng)
        return cls(base, s_models, pop_gmm)

    def adapt(self, g_name):
        """One VI adaptation step for all model parameters
        :param g_name: group id label for logger output
        :return: ll = scalar VI lower bound to data log-likelihood,
            incl. negative contributions for parameter KLdiv re priors

        NOTE: All contributions to VI log-likelihood
        are calculated AFTER all updates of factorized parameter distributions
        because all must use the SAME parameter distribution
        """
        ll_pop_gmm = self.pop_gmm.adapt(g_name, self.participants)
        # = -KLdiv{ q(mix_weight) || prior.mix_weight}
        #   sum_m -KLdiv(current q(mu_m, Lambda_m) || prior(mu_m, Lambda_m))

        # *** allow multiprocessing across participants in parallel
        if usePool:
            n_pool = _pool_size(len(self.participants))
            ch_size = len(self.participants) // n_pool
            # ****** check time ! ********************
            if n_pool * ch_size < len(self.participants):
                ch_size += 1
            logger.debug(f'adapt with Pool: n_pool= {n_pool}, ch_size= {ch_size}')
            with Pool(n_pool) as p:
                self.participants = dict(p.imap(_adapt_respondent, self.participants.items(),
                                                chunksize=ch_size))
                # ******* send self.pop_gmm as argument to _adapt_participant ??? ******
                # if so, MUST delete the copy in sub-process! Maybe pickling takes longer time? ***
                for s in self.participants.values():
                    s.prior = self.pop_gmm
                    # MUST restore link; sub-processed object links to a copy of self.pop_gmm
        else:
            logger.debug(f'adapt without Pool multiprocessing')
            self.participants = dict(map(_adapt_respondent, self.participants.items()))
        ll_participants = sum(s_model.ll for s_model in self.participants.values())
        # = sum <ln p(data | xi)> + <ln prior p(xi | comp)> - <ln q(xi)>
        #           - KLdiv(q(zeta | xi) || p(zeta | self.mix_weight)
        #  All ll contributions now calculated using the current updated q() distributions
        logger.debug(f'Group {repr(g_name)}: '
                     + f'\n\tll_pop_gmm = {ll_pop_gmm:.3f}'
                     + f'\n\tparticipant sum ll_xi= {ll_participants:.3f}')
        return ll_pop_gmm + ll_participants

    def prune(self, g_name, min_weight=JEFFREYS_CONC):
        """Prune model to keep only active mixture components
        :param g_name: group label for logger output
        :param min_weight: scalar, smallest accepted value for sum individual weight
        :return: None
        Result: all model components pruned consistently
        """
        w_sum = np.sum([np.mean(self.pop_gmm.mean_conditional_zeta(s.xi), axis=-1)
                        for s in self.participants.values()],
                       axis=0, keepdims=False)
        # = sum of mean individual mixture weights, given xi
        logger.debug(f'{repr(g_name)}: Before pruning: w_sum = '
                     + np.array2string(w_sum, precision=2, suppress_small=True))
        if np.any(np.logical_and(min_weight < w_sum, w_sum <= 2.5)):
            logger.warning(f'Group {repr(g_name)}: *** Some GMM component(s) has TWO or LESS participants. '
                           'Variance estimates may be unreliable. ***')
        keep = min_weight < w_sum
        n_keep = np.sum(keep)
        n_total = len(keep)
        self.pop_gmm.prune(keep)
        # --- make logger message:
        msg = f'Group {repr(g_name)}:\t'
        if n_keep < n_total:
            msg += f'Model pruned to {n_keep} active mixture component(s) out of initially {n_total}'
        else:
            msg += f'All initial {n_total} mixture component(s) still active.'
        if len(self.pop_gmm.comp) > 1:
            msg += (f'\nParticipant GMM weights =\n\t'
                    + '\n\t'.join((str(s_name) + ':\t'
                                   + np.array_str(np.mean(self.pop_gmm.mean_conditional_zeta(s_model.xi),
                                                          axis=-1),
                                                  precision=2,
                                                  suppress_small=True)
                                   for (s_name, s_model) in self.participants.items())))
        logger.info(msg)

    # ---------------------------- make final results for display:
    def predictive_population_ind(self):
        """Predictive probability-distribution for a Random Individual
        in the population represented by self
        :return: a PredictivePopulationModel object
        """
        return self.pop_gmm.predictive_population_ind()

    def predictive_population_mean(self):
        """Predictive probability-distribution for MEAN parameter vector
        in the population represented by self
        :return: a PredictivePopulationModel object
        """
        return self.pop_gmm.predictive_population_mean()

# ------------------------------------- display functions
    def attribute_grade_count(self, a, groupby=None):
        """Collect table of ordinal grade counts for ONE attribute,
        summed across all participants, optionally subdivided by situation.
        :param a: selected attribute key
        :param groupby: (optional) single situation dimension or sequence of such keys
            for which separate attribute-counts are calculated.
            Counts are summed across any OTHER situation dimensions.
        :return: a pd.DataFrame object with all grade counts,
            with one row for each (*groupby) combination
            and one column for each grade category
        """
        return sum((s_model.attribute_grade_count(a, groupby=groupby)
                    for s_model in self.participants.values()))

    def rvs_grade_count(self, a, groupby=None):
        """Collect table of predicted grade counts for ONE attribute,
        summed across all participants, optionally subdivided by situation.
        :param a: selected attribute key
        :param groupby: (optional) single situation dimension or sequence of such keys
            for which separate attribute-counts are calculated.
            Counts are summed across any OTHER situation dimensions.
        :return: a pd.DataFrame object with all grade counts,
            with one row for each (sample, *groupby) combination
            and one column for each grade category
        """

        return sum((s_model.rvs_grade_count(a, groupby=groupby)
                    for s_model in self.participants.values()))


# -------------------------------------------------------------------
class PopulationModel:
    """A Gaussian Mixture Model (GMM) representing the parameter distribution in
    a population of participants from which participants in ONE group are recruited.
    The GMM is Bayesian, implemented by random-variable properties
    mix_weight = a MixWeight object = Dirichlet-distributed mixture weights,
    comp = a list of gauss_gamma.GaussianRV objects.
    """
    def __init__(self, base, mix_weight, comp, rng):
        """
        :param base: single common EmaParamBase object, used by all model parts
        :param mix_weight: a single MixtureWeight(DirichletVector) instance,
            with one element for each element of base.comp
        :param comp: list of GaussianRV instances,
            each representing ONE mixture component
            for parameter vector xi, in the (sub-)population represented by self
        :param rng: random Generator instance
        """
        self.base = base
        self.mix_weight = mix_weight
        self.comp = comp
        self.rng = rng

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                f'\n\tmix_weight={repr(self.mix_weight)},'
                f'\n\tcomp= {len(self.comp)} mixture components)'
                )

    @classmethod
    def initialize(cls, n_comp, participants, base, rng):
        """Crude initial group model given group EMA data
        :param n_comp: integer number of GMM components
        :param participants: list with EmaRespondentModel instances for group participants,
            only crudely initialized
        :param base: single common EmaParamBase object, used by all model parts
        :param rng: random Generator for this group
        :return: a cls instance crudely initialized
        """
        mix_weight = MixtureWeight(alpha=np.ones(n_comp) * PRIOR_MIXTURE_CONC,
                                   rng=rng)
        # -> equal mean weights for all mixture components
        comp = [copy.deepcopy(base.comp_prior)
                for _ in range(n_comp)]
        self = cls(base, mix_weight, comp, rng)
        self._init_comp(participants)
        # Mixture weights will be adapted later in the general VI procedure.
        return self

    def _init_comp(self, participants):
        """Initialize Gaussian mixture components to make them distinctly separated,
        using only initialized values for all participant.xi.
        This is a necessary starting point for VI learning.
        :param participants: dict with (participant_id, EmaRespondentModel-object) elements
            crudely initialized
        :return: None

        Method: pull self.comp elements apart by random method like k-means++
        that tends to maximize separation between mixture components.
        """
        def distance(x, c):
            """Square-distance from given samples to ONE mixture component,
            as estimated by component logpdf.
            :param x: 2D array of sample row vectors that might be drawn from c
            :param c: ONE mixture component in self.base.comp
            :return: d = 1D array with non-negative distance measures
                d[n] = distance from x[n] to c >= 0.
                len(d) == x.shape[0]
            """
            d = - c.mean_logpdf(x)
            return d - np.amin(d)

        def weight_by_dist(d):
            """Crude weight vector estimated from given distance measures
            :param d: 1D array with non-negative distances
            :return: w = 1D array with weights,
                with ONE large element randomly chosen with probability prop.to d2,
                and all other elements small and equal.

                Purpose: same as in kmeans++:
                    Tends to push current comp element FAR away
                    from all other comp elements already initialized.
                w.shape == d.shape
            """
            w = np.full_like(d, 1. / len(d))
            # ALL samples jointly contribute with weight equiv to ONE sample
            i = self.rng.choice(len(d), p=d / sum(d))
            w[i] = len(d) / len(self.comp)
            # total weight of all samples divided uniformly across components
            # placed on the single selected i-th sample point
            return w

        # --------------------------------------------------------
        xi = np.array([np.mean(s_model.xi, axis=0)
                       for s_model in participants.values()])
        xi2 = np.array([np.mean(s_model.xi**2, axis=0)
                        for s_model in participants.values()])
        xi_d = np.full(len(xi), np.finfo(float).max / len(xi) / 2)
        # = very large numbers that can still be normalized to sum == 1.
        for c_i in self.comp:
            c_i.adapt(xi, xi2, w=weight_by_dist(xi_d), prior=self.base.comp_prior)
            xi_d = np.minimum(xi_d, distance(xi, c_i))
            # xi_d[n] = MIN distance from xi[n] to ALL already initialized components

    def adapt(self, g_name, participants):
        """One VI adaptation step for all model parameters
        :param g_name: group id label for logger output
        :param participants: dict with current (participant_id, EmaRespondentModel) elements
        :return: ll = scalar VI lower bound to data log-likelihood,
            incl. negative contributions for parameter KLdiv re priors

        NOTE: All contributions to VI log-likelihood
        are calculated AFTER all updates of factorized parameter distributions
        because all must use the SAME parameter distribution
        """
        ll_weights = self._adapt_mix_weight(participants)
        # = -KLdiv{ q(self.mix_weight) || prior.mix_weight}
        ll_comp = self._adapt_comp(g_name, participants)
        # ll_comp[c] = -KLdiv(current q(mu_c, Lambda_c) || prior(mu_c, Lambda_c)), for
        # q = new adapted comp, p = prior_comp model, for c-th mixture component
        # Leijon doc eq:CalcLL
        sum_ll_comp = sum(ll_comp)
        logger.debug(f'{repr(g_name)}.pop_gmm: '
                     + f'\n\tll_weights= {ll_weights:.4f} '
                     + f'\n\tmix_weight.alpha= '
                     + np.array2string(self.mix_weight.alpha,
                                       precision=2,
                                       suppress_small=True)
                     + f'\n\tcomp: -KLdiv= {sum_ll_comp: .3f} = sum'
                     + np.array_str(np.array(ll_comp),
                                    precision=2,
                                    suppress_small=True))
        return ll_weights + sum_ll_comp

    def _adapt_comp(self, g_name, participants):
        """One VI update for all GMM components in self.comp
        :param g_name: group id label for logger output
        :param participants: dict with current (participant_id, EmaRespondentModel) elements
        :return: ll = sum_c (-KLdiv re prior) across self.base.comp[c]
        """
        (m_zeta, m_zeta_xi, m_zeta_xi2) = ([], [], [])
        # = accumulators for <zeta>, <zeta * xi>, <zeta * xi**2>
        for s in participants.values():
            zeta = self.mean_conditional_zeta(s.xi)
            # zeta[c, ...] = E{zeta_c | s.xi[...]}; zeta_c= binary component indicator
            # for ...-th sample of participant s to be generated by c-th mixture component.
            n_xi = s.xi.shape[0]  # = zeta.shape[1]
            m_zeta.append(np.mean(zeta, axis=-1))
            m_zeta_xi.append(np.dot(zeta, s.xi) / n_xi)
            m_zeta_xi2.append(np.dot(zeta, s.xi**2) / n_xi)
        # m_zeta[s][c] = < zeta_cs >_s.xi
        # m_zeta_xi[s][c, :] = < zeta_cs * s.xi >_s.xi
        # m_zeta_xi2[s][c, :] = < zeta_cs * s.xi**2 >_s.xi
        ll = [c.adapt(xi_c, xi2_c, w_c, prior=self.base.comp_prior)
              for (c, xi_c, xi2_c, w_c) in zip(self.comp,
                                               np.array(m_zeta_xi).transpose((1, 0, 2)),
                                               np.array(m_zeta_xi2).transpose((1, 0, 2)),
                                               np.array(m_zeta).T)]
        # = list of -KLdiv(self.comp[c] || self.base.comp_prior)
        return ll

    def _adapt_mix_weight(self, participants):
        """One update step of properties self.mix_weight,
        :return: ll = - KLdiv(self.mix_weight || prior.mix_weight), after updated mix_weight
        """
        self.mix_weight.alpha = (np.sum([np.mean(self.mean_conditional_zeta(s.xi),
                                                 axis=1)
                                         for s in participants.values()],
                                        axis=0)
                                 + PRIOR_MIXTURE_CONC)
        # = Leijon doc eq:PosteriorV
        prior_alpha = PRIOR_MIXTURE_CONC * np.ones(len(self.comp))
        # *** might store a complete prior GMM in self.base,
        # instead of generating the DirichletVector here ?
        return - self.mix_weight.relative_entropy(DirichletVector(alpha=prior_alpha))

    def prune(self, keep):
        """Prune model to keep only active mixture components
        :param keep: boolean array indicating mixture components to keep
        :return: None
        Result: all model components pruned consistently
        """
        self.mix_weight.alpha = self.mix_weight.alpha[keep]
        del_index = list(np.arange(len(keep), dtype=int)[np.logical_not(keep)])
        del_index.reverse()
        # Must delete in reverse index order to avoid IndexError
        for i in del_index:
            del self.comp[i]

    # ----------------- methods used as prior for EmaRespondentModel instances:
    def logpdf(self, xi):
        """Mean log pdf of any candidate participant parameter array,
        given current GMM defined by self.mix_weight and self.comp
        averaged across self.comp parameters and self.mix_weight
        :param xi: array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: lp = array with
            lp[...] = E_self{ln p(xi[..., :] | self)}
            lp.shape == xi.shape[:-1]

        Method: Leijon doc eq:LogProbXi, prior part
        """
        return logsumexp(self.log_responsibility(xi), axis=0)

    def d_logpdf(self, xi):
        """gradient of self.logpdf(xi) w.r.t. xi
        :param xi: 2D array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: dlp = array with
            dlp[..., j] = d log p(xi[..., :] | self) / d xi[..., j]
            lp.shape == xi.shape
        """
        return np.sum(softmax(self.log_responsibility(xi)[..., None],
                              axis=0) * self.d_log_responsibility(xi),
                      axis=0)

    def mean_conditional_zeta(self, xi):
        """Expected value of mixture-component indicator zeta,
         given any candidate participant parameter vector(s)
        :param xi: 1D or 2D array with
            xi[..., :] = ...-th parameter sample vector
         :return: w = array, normalized for sum(w) == 1.
             w[c, ...] = P{xi[..., :] generated by c-th mixture component}
             w.shape == (len(self.comp), *xi.shape[:-1])
        """
        return softmax(self.log_responsibility(xi), axis=0)

    def mean_marginal_zeta(self, xi):  # *** needed ?
        """Marginal expected value of mixture-component indicator zeta,
         given any candidate participant parameter vector(s),
         averaged across all xi samples
        :param xi: 2D array with
            xi[s, :] = s-th parameter sample vector
         :return: w = 1D array, normalized for sum(w) == 1.
             w[c] = mean_s(P{xi[s, :] generated by c-th mixture component})
             w.shape == (len(self.comp),)
        """
        return np.mean(self.mean_conditional_zeta(xi), axis=1)

    def log_responsibility(self, xi):
        """Expected log pdf for any candidate participant parameters,
        for each comp in current GMM represented by self.mix_weight and self.comp
        :param xi: 2D array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: lr = array with
            lr[c, ...] = E{ log P[ xi[..., :] | self.comp[c] }
            lr.shape == (len(self.comp), *xi.shape[:-1])

        Method: Leijon doc l_c(xi) from eq:LogProbXiZeta
        """
        return np.array([c.mean_logpdf(xi) + lv_c
                         for (c, lv_c) in zip(self.comp,
                                              self.mix_weight.mean_log)
                         ])

    def d_log_responsibility(self, xi):
        """Gradient of self.log_responsibility(xi) w.r.t. xi
        :param xi: 2D array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: dlr = array with
            dlr[c, ..., j] = d self.log_responsibility(xi)[c, ...] / d xi[..., j]
            dlr.shape == (len(self.comp), *xi.shape)
        """
        return np.array([c.grad_mean_logpdf(xi)
                         for c in self.comp])

    # ---------------------------- final results for display:
    def predictive_population_ind(self):
        """Predictive probability-distribution for Random Individual
        population represented by self
        :return: a PredictivePopulationModel object

        Method: report eq:PredictiveSubPopulation
        """
        comp = [c_m.predictive(rng=self.rng) for c_m in self.comp]
        return PredictivePopulationModel(self.base, comp, self.mix_weight.mean, self.rng)

    def predictive_population_mean(self):
        """Predictive probability-distribution for MEAN parameter vector
        in population represented by self
        :return: a PredictivePopulationModel object

        Method: report eq:PredictivePopulation
        """
        comp = [c_m.mean.predictive(rng=self.rng) for c_m in self.comp]
        return PredictivePopulationModel(self.base, comp, self.mix_weight.mean, self.rng)


# ------------------------------------------------------------------
class PredictivePopulationModel:
    """Help class defining a non-Bayesian predictive mixture model
    for parameter distribution in a population,
    derived from existing trained model components
    """
    def __init__(self, base, comp, w, rng):
        """
        :param base: ref to common EmaParamBase object
        :param comp: list of predictive mixture component models
            NOT same as original base.comp
        :param w: 1D array with mixture weight values
        :param rng: random Generator instance
        """
        self.base = base
        self.comp = comp
        self.w = w
        self.rng = rng

    @property
    def mean(self):
        """Mean of parameter vector, given population mixture,
        averaged across mixture components
        and across posterior distribution of component concentration params.
        :return: 1D array
        """
        return np.dot(self.w, [c_m.mean for c_m in self.comp])

    def rvs(self, size=N_SAMPLES):
        """Generate random probability-profile samples from self
        :param size: integer number of sample vectors
        :return: xi = 2D array of parameter-vector samples
            xi[s, :] = s-th sample parameter vector,
                with parameter sub-types as specified by self.base
        """
        n_comp = len(self.comp)
        comp_ind = self.rng.choice(n_comp, p=self.w, size=size)
        # = array of random comp indices
        n_comp_samples = [np.sum(comp_ind == i) for i in range(n_comp)]
        # = n samples to generate from each mixture component
        xi = np.concatenate([c.rvs(size=n_c)
                             for (n_c, c) in zip(n_comp_samples, self.comp)],
                            axis=0)
        self.rng.shuffle(xi, axis=0)
        return xi


# ------------------------------ help functions for Pool multi-tasking:
def _pool_size(n):
    """Estimate number of Pool sub-processes
    :param n: total number of independent jobs to share between processes
    :return: n_processes
    """
    # NOTE: cpu_count() returns n of LOGICAL cpu cores.
    return min(os.cpu_count(), n)


def _adapt_respondent(s_item):
    """dispatch function call to given object.adapt(...)
    for use by multi-processing Pool.imap() or non-pool map()
    :param s_item: tuple(s_id, s_model), where
        s_id is object id, and s_model has an adapt method
        Here, s_model is always an ema_respondent.EmaRespondentModel instance
    :return: tuple(s_id, s_model_adapted)
    """
    (s_id, s_model) = s_item
    return s_id, s_model.adapt(s_id)
