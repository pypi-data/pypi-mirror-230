from dataclasses import dataclass, field
from functools import partial
from numba import jit

import pandas as pd
import numpy as np


@dataclass
class MTEM:
    # CLASS VARIABLES
    anticodon_file: str
    cell_volume: float

    # fixed parameters
    trna: pd.DataFrame = field(init=False, repr=False)

    # calculated parameters
    arrival_rate: pd.DataFrame = field(init=False, repr=False)
    ar: np.array = field(init=False, repr=False)
    arrival_probabilities: pd.DataFrame = field(init=False, repr=False)
    ap: np.array = field(init=False, repr=False)
    synonymous_trna: dict = field(default_factory=dict, init=False, repr=False)
    available_trna: list = field(default_factory=list, init=False, repr=False)

    # CONSTANTS
    NON_WC_NUC_PAIRS: list = field(default_factory=lambda: ['AA', 'AC', 'AG', 'CA', 'CC', 'CT', 'TC', 'TT', 'TG', 'GA',
                                                            'GT', 'GG'], repr=False)
    WC_NUC_PAIRS: list = field(default_factory=lambda: ['AA', 'AC', 'AG', 'CA', 'CC', 'CT', 'TC', 'TT', 'TG', 'GA',
                                                        'GT', 'GG', 'AT', 'TA', 'GC', 'CG'], repr=False)
