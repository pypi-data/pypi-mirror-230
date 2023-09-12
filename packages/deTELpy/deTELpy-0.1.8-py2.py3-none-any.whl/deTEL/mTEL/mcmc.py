import io
import time
import sys
from contextlib import redirect_stderr

import matplotlib.pyplot as plt
from tqdm import tqdm
from dataclasses import dataclass, field

import multiprocessing as mp
import numpy as np

from . import mtem
from . import data


# TODO change mtem to object that can be evaluated at a given parameter set in order to avoid passing model constants
#  and data through the mcmc. This also allows to keep things cleaner in general

@dataclass
class MCMCstate:
    alpha: np.array = field(default_factory=np.array)  # position penalty
    beta: np.array = field(default_factory=np.array)  # nucleotide mismatching
    log_likelihood: float = 0.0


@dataclass
class MCMC:
    model: mtem.MTEM

    c_alpha: np.array = field(init=False)  # position penalty
    c_beta: np.array = field(init=False)  # nucleotide mismatching

    p_alpha: np.array = field(init=False)  # position penalty
    p_beta: np.array = field(init=False)  # nucleotide mismatching

    alpha_acceptance_counter: int = 0
    beta_acceptance_counter: int = 0
    adaptive_width: int = 100
    a_proposal_width: float = 0.01
    b_proposal_width: float = 0.01

    trace: list = field(default_factory=list)

    current_log_likelihood: float = 0.0
    proposed_log_likelihood: float = 0.0

    POSITION_PENALTY = 'alpha'
    WOBBLE_PENALTY = 'beta'

    # Move the likelihood into a data class that 'knows' what type of data it is?
    # Probably better to move it into the model mtem class.
    # This would allow for a generalization of the MCMC. Necessary and worth the time?
    @staticmethod
    def log_likelihood(x, p):

        """
        :param x: data.frame of substitutions from codon (row) to AA (column)
        :param p: data.frame of estimated substitutions probabilities from codon (row) to AA (column)
        :return: log(likelihood) of x
        """
        log_p = np.log(np.array(p))
        ll = 0.0
        for dataset in x:
            d = np.array(dataset.substitutions)
            ll += np.sum(d * log_p)

        return ll

    @staticmethod
    def propose(x, sd):
        """
        :param x: vector of current position penalties
        :param sd: vector of proposal width
        :return: vector of proposed position penalties
        """
        y = np.random.normal(x, sd)
        return y

    def update_alpha(self):
        self.c_alpha = self.p_alpha
        self.current_log_likelihood = self.proposed_log_likelihood
        self.alpha_acceptance_counter += 1

    def update_beta(self):
        self.c_beta = self.p_beta
        self.current_log_likelihood = self.proposed_log_likelihood
        self.beta_acceptance_counter += 1

    def update_proposal_width(self):
        if self.alpha_acceptance_counter / self.adaptive_width < 0.25:
            self.a_proposal_width *= 0.8
        if self.alpha_acceptance_counter / self.adaptive_width > 0.35:
            self.a_proposal_width *= 1.2
        if self.beta_acceptance_counter / self.adaptive_width < 0.25:
            self.b_proposal_width *= 0.8
        if self.beta_acceptance_counter / self.adaptive_width > 0.35:
            self.b_proposal_width *= 1.2

        self.alpha_acceptance_counter = 0
        self.beta_acceptance_counter = 0

    def accept_parameter_set(self, log_parameter=False):
        """
        :return: boolean indicating acceptance/rejection of current state
        """

        ratio = (self.proposed_log_likelihood - self.current_log_likelihood)
        if log_parameter:
            ratio = ratio - np.sum(self.c_alpha - self.p_alpha)

        alpha = -np.random.exponential()

        return ratio > alpha

    def position_penalty_trace(self):
        nsamples = len(self.trace)
        position_trace = np.zeros(shape=(nsamples, self.trace[0].alpha.shape[0]))
        for i in range(nsamples):
            position_trace[i, :] = self.trace[i].alpha

        return np.exp(position_trace)

    def wobble_penalty_trace(self):
        nsamples = len(self.trace)
        wobble_trace = np.zeros(shape=(nsamples, self.trace[0].beta.shape[0]))
        for i in range(nsamples):
            wobble_trace[i, :] = self.trace[i].beta

        return wobble_trace

    def position_penalty_posterior(self, samples):
        nsamples = len(self.trace)
        posterior = np.zeros(shape=(samples, self.trace[0].alpha.shape[0]))
        for i, s in enumerate(range(nsamples - samples, nsamples)):
            posterior[i, :] = self.trace[s].alpha

        return np.exp(posterior)

    def wobble_penalty_posterior(self, samples):
        nsamples = len(self.trace)
        posterior = np.zeros(shape=(samples, self.trace[0].beta.shape[0]))
        for i, s in enumerate(range(nsamples - samples, nsamples)):
            posterior[i, :] = self.trace[s].beta

        return posterior

    def likelihood_trace(self):
        t_len = len(self.trace)
        ll_trace = [0] * t_len
        for t in range(t_len):
            ll_trace[t] = self.trace[t].log_likelihood

        return ll_trace

    def plot_posterior(self, which, samples):
        if which == self.POSITION_PENALTY:
            posterior = self.position_penalty_posterior(samples=samples)
            fig, axes = plt.subplots(1, 3)
            # TODO turn into loop
            axes[0].hist(posterior[:, 0])
            axes[0].set_xlabel('First Codon Position', weight='bold')
            axes[0].set_ylabel('Frequency', weight='bold')

            axes[1].hist(posterior[:, 1])
            axes[1].set_xlabel('First Codon Position', weight='bold')
            axes[1].set_ylabel('Frequency', weight='bold')

            axes[2].hist(posterior[:, 2])
            axes[2].set_xlabel('First Codon Position', weight='bold')
            axes[2].set_ylabel('Frequency', weight='bold')

    def prepare_dataset(self, unordered_data):
        reordered_data = []
        for d in unordered_data:
            d.substitutions = d.substitutions[self.model.THREE_LETTER_AA_NO_I]
            d.substitutions = d.substitutions.reindex(self.model.CODONS_NO_STOP)
            reordered_data.append(d)

        return reordered_data

    def run(self, samples, thinning, burnin, ic_alpha, ic_beta, data):
        data = self.prepare_dataset(data)

        iterations = (samples + burnin) * thinning
        self.trace = samples * [MCMCstate]

        self.c_alpha = ic_alpha
        self.c_beta = ic_beta
        c_beta = self.model.format_wobble_penalties(self.c_beta)
        p = self.model.calculate_all_substitution_probabilities(np.exp(self.c_alpha), c_beta, combine_ile_leu=True)
        self.current_log_likelihood = self.log_likelihood(data, p)
        print('Initial log(likelihood): {}\n'.format(self.current_log_likelihood))

        f = None
        if not sys.stdin.isatty():
            f = io.StringIO()

        for i in tqdm(range(0, iterations), file=sys.stdout):
            # Accept/Reject Position penalty
            self.p_alpha = self.propose(self.c_alpha, self.a_proposal_width)
            # forgetting this line caused a bug before. move it into the model itself?
            c_beta = self.model.format_wobble_penalties(self.c_beta)
            p = self.model.calculate_all_substitution_probabilities(np.exp(self.p_alpha), c_beta, combine_ile_leu=True)
            self.proposed_log_likelihood = self.log_likelihood(data, p)
            if self.accept_parameter_set(log_parameter=True):
                self.update_alpha()

            # Accept/Reject Nucleotide Mismatch penalty
            self.p_beta = self.propose(self.c_beta, self.b_proposal_width)
            p_beta = self.model.format_wobble_penalties(self.p_beta)
            p = self.model.calculate_all_substitution_probabilities(np.exp(self.c_alpha), p_beta, combine_ile_leu=True)
            self.proposed_log_likelihood = self.log_likelihood(data, p)
            if self.accept_parameter_set(log_parameter=False):
                self.update_beta()

            # ---- UPDATE TRACE ----
            if i / thinning >= burnin:
                if i % thinning == 0:
                    self.trace[int(i / thinning) - burnin] = MCMCstate(alpha=self.c_alpha, beta=self.c_beta,
                                                                       log_likelihood=self.current_log_likelihood)

            # ---- ADAPT PROPOSAL WIDTH ----
            if i != 0 and i % self.adaptive_width == 0:
                self.update_proposal_width()

            if f and i % 12 == 0:
                print(end ='\n', flush=True)

        print('Final log(likelihood): {}\n'.format(self.current_log_likelihood))
