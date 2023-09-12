"""
Most routines are taken from the workflow created by Ernest Mordret (Mordret et al. 2019, Cell)
The functions were cleaned up to eliminate global variables and to make the workflow more command line and git friendly.
"""
from itertools import groupby
from operator import itemgetter
from numba import njit

import collections as clt
import pandas as pd
import numpy as np

import re


def create_suffix_array(text, _step=16):
    """Analyze all common strings in the text.

    Short substrings of the length _step a are first pre-sorted. The are the
    results repeatedly merged so that the garanteed number of compared
    characters bytes is doubled in every iteration until all substrings are
    sorted exactly.

    Arguments:
        text:  The text to be analyzed.
        _step: Is only for optimization and testing. It is the optimal length
               of substrings used for initial pre-sorting. The bigger value is
               faster if there is enough memory. Memory requirements are
               approximately (estimate for 32 bit Python 3.3):
                   len(text) * (29 + (_size + 20 if _size > 2 else 0)) + 1MB

    Return value:      (tuple)
      (sa, rsa, lcp)
        sa:  Suffix array                  for i in range(1, size):
               assert text[sa[i-1]:] < text[sa[i]:]
        rsa: Reverse suffix array          for i in range(size):
               assert rsa[sa[i]] == i
        lcp: Longest common prefix         for i in range(1, size):
               assert text[sa[i-1]:sa[i-1]+lcp[i]] == text[sa[i]:sa[i]+lcp[i]]
               if sa[i-1] + lcp[i] < len(text):
                   assert text[sa[i-1] + lcp[i]] < text[sa[i] + lcp[i]]

    suffix_array(text='banana')
    ([5, 3, 1, 0, 4, 2], [3, 2, 5, 1, 4, 0], [0, 1, 3, 0, 0, 2])

    Explanation: 'a' < 'ana' < 'anana' < 'banana' < 'na' < 'nana'
    The Longest Common String is 'ana': lcp[2] == 3 == len('ana')
    It is between  tx[sa[1]:] == 'ana' < 'anana' == tx[sa[2]:]
    """
    tx = text
    size = len(tx)
    step = min(max(_step, 1), len(tx))
    sa = list(range(len(tx)))
    sa.sort(key=lambda i: tx[i:i + step])
    grpstart = size * [False] + [True]  # a boolean map for iteration speedup.
    # It helps to skip yet resolved values. The last value True is a sentinel.
    rsa = size * [None]
    stgrp, igrp = '', 0
    for i, pos in enumerate(sa):
        st = tx[pos:pos + step]
        if st != stgrp:
            grpstart[igrp] = (igrp < i - 1)
            stgrp = st
            igrp = i
        rsa[pos] = igrp
        sa[i] = pos
    grpstart[igrp] = (igrp < size - 1 or size == 0)
    while grpstart.index(True) < size:
        # assert step <= size
        nextgr = grpstart.index(True)
        while nextgr < size:
            igrp = nextgr
            nextgr = grpstart.index(True, igrp + 1)
            glist = []
            for ig in range(igrp, nextgr):
                pos = sa[ig]
                if rsa[pos] != igrp:
                    break
                newgr = rsa[pos + step] if pos + step < size else -1
                glist.append((newgr, pos))
            glist.sort()
            for ig, g in groupby(glist, key=itemgetter(0)):
                g = [x[1] for x in g]
                sa[igrp:igrp + len(g)] = g
                grpstart[igrp] = (len(g) > 1)
                for pos in g:
                    rsa[pos] = igrp
                igrp += len(g)
        step *= 2
    del grpstart
    del rsa
    return np.array(sa)

@njit()
def search_suffix_array(searchstring, search_db, sa):
    lp = len(searchstring)
    n = len(sa)
    l = 0
    r = n
    while l < r:
        mid = int((l + r) / 2)
        a = sa[mid]
        if searchstring > search_db[a: a + lp]:
            l = mid + 1
        else:
            r = mid
    s = l
    r = n
    while l < r:
        mid = int((l + r) / 2)
        a = sa[mid]
        if searchstring < search_db[a: a + lp]:
            r = mid
        else:
            l = mid + 1
    return [sa[i] for i in range(s, r)]


def get_codons():
    bases = 'TCAG'
    return [a + b + c for a in bases for b in bases for c in bases]


def invert_codon_table(ct):
    """
    input: Codon table as dictionary with codons as keys and amino acids as values
    output: Dictionary with amino acids as keys and codons as values
    """
    inv_codon_table = clt.defaultdict(list)
    for k, v in ct.items():
        inv_codon_table[v] = inv_codon_table.get(v, [])
        inv_codon_table[v].append(k)
    return inv_codon_table


def get_mass_substitution_dict():
    """
    output: Dictionary of amino acid (key) mass differences (value)
    """
    aa_mass = {"G": 57.02147, "A": 71.03712, "S": 87.03203, "P": 97.05277, "V": 99.06842, "T": 101.04768,
               "I": 113.08407, "L": 113.08407, "N": 114.04293, "D": 115.02695, "Q": 128.05858, "K": 128.09497,
               "E": 129.0426, "M": 131.04049, "H": 137.05891, "F": 147.06842, "R": 156.10112, "C": 160.030654,  # CamCys
               "Y": 163.0633, "W": 186.07932, "*": 71.03712}

    subs_dict_complete = {i + ' to ' + j: aa_mass[j] - aa_mass[i] for i in aa_mass for j in aa_mass if i != j}
    del subs_dict_complete['L to I']
    del subs_dict_complete['I to L']

    subs_dict_complete = {k: v for k, v in subs_dict_complete.items() if k[-1] != 'L'}
    subs_dict = clt.defaultdict(int)
    for k, v in subs_dict_complete.items():  # unifies I and L
        if k[-1] == 'I':
            subs_dict[k + '/L'] = v
        else:
            subs_dict[k] = v

    return subs_dict


def codonify(seq):
    """
    input: a nucleotide sequence (not necessarily a string)
    output: a list of codons
    """
    seq = str(seq)
    l = len(seq)
    return [seq[i:i + 3] for i in range(0, l, 3)]


def is_gene(record, needs_stop_end=True):
    if len(record.seq) % 3 != 0:
        return False
    if not record.seq[:3] in {'ATG', 'GTG', 'TTG', 'ATT', 'CTG'}:
        return False
    if record.seq[-3:].translate() != '*' and needs_stop_end:
        return False
    return True


def c_term_probability(modified_sequence):
    """
    Returns the probability that C term AA was modified.
    """
    if modified_sequence[-1] == ')':
        return float(modified_sequence[:-1].split('(')[-1])
    else:
        return 0.0


def n_term_probability(modified_sequence):
    """
    Returns the probability that C term AA was modified.
    """
    if modified_sequence[1] == '(':
        return float(modified_sequence[2:].split(')')[0])
    else:
        return 0.0

@njit()
def is_prot_nterm(sequence, w_aa, suffix_array):
    """
    Does the peptide originate at the protein's N-term
    """
    for start in search_suffix_array(sequence, w_aa, suffix_array):
        if w_aa[start - 1] == '*':
            return True
        if w_aa[start - 2] == '*':
            return True
    return False

@njit()
def is_prot_cterm(sequence, w_aa, suffix_array):
    l = len(sequence)
    for start in search_suffix_array(sequence, w_aa, suffix_array):
        end = start + l
        if w_aa[end] == '*':
            return True
    return False


def refine_localization_probabilities(modified_seq, threshold=0.05):
    """
    returns the AAs that were possibly modified (with p > threshold).
    Input: modified sequence (a string of AA with p of each to contain modification: APKV(.7)ML(.3)L means
    that V was modified with p = .7 and L with p = .3)
    Output: A string with all candidate AAs separated by ';' (V;L).
    """
    modified_sites = [modified_seq[m.start() - 1] for m in re.finditer('\(', modified_seq)]
    weights = [float(i) for i in re.findall('\(([^\)]+)\)', modified_seq)]
    site_probabilities = {}
    for aa, weight in zip(modified_sites, weights):
        if aa in site_probabilities:
            site_probabilities[aa] += weight
        else:
            site_probabilities[aa] = weight
    return ";".join([k for k, v in site_probabilities.items() if v > threshold])


def read_allpeptide(filename, w_aa, sa, prot_bounds, prot_names, chunksize=10000, dp_columns=None):
    if dp_columns is None:
        dp_columns = [u'Raw file', u'Charge', u'm/z', u'Retention time', u'Sequence', u'Proteins', u'DP Base Sequence',
                      u'DP Mass Difference', u'DP Time Difference', u'DP PEP', u'DP Base Sequence', u'DP Probabilities',
                      u'DP Positional Probability', u'DP Decoy', u'DP Base Scan Number', u'DP Mod Scan Number']

    df_iter = pd.read_csv(filename, sep='\t', chunksize=chunksize, iterator=True, usecols=dp_columns)
    dp = pd.concat(chunk[pd.notnull(chunk['DP Mass Difference'])] for chunk in df_iter)
    dp.reset_index(drop=True, inplace=True)

    print('\tfinished reading... processing columns')

    dp['DPMD'] = dp['DP Mass Difference']
    dp['BASE_SCAN'] = dp['DP Base Scan Number']
    dp['MOD_SCAN'] = dp['DP Mod Scan Number']
    dp['DPAA_noterm'] = dp['DP Probabilities'].map(refine_localization_probabilities)
    dp['nterm'] = dp['DP Probabilities'].map(n_term_probability)  # p(N-term AA was substituted)
    dp['cterm'] = dp['DP Probabilities'].map(c_term_probability)
    # Does the peptide come from the N-term of the protein
    dp['prot_nterm'] = dp['DP Base Sequence'].map(lambda x: is_prot_nterm(x, w_aa, sa))
    dp['prot_cterm'] = dp['DP Base Sequence'].map(lambda x: is_prot_cterm(x, w_aa, sa))
    dp['proteins'] = dp['DP Base Sequence'].map(lambda x: find_proteins(x, prot_bounds, w_aa, sa, prot_names))
    dp['protein'] = dp['proteins'].map(lambda x: x.split(' ')[0] if len(x) > 0 else float('NaN'))
    dp['srt'] = False

    return dp


def find_peptide_start_position(protein_id, peptide, cds_aa):
    if protein_id != protein_id:  # test if protein_id is not NA or similar
        return -1
    db_cds = str(cds_aa[protein_id])
    # The minimum index is also the first occurrence in case the peptide occurs multiple times in the sequence
    # This means a potential SRT might be missed but this conservative approach is on purpose as we can not distinguish
    # which peptide we actuall see
    return db_cds.find(peptide)  # finds minimum index


def is_base_peptide_srt(protein_id, current_peptide, min_pos, wtlens):
    is_srt = False
    if protein_id != protein_id:
        return is_srt
    max_pos = min_pos + len(current_peptide)
    cds_length = wtlens[protein_id]
    if min_pos > cds_length or max_pos > cds_length:
        is_srt = True

    return is_srt


def is_dependent_peptide_srt(protein, position, wtlens):
    return wtlens[protein] - 1 < position


def find_proteins(base_seq, protein_bounds, w_aa, suffix_array, protein_names):
    """
    input: a peptide sequence (string)
    output: the names of proteins containing that sequence
    """
    tbr = " ".join([protein_names[i] for i in np.searchsorted(protein_bounds - 1,
                                                              search_suffix_array(base_seq, w_aa, suffix_array))])
    if tbr.strip(" ") == '':
        return ''
    else:
        return tbr


def fetch_codon_counts_in_peptide(peptide, cds_aa_dict, codons, prot_bounds, w_aa, sa, prot_names):
    """
    :param peptide: The peptide to search for in the proteome, for which the codons are identified
    :param cds_aa_dict: The proteome to search the peptide in
    :param codons: The codons to search for
    :return: DataFrame containing the counts of each codon in the sequence.
            Ambiguous peptides will be considered at all positions
    """

    possible_codons = np.zeros(len(codons))
    proteins = find_proteins(peptide, prot_bounds, w_aa, sa, prot_names)
    if proteins:
        proteins = proteins.split(" ")
    else:
        return possible_codons
    for p in proteins:
        if p in cds_aa_dict:
            s = cds_aa_dict[p].seq
            seq_i = s.translate().find(peptide)
            codon_seq = codonify(s)
            for i in range(seq_i, seq_i + len(peptide)):
                possible_codons[codons.index(codon_seq[i])] += 1

    return possible_codons


def count_observed_base_codons(peptide_df, cds_aa_dict, codons, prot_bounds, w_aa, sa, prot_names):
    """ Count all identified codons """
    codon_counts = np.zeros(len(codons))
    for peptide in peptide_df['DP Base Sequence']:
        codon_counts += fetch_codon_counts_in_peptide(peptide, cds_aa_dict, codons, prot_bounds, w_aa, sa, prot_names)

    return pd.DataFrame(data=codon_counts, index=codons, columns=['Count'])


def mark_dangerous_peptides(peptide_df, file_handle, aas, arguments):
    danger_mods = pd.read_csv(file_handle)
    peptide_df['danger'] = False
    for mod in danger_mods.iterrows():
        mod = mod[1]
        position = mod['position']
        site = mod['site']
        delta_m = mod['delta_m']

        mass_filter = (delta_m - (2 * arguments.tol) < peptide_df.DPMD) & \
                      (peptide_df.DPMD < delta_m + (2 * arguments.tol))

        term_filter = True
        if position == 'Protein N-term':
            term_filter = (peptide_df.nterm > arguments.n_term_prob_cutoff) & peptide_df.prot_nterm
        elif position == 'Protein C-term':
            term_filter = (peptide_df.cterm > arguments.c_term_prob_cutoff) & peptide_df.prot_cterm
        elif position == 'Any N-term':
            term_filter = peptide_df.nterm > arguments.n_term_prob_cutoff
        elif position == 'Any C-term':
            term_filter = peptide_df.cterm > arguments.c_term_prob_cutoff

        site_filter = True
        if site in aas:
            site_filter = peptide_df.DPAA_noterm.str.contains(site)

        peptide_df.loc[site_filter & term_filter & mass_filter, 'danger'] = True

    return peptide_df


def mark_substitutions(peptide_df, mass_diff_dict, tolerance, ppc):
    peptide_df['substitution'] = False
    for i in sorted(mass_diff_dict.keys()):
        delta_m = mass_diff_dict[i]
        original_aa = i[0]
        peptide_df.loc[(peptide_df.DPMD > delta_m - tolerance) & (peptide_df.DPMD < delta_m + tolerance) &
                       (peptide_df['DPAA_noterm'] == original_aa) & (peptide_df['DP Positional Probability'] > ppc) &
                       ~peptide_df['danger'], 'substitution'] = i
    return peptide_df


def hamming(s1, s2):
    return sum(a != b for a, b in zip(s1, s2))


def define_mispairing_mask(codons, aas, i_codon_table):
    """
    Create mask for mispairing. A binary dataframe indicating for each codon the AAs encoded by near-cognate codons.
    """
    mask = pd.DataFrame(data=False, index=codons, columns=list('ACDEFGHKLMNPQRSTVWY*'), dtype=float)
    for label in codons:
        near_cognates = np.array([hamming(i, label) == 1 for i in codons])
        reachable_aa = set(np.array(list(aas))[near_cognates])
        mask.loc[label] = [i in reachable_aa for i in 'ACDEFGHKLMNPQRSTVWY*']

    for label in mask.index:  # removes "near-cognates" that encodes the same AA
        for col in mask.columns:
            if label in i_codon_table[col]:
                mask.loc[label, col] = float('NaN')

    return mask


def fetch_codon(base_seq, modified_pos, cds_dict, prot_bounds, w_aa, sa, prot_names):
    """
    input: the original aa sequence of a peptide (base_seq),
            and the relative position of the modification.
    output: returns the list of all codons possibly associated
            with the substitution, presented as a string separated
            by white spaces.
    """
    possible_codons = []
    proteins = find_proteins(base_seq, prot_bounds, w_aa, sa, prot_names)
    if proteins:
        proteins = proteins.split(" ")
    else:
        return '_'
    for p in proteins:
        if p in cds_dict:
            s = cds_dict[p].seq
            seq_i = s.translate().find(base_seq)
            i = seq_i + modified_pos
            possible_codons.append(codonify(s)[i])
        else:
            possible_codons.append('_')
    return " ".join(possible_codons)


def fetch_best_codons(modified_seq, cds_dict, prot_bounds, w_aa, sa, prot_names):
    """
    input: a modified sequence, e.g. LQV(0.91)A(0.09)EK
    output: the list of codons associated with the most likely
            position
    """
    possible_sites = re.findall('\(([^\)]+)\)', modified_seq)
    best_site = np.argmax([float(i) for i in possible_sites])
    modified_pos_prime = [m.start() - 1 for m in re.finditer('\(', modified_seq)][best_site]
    modified_pos = len(re.sub('\(([^\)]+)\)', '', modified_seq[:modified_pos_prime]))
    base_seq = re.sub('\(([^\)]+)\)', '', modified_seq)
    return fetch_codon(base_seq, modified_pos, cds_dict, prot_bounds, w_aa, sa, prot_names)


def is_mispairing(codon, destination, mask):
    """
    Returns whether the substitution is mispairing or misloading, based on the
    near-cognate mask.
    """
    #codon = row['codon']
    #destination = row['destination']
    if pd.notnull(codon) and pd.notnull(destination):
        if (codon in mask.index) and destination:
            return mask.loc[codon, destination]
        else:
            return 0
    else:
        return float('NaN')


def find_substitution_position_local(modified_seq, protein, cds_dict):
    """
    returns the position of a substitutions relative to the start
    of the protein sequence
    """
    possible_sites = re.findall('\(([^\)]+)\)', modified_seq)
    best_site = np.argmax([float(i) for i in possible_sites])
    modified_pos_prime = [m.start() - 1 for m in re.finditer('\(', modified_seq)][best_site]
    modified_pos = len(re.sub('\(([^\)]+)\)', '', modified_seq[:modified_pos_prime]))
    base_seq = re.sub('\(([^\)]+)\)', '', modified_seq)
    s = cds_dict[protein].seq
    seq_i = s.translate().find(base_seq)
    i = seq_i + modified_pos
    return i


def find_positions_local(modified_seq, proteins, cds_dict):
    """
    returns the position of a substitutions relative to the start
    of the protein sequence, across all the codons
    """
    positions = []
    for prot in proteins.split(" "):
        positions.append(str(find_substitution_position_local(modified_seq, prot, cds_dict)))
    return " ".join(positions)


def create_modified_seq(modified_seq, destination):
    if type(destination) == str:
        possible_sites = re.findall('\(([^\)]+)\)', modified_seq)
        best_site = np.argmax([float(i) for i in possible_sites])
        modified_pos_prime = [m.start() - 1 for m in re.finditer('\(', modified_seq)][best_site]
        modified_pos = len(re.sub('\(([^\)]+)\)', '', modified_seq[: modified_pos_prime]))
        base_seq = re.sub('\(([^\)]+)\)', '', modified_seq)
        return base_seq[: modified_pos] + destination + base_seq[modified_pos + 1:]
    else:
        return ""


def find_homologous_peptide(peptide, is_srt, w_aa_ambiguous, sa_ambiguous):
    """
    Gets a peptide and returns whether it has homolegous in the genome.
    If so, that peptide is discarded.
    """
    if is_srt:
        return True
    if len(search_suffix_array('K' + peptide, w_aa_ambiguous, sa_ambiguous)) > 0:
        return False
    if len(search_suffix_array('R' + peptide, w_aa_ambiguous, sa_ambiguous)) > 0:
        return False
    if len(search_suffix_array('*' + peptide, w_aa_ambiguous, sa_ambiguous)) > 0:
        return False
    return True


def process_substitutions(peptide_df, proteome_string_ambiguous, suffix_array_ambiguous, mask, cds_dict, wtlen,
                          prot_bounds, w_aa, sa, prot_names, pos_prop_cutoff, fdr):
    subs = peptide_df[(peptide_df['substitution'] != False) | (peptide_df['srt'] != False)].copy()
    subs = subs[pd.notnull(subs['protein'])]  # mismatching files?

    subs['codons'] = 'NaN'
    subs.loc[subs['DP Positional Probability'] > pos_prop_cutoff, 'codons'] = \
        subs[subs['DP Positional Probability'] > pos_prop_cutoff]['DP Probabilities'].map(lambda x:
                                                                                          fetch_best_codons(x, cds_dict,
                                                                                                            prot_bounds,
                                                                                                            w_aa, sa,
                                                                                                            prot_names))
    subs['codon'] = subs['codons'].map(lambda x: x.split(' ')[0] if len(set(x.split(' '))) == 1 else float('NaN'))
    subs['destination'] = subs['substitution'].map(lambda x: x[-1] if x else False)
    subs['origin'] = subs['substitution'].map(lambda x: x[0] if x else False)
    subs['mispairing'] = subs.apply(lambda row: is_mispairing(row['codon'], row['destination'], mask), axis=1)

    subs['positions'] = subs.apply(lambda row: find_positions_local(row['DP Probabilities'], row['proteins'], cds_dict),
                                   axis=1)
    subs['position'] = subs['positions'].map(
        lambda x: int(x.split(' ')[0]) if len(set(x.split(' '))) == 1 else float('NaN'))
    subs['wt_len'] = subs['protein'].map(lambda x: wtlen[x])
    subs['modified_sequence'] = subs.apply(lambda row: create_modified_seq(row['DP Probabilities'], row['destination']),
                                           axis=1)
    subs['modified_sequence'] = subs['modified_sequence'].map(lambda x: x.replace('I', 'L'))
    subs = subs[subs.apply(lambda row: find_homologous_peptide(row['modified_sequence'], row['srt'],
                                                               proteome_string_ambiguous,
                                                               suffix_array_ambiguous), axis=1)]

    subs.sort_values('DP PEP', inplace=True)
    subs['decoy'] = pd.notnull(subs['DP Decoy'])
    # Understand this FDR protocol
    cut_off = np.max(np.where(np.array([i / float(j) for i, j in zip(subs['decoy'].cumsum(),
                                                                     range(1, len(subs) + 1))]) < fdr))
    subs = subs.iloc[:cut_off + 1]

    subs = subs[~subs.decoy]
    subs['srt'] = subs.apply(lambda row: row['srt'] or is_dependent_peptide_srt(row['protein'], row['position'], wtlen),
                             axis=1)

    return subs