#    NON_CONST_WC_NUC_PAIRS: list = field(default_factory=lambda: ['AA', 'AC', 'AG', 'CA', 'CC', 'CT', 'TC', 'TT', 'TG',
#                                                                  'GA', 'GG', 'AT', 'TA', 'GC', 'CG'], repr=False)
    CODONS: list = field(default_factory=lambda: ["GCA", "GCC", "GCG", "GCT", "TGC", "TGT", "GAC", "GAT", "GAA",
                                                  "GAG", "TTT", "TTC", "GGT", "GGC", "GGA", "GGG", "CAT", "CAC",
                                                  "ATT", "ATC", "ATA", "AAA", "AAG", "TTA", "TTG", "CTT", "CTC",
                                                  "CTA", "CTG", "ATG", "AAT", "AAC", "CCT", "CCC", "CCA", "CCG",
                                                  "CAA", "CAG", "CGT", "CGC", "CGA", "CGG", "AGA", "AGG", "TCT",
                                                  "TCC", "TCA", "TCG", "AGT", "AGC", "ACT", "ACC", "ACA", "ACG",
                                                  "GTT", "GTC", "GTA", "GTG", "TGG", "TAT", "TAC", "TAA", "TAG",
                                                  "TGA"], repr=False)
    CODONS_NO_STOP: list = field(default_factory=lambda: ["GCA", "GCC", "GCG", "GCT", "TGC", "TGT", "GAC", "GAT", "GAA",
                                                          "GAG", "TTT", "TTC", "GGT", "GGC", "GGA", "GGG", "CAT", "CAC",
                                                          "ATT", "ATC", "ATA", "AAA", "AAG", "TTA", "TTG", "CTT", "CTC",
                                                          "CTA", "CTG", "ATG", "AAT", "AAC", "CCT", "CCC", "CCA", "CCG",
                                                          "CAA", "CAG", "CGT", "CGC", "CGA", "CGG", "AGA", "AGG", "TCT",
                                                          "TCC", "TCA", "TCG", "AGT", "AGC", "ACT", "ACC", "ACA", "ACG",
                                                          "GTT", "GTC", "GTA", "GTG", "TGG", "TAT", "TAC"], repr=False)
    INV_CODON_TABLE_SPLIT: dict = field(default_factory=lambda: {'Ile': ['ATA', 'ATC', 'ATT'], 'Met': ['ATG'],
                                                                 'Thr': ['ACA', 'ACC', 'ACG', 'ACT'],
                                                                 'Asn': ['AAC', 'AAT'], 'Lys': ['AAA', 'AAG'],
                                                                 'Ser2': ['AGC', 'AGT'], 'Gln': ['CAA', 'CAG'],
                                                                 'Ser4': ['TCT', 'TCC', 'TCA', 'TCG'],
                                                                 'Phe': ['TTT', 'TTC'], 'Arg2': ['AGA', 'AGG'],
                                                                 'Arg4': ['CGT', 'CGC', 'CGA', 'CGG'],
                                                                 'Leu': ['CTA', 'CTC', 'CTG', 'CTT'],
                                                                 'Leu2': ['TTA', 'TTG'], 'His': ['CAT', 'CAC'],
                                                                 'Pro': ['CCT', 'CCC', 'CCA', 'CCG'],
                                                                 'Val': ['GTT', 'GTC', 'GTA', 'GTG'],
                                                                 'Ala': ['GCT', 'GCC', 'GCA', 'GCG'],
                                                                 'Asp': ['GAT', 'GAC'], 'Glu': ['GAA', 'GAG'],
                                                                 'Gly': ['GGT', 'GGC', 'GGA', 'GGG'],
                                                                 'Tyr': ['TAT', 'TAC'], 'Cys': ['TGC', 'TGT'],
                                                                 'Trp': ['TGG'], 'Stop': ['TGA', 'TAG', 'TAA']},
                                        repr=False)

    INV_CODON_TABLE: dict = field(default_factory=lambda: {'Ile': ['ATA', 'ATC', 'ATT'], 'Met': ['ATG'],
                                                           'Thr': ['ACA', 'ACC', 'ACG', 'ACT'],
                                                           'Asn': ['AAC', 'AAT'], 'Lys': ['AAA', 'AAG'],
                                                           'Ser': ['TCT', 'TCC', 'TCA', 'TCG', 'AGC', 'AGT'],
                                                           'Phe': ['TTT', 'TTC'], 'Glu': ['GAA', 'GAG'],
                                                           'Arg': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
                                                           'Leu': ['CTA', 'CTC', 'CTG', 'CTT', 'TTA', 'TTG'],
                                                           'Pro': ['CCT', 'CCC', 'CCA', 'CCG'],
                                                           'His': ['CAT', 'CAC'], 'Gln': ['CAA', 'CAG'],
                                                           'Val': ['GTT', 'GTC', 'GTA', 'GTG'], 'Trp': ['TGG'],
                                                           'Ala': ['GCT', 'GCC', 'GCA', 'GCG'],
                                                           'Asp': ['GAT', 'GAC'], 'Stop': ['TGA', 'TAG', 'TAA'],
                                                           'Gly': ['GGT', 'GGC', 'GGA', 'GGG'],
                                                           'Tyr': ['TAT', 'TAC'], 'Cys': ['TGC', 'TGT']}, repr=False)
    ONE_LETTER_AA: list = field(default_factory=lambda: list("ACDEFGHIKLMNPQRSTVWY"), repr=False)
    ONE_LETTER_AA_NO_I: list = field(default_factory=lambda: list("ACDEFGHKLMNPQRSTVWY"), repr=False)
    THREE_LETTER_AA: list = field(default_factory=lambda: ['Ala', 'Cys', 'Asp', 'Glu', 'Phe', 'Gly', 'His', 'Ile',
                                                           'Lys', 'Leu', 'Met', 'Asn', 'Pro', 'Gln', 'Arg', 'Ser',
                                                           'Thr', 'Val', 'Trp', 'Tyr'])
    THREE_LETTER_AA_NO_I: list = field(default_factory=lambda: ['Ala', 'Cys', 'Asp', 'Glu', 'Phe', 'Gly', 'His', 'Lys',
                                                                'Leu', 'Met', 'Asn', 'Pro', 'Gln', 'Arg', 'Ser', 'Thr',
                                                                'Val', 'Trp', 'Tyr'])

    CODONTABLE_SPLIT: dict = field(default_factory=lambda: {'ATA': 'Ile', 'ATC': 'Ile', 'ATT': 'Ile', 'ATG': 'Met',
                                                            'ACA': 'Thr', 'ACC': 'Thr', 'ACG': 'Thr', 'ACT': 'Thr',
                                                            'AAC': 'Asn', 'AAT': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
                                                            'AGC': 'Ser2', 'AGT': 'Ser2', 'AGA': 'Arg2',
                                                            'AGG': 'Arg2', 'CTA': 'Leu', 'CTC': 'Leu',
                                                            'CTG': 'Leu', 'CTT': 'Leu', 'CCA': 'Pro', 'CCC': 'Pro',
                                                            'CCG': 'Pro', 'CCT': 'Pro', 'CAC': 'His', 'CAT': 'His',
                                                            'CAA': 'Gln', 'CAG': 'Gln', 'CGA': 'Arg', 'CGC': 'Arg',
                                                            'CGG': 'Arg', 'CGT': 'Arg', 'GTA': 'Val', 'GTC': 'Val',
                                                            'GTG': 'Val', 'GTT': 'Val', 'GCA': 'Ala', 'GCC': 'Ala',
                                                            'GCG': 'Ala', 'GCT': 'Ala', 'GAC': 'Asp', 'GAT': 'Asp',
                                                            'GAA': 'Glu', 'GAG': 'Glu', 'GGA': 'Gly', 'GGC': 'Gly',
                                                            'GGG': 'Gly', 'GGT': 'Gly', 'TCA': 'Ser4',
                                                            'TCC': 'Ser4', 'TCG': 'Ser4', 'TCT': 'Ser4',
                                                            'TTC': 'Phe', 'TTT': 'Phe', 'TTA': 'Leu2',
                                                            'TTG': 'Leu2', 'TAC': 'Tyr', 'TAT': 'Tyr',
                                                            'TAA': 'Stop', 'TAG': 'Stop', 'TGC': 'Cys',
                                                            'TGT': 'Cys', 'TGA': 'Stop', 'TGG': 'Trp',
                                                            'LAT': 'Ile'}, repr=False)
    CODONTABLE: dict = field(default_factory=lambda: {'ATA': 'Ile', 'ATC': 'Ile', 'ATT': 'Ile', 'ATG': 'Met',
                                                      'ACA': 'Thr', 'ACC': 'Thr', 'ACG': 'Thr', 'ACT': 'Thr',
                                                      'AAC': 'Asn', 'AAT': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
                                                      'AGC': 'Ser', 'AGT': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
                                                      'CTA': 'Leu', 'CTC': 'Leu', 'CTG': 'Leu', 'CTT': 'Leu',
                                                      'CCA': 'Pro', 'CCC': 'Pro', 'CCG': 'Pro', 'CCT': 'Pro',
                                                      'CAC': 'His', 'CAT': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
                                                      'CGA': 'Arg', 'CGC': 'Arg', 'CGG': 'Arg', 'CGT': 'Arg',
                                                      'GTA': 'Val', 'GTC': 'Val', 'GTG': 'Val', 'GTT': 'Val',
                                                      'GCA': 'Ala', 'GCC': 'Ala', 'GCG': 'Ala', 'GCT': 'Ala',
                                                      'GAC': 'Asp', 'GAT': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
                                                      'GGA': 'Gly', 'GGC': 'Gly', 'GGG': 'Gly', 'GGT': 'Gly',
                                                      'TCA': 'Ser', 'TCC': 'Ser', 'TCG': 'Ser', 'TCT': 'Ser',
                                                      'TTC': 'Phe', 'TTT': 'Phe', 'TTA': 'Leu', 'TTG': 'Leu',
                                                      'TAC': 'Tyr', 'TAT': 'Tyr', 'TAA': 'Stop', 'TAG': 'Stop',
                                                      'TGC': 'Cys', 'TGT': 'Cys', 'TGA': 'Stop', 'TGG': 'Trp',
                                                      'LAT': 'Ile'}, repr=False)

    WC: dict = field(default_factory=lambda: {"A": "T", "C": "G", "G": "C", "T": "A", "L": "A"}, repr=False)
    NUC: list = field(default_factory=lambda: list("ATCG"), repr=False)
    NUC_IDX: dict = field(default_factory=lambda: {"A": 0, "C": 1, "G": 2, "T": 3, "N": 4, "L": 5}, repr=False)

    REV_COMPL: dict = field(default_factory=dict, init=False, repr=False)

    # FUNCTIONS
    def __post_init__(self):
        self.REV_COMPL = {c: self.reverse_complement(c) for c in self.CODONS}

        self.codon_idx = {codon: self.THREE_LETTER_AA.index(self.CODONTABLE[codon]) for codon in self.CODONS_NO_STOP}

        self.trna = pd.read_csv(self.anticodon_file, delimiter=",", header=0)

        # drop STOP AC until we have actual energies for the RFs
        self.trna.index = self.trna['Anticodon']
        self.trna = self.trna.drop(['TTA', 'CTA', 'TCA'], axis=0)

        self.available_trna = list(self.trna['Anticodon'])

        self.arrival_rate = self.calculate_arrival_rates()
        self.arrival_probabilities = self.calculate_arrival_probabilities()

        aa_group = self.arrival_rate.groupby('AA')
        for aa in self.THREE_LETTER_AA:  # Add STOP codons once we have actual energies
            self.synonymous_trna[aa] = list(aa_group.get_group(aa)['Anticodon'])

        # these two are needed for the acceptance probability. Pre-cast them to numpy as this seems to take quite a
        # bit of the total computation time
        self.ap = np.array(self.arrival_probabilities['First'])
        self.ar = np.array(self.arrival_rate['ArrivalRate'])

    def format_wobble_penalties(self, wobble_param):
        """
        :param wobble_param: wobble parameters exculding Watson-Crick pairs (12)
        :return: Dictionary with wobble parameters, and Watson-Crick Pairs set to 1
        """

        ret = dict(zip(self.WC_NUC_PAIRS, wobble_param))
        return ret

    def reverse_complement(self, current_codon):
        return self.WC[current_codon[2]] + self.WC[current_codon[1]] + self.WC[current_codon[0]]

    def calculate_arrival_rates(self):
        # Parameters taken from Shah et. al 2013
        effect_length = 1.5e-8
        diffusion_coeff = 8.42e-11
        transition_time = (effect_length ** 2) / (6 * diffusion_coeff)  # transition time between locations
        n_loc = self.cell_volume / effect_length ** 3  # number of locations in a cell

        ar = pd.DataFrame()
        ar['Anticodon'] = self.available_trna
        ar.index = ar['Anticodon']
        ar['ArrivalRate'] = self.trna['Abundance'].map(lambda x: (x / n_loc) / transition_time)
        ar['AA'] = self.trna['Anticodon'].map(lambda x: self.CODONTABLE[self.REV_COMPL[x]])
        return ar

    def calculate_arrival_probabilities(self):
        denominator = self.arrival_rate['ArrivalRate'].sum()
        df_index = self.available_trna
        ap = pd.DataFrame()
        aa_rate = self.arrival_rate.groupby('AA').sum(numeric_only=True)

        ap['First'] = self.arrival_rate['ArrivalRate'].map(lambda x: x / denominator)
        ap['First_syn'] = self.arrival_rate.apply(lambda row: row['ArrivalRate'] / aa_rate.at[row['AA'], 'ArrivalRate'],
                                                  axis=1)
        for ac in self.available_trna:
            focal_ac = self.arrival_rate.at[ac, 'ArrivalRate']
            ap[ac] = self.arrival_rate['ArrivalRate'].map(lambda x: focal_ac / (focal_ac + x))
        ap.index = df_index
        return ap

    @staticmethod
    def calc_dr(ac, c, position_penalty, wobble_set):
        wp1 = wobble_set[c[0] + ac[2]]
        wp2 = wobble_set[c[1] + ac[1]]
        wp3 = wobble_set[c[2] + ac[0]]

        # position penalty for position three is fixed to 1
        return position_penalty[0] * wp1 + position_penalty[1] * wp2 + wp3

    def calculate_detection_parameter(self, trnas, c, position_penalty, wobble_set):
        dr = np.array([self.calc_dr(ac, c, position_penalty, wobble_set) for ac in trnas])

        return dr

    def calculate_asite_binding_probability(self, acodon, trnas, position_penalty=None, wobble_set=None):
        detection_rates = self.calculate_detection_parameter(trnas, acodon, position_penalty, wobble_set)
        delta_stability = np.exp(-detection_rates)  # stability of codon/anticodon interaction
        p_binding_a = delta_stability / np.sum(delta_stability)

        return p_binding_a

    def calculate_acceptance_probability(self, pb):
        nrow = pb.shape[0]
        not_p_b = 1 - pb
        return self.calculate_acceptance_probability_jit(pb, not_p_b, self.ap, self.ar, nrow)

    @staticmethod
    @jit(nopython=True)
    def calculate_acceptance_probability_jit(pb, not_p_b, ap, ar, n):
        p_acceptance = np.zeros(pb.shape)
        for ac1 in range(n):
            p_acceptance[ac1] = pb[ac1] * ap[ac1]
            x = np.delete(not_p_b, ac1)
            y = np.delete(ar, ac1)
            tmp = np.prod(np.power(x, y / ar[ac1]))
            p_acceptance[ac1] += (tmp * pb[ac1]) * (1 - ap[ac1])

        return p_acceptance / np.sum(p_acceptance)

    def calculate_substitution_probability(self, acodon, position_penalty, wobble_set):
        trnas = self.available_trna
        asite_binding_probability = self.calculate_asite_binding_probability(acodon, trnas, position_penalty,
                                                                             wobble_set)
        return self.calculate_acceptance_probability(asite_binding_probability)

    def calculate_all_substitution_probabilities(self, position_penalty, wobble_set, combine_ile_leu=False):
        np_sub_probs = np.zeros(shape=(len(self.CODONS_NO_STOP), len(self.available_trna)), dtype='float')

        for i, current_codon in enumerate(self.CODONS_NO_STOP):
            np_sub_probs[i] = self.calculate_substitution_probability(current_codon, position_penalty, wobble_set)

        # Convert codon to anticodon dataframe to codon to amino acid dataframe
        np_codon_to_aa = np.zeros(shape=(len(self.CODONS_NO_STOP), len(self.THREE_LETTER_AA)), dtype='float')
        for c, current_codon in enumerate(self.CODONS_NO_STOP):
            for ac, anticodon in enumerate(self.available_trna):
                trna = self.REV_COMPL[anticodon]
                aa = self.codon_idx[trna]  # amino acid of the attempting tRNA
                np_codon_to_aa[c, aa] += np_sub_probs[c, ac]

        codon_to_aa = pd.DataFrame(np_codon_to_aa, index=self.CODONS_NO_STOP, columns=self.THREE_LETTER_AA)
        if combine_ile_leu:
            codon_to_aa['Leu'] = codon_to_aa['Ile'] + codon_to_aa['Leu']
            codon_to_aa = codon_to_aa.drop('Ile', axis=1)
            codon_to_aa = codon_to_aa[self.THREE_LETTER_AA_NO_I]

        # Numerics (double check that this is not a bug) causes near 0 negative numbers.
        codon_to_aa[codon_to_aa <= 0] = 1e-20  # avoid zero since we want to take the log in the MCMC
        codon_to_aa = codon_to_aa.div(codon_to_aa.sum(axis=1), axis=0)

        return codon_to_aa

    def simulate_data(self, position_penalty, wobble_penalty):
        substitution_probabilities = self.calculate_all_substitution_probabilities(position_penalty, wobble_penalty,
                                                                                   combine_ile_leu=True)
        simulated_codon_counts = pd.DataFrame(0, index=substitution_probabilities.index,
                                              columns=substitution_probabilities.columns)
        ncodons = len(substitution_probabilities.index)
        n_codons_observed = pd.DataFrame(0, index=substitution_probabilities.index, columns=['Count'])
        n_codons_observed['Count'] = 10000 * np.random.randn(ncodons) + 45000
        for codon in substitution_probabilities.index:
            simulated_codon_counts.loc[codon:, ] = np.random.multinomial(n_codons_observed.at[codon, 'Count'],
                                                                         substitution_probabilities.loc[codon, :])
        return n_codons_observed.astype('int32'), simulated_codon_counts.astype('int32')

    def calculate_incorporation_probability(self, seq, position_penalty, wobble_penalty, include_fs=True):
        incorporation_df = pd.DataFrame()
        if include_fs:
            # default is full 10-mer
            is_start, is_start = False, False
            if len(seq) == 5:
                is_start = (seq[0:3] == 'ATG')
                is_end = not is_start
            # TODO implement FS model
        else:
            incorporation_df = self.calculate_substitution_probability(seq, position_penalty, wobble_penalty)

        return incorporation_df


'''
if __name__ == "__main__":
    model = MTEM(anticodon_file="parameter_files/ecoli_tRNA_count_SRR1232430.csv", cell_volume=0.6e-18)

    pp = np.array(pd.read_csv('output/pride_filtered_ecoli/position_2022-03-10.csv', index_col=0, header=0)).flatten()
    w = np.array(pd.read_csv('output/pride_filtered_ecoli/wobble_2022-03-10.csv', index_col=0, header=0)).flatten()
    wp = model.format_wobble_penalties(w)
    test = model.calculate_all_substitution_probabilities(pp, wp)

    test = pd.Series(model.calculate_asite_binding_probability('ATT', model.available_trna, pp, wp))
    test.index = model.available_trna

    df = pd.DataFrame(index=model.CODONS, columns=model.CODONS)
    for codon in model.CODONS:
        df[codon] = model.calculate_detection_parameter(model.CODONS, codon, pp, wp)

    df.to_csv('output/ecoli/fitted_energies.csv')
'''