import numpy as np
import collections as clt
import pandas as pd

from pathlib import Path
from Bio import SeqIO

import argparse
import time
import os
import re
from gooey import Gooey, GooeyParser


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


def codonify(seq):
    """
    input: a nucleotide sequence (not necessarily a string)
    output: a list of codons
    """
    seq = str(seq).upper()
    l = len(seq)
    return [seq[i:i + 3] for i in range(0, l, 3)]


def count_observed_codons(dp, cds_dict):
    codon_counts = clt.Counter()
    proteinID = np.array(dp['Protein'], dtype=str)
    peptideStartPos = np.array(dp['Protein Start'], dtype=int) - 1
    peptideEndPos = np.array(dp['Protein End'], dtype=int)
    for i in range(0, len(proteinID)):
        sequence = cds_dict[proteinID[i]]
        codon_seq = codonify(sequence.seq)

        codon_peptide = codon_seq[peptideStartPos[i]:peptideEndPos[i]]
        codon_counts.update(clt.Counter(codon_peptide))

    return codon_counts


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


def mark_danger_mods(dp, dm, mass_tol=0.005):
    aas = list('ACDEFGHIKLMNPQRSTVWY')

    dp['danger'] = False
    for mod in dm.iterrows():
        mod = mod[1]
        position = mod['position']
        site = mod['site']
        delta_m = mod['delta_m']

        mass_filter = (delta_m - (2 * mass_tol) < dp['Delta Mass']) & (dp['Delta Mass'] < delta_m + (2 * mass_tol))

        site_filter = True
        if site in aas:
            site_filter = dp.modAA.str.contains(site)

        term_filter = True
        if position == 'Protein N-term':
            term_filter = dp.is_prot_nterm
        elif position == 'Protein C-term':
            term_filter = dp.is_prot_cterm
        elif position == 'Any N-term':
            term_filter = dp.is_peptide_nterm
        elif position == 'Any C-term':
            term_filter = dp.is_peptide_cterm

        dp.loc[site_filter & term_filter & mass_filter, 'danger'] = True

    return dp


def define_near_cognate_mask(codons, aas, i_codon_table):
    """
    Create mask for mispairing. A binary dataframe indicating for each codon the AAs encoded by near-cognate codons.
    """

    def hamming(s1, s2):
        return sum(a != b for a, b in zip(s1, s2))

    mask = pd.DataFrame(data=False, index=codons, columns=list('ACDEFGHKLMNPQRSTVWY*'), dtype=float)
    for label in codons:
        near_cognates = np.array([hamming(i, label) == 1 for i in codons])
        reachable_aa = set(np.array(list(aas))[near_cognates])
        mask.loc[label] = [i in reachable_aa for i in 'ACDEFGHKLMNPQRSTVWY*']

    for label in mask.index:  # removes "near-cognates" that encodes the same AA
        for col in mask.columns:
            if label in i_codon_table[col]:
                mask.loc[label, col] = float('NaN')

    return mask.rename(columns={'L': 'I/L'})


def mark_substitutions(peptide_df, mass_diff_dict, tolerance):
    peptide_df['substitution'] = False
    for i in sorted(mass_diff_dict.keys()):
        delta_m = mass_diff_dict[i]
        original_aa = i[0]
        peptide_df.loc[(peptide_df['Delta Mass'] > (delta_m - tolerance)) &
                       (peptide_df['Delta Mass'] < (delta_m + tolerance)) &
                       (peptide_df['modAA'] == original_aa) & ~peptide_df['danger'], 'substitution'] = i
    return peptide_df


def peptide_in_proteome(peptide, proteome):
    return any([id for id, seq in proteome.items() if peptide in str(seq.seq)])


def is_valid_file(p, arg):
    if not os.path.exists(arg):
        p.error("The file %s does not exist!" % arg)
    else:
        return arg


def prep_folder(arg):
    if not os.path.exists(arg):
        os.mkdir(arg)

    return arg


def prepare(psm, dm_mass_tol, decoy, cds_names):
    psm = psm.loc[psm['Is Unique'], :].copy()
    psm['is_decoy'] = psm['Protein'].map(lambda p: re.search(decoy, p) is not None)
    psm['is_contaminant'] = psm['Protein'].map(lambda p: p not in cds_names)
    psm.query("not is_decoy and not is_contaminant", inplace=True)
    psm['Delta Mass'] = psm['Delta Mass'].astype(float)
    psm['zero_shift_peptide'] = psm['Delta Mass'].map(lambda dm: (dm < dm_mass_tol) and (dm > -dm_mass_tol))
    psm['is_prot_nterm'] = psm['Prev AA'].map(lambda x: x == '-')
    psm['is_prot_cterm'] = psm['Next AA'].map(lambda x: x == '-')

    psm.loc[psm['MSFragger Localization'].isna(), 'MSFragger Localization'] = ''
    psm['MSFragger Localization'] = psm['MSFragger Localization'].astype(str)

    psm['n_matched_pos'] = psm['MSFragger Localization'].map(lambda loc: len(re.findall("[a-z]", loc)))
    psm.query("n_matched_pos <= 1", inplace=True)
    psm = psm.loc[~((psm['n_matched_pos'] == 1) & (psm["Delta Mass"] < dm_mass_tol) &
                    (psm["Delta Mass"] > -dm_mass_tol)), :]

    # psm.query(f" not (n_matched_pos == 1 and (`Delta Mass` < {dm_mass_tol}) and (`Delta Mass` > {-dm_mass_tol}))", inplace=True)

    def localize_mod(loc):
        x = re.search("[a-z]", loc)
        return x.span()[0] if x is not None else -1

    psm['mod_loc_in_peptide'] = psm['MSFragger Localization'].map(localize_mod)

    def get_mod_aa(loc):
        x = re.findall("[a-z]", loc)
        return x[0].upper() if len(x) > 0 else ''

    psm['modAA'] = psm['MSFragger Localization'].map(get_mod_aa)
    psm['Protein Start'] = psm['Protein Start'].astype(int)
    psm['mod_loc_in_protein'] = psm['mod_loc_in_peptide'] + psm['Protein Start']
    psm['is_peptide_nterm'] = psm['mod_loc_in_peptide'] == 0
    psm['is_peptide_cterm'] = (psm['mod_loc_in_peptide'] + 1) == psm['Peptide Length']
    psm['raw_file'] = [s[0:re.search("\.\d+\.\d+\.\d\Z", s).span()[0]] for s in psm.index]

    return psm


def retain_subs_with_basepeptide(psm):
    subs = psm.query('substitution != False and danger == False').copy()
    base_peptide_df = psm.query('substitution == False and danger == False and zero_shift_peptide')
    print(f'\tidentified {base_peptide_df.shape[0]} base peptides')

    def is_in(x, base_df):
        return base_df.loc[(base_df["Protein"] == x.Protein) & (base_df["raw_file"] == x.raw_file) &
                           (base_df["Protein Start"] < x.mod_loc_in_protein) &
                           (base_df["Protein End"] > x.mod_loc_in_protein), :].shape[0] > 0

        # return base_df.query(f"Protein == '{x.Protein}' and raw_file == '{x.raw_file}' and "
        #                     f"`Protein Start` < {x.mod_loc_in_protein} and "
        #                     f"`Protein End` > {x.mod_loc_in_protein}").shape[0] > 0

    subs['base_peptide_exists'] = subs.apply(lambda row: is_in(row, base_peptide_df), axis=1)
    return subs.query('base_peptide_exists')


def fetch_substituted_codon(row, cds_dict):
    mod_loc = row.mod_loc_in_protein
    prot = row.Protein

    codon = 'NaN'
    if (not row.is_decoy) & (prot in cds_dict.keys()):
        sequence = cds_dict[prot]
        codon_seq = codonify(sequence.seq)
        codon = codon_seq[mod_loc - 1]

    return codon


def run(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="fasta", required=True,
                        help="search database as codon fasta file", metavar="FILE",
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-psm", dest="psm", required=True,
                        help="psm.tsv produced by philisopher", metavar="FILE")
    parser.add_argument("-o", dest="output_folder", required=True,
                        help="Output folder", metavar="FILE",
                        type=lambda x: prep_folder(x))
    parser.add_argument("-decoy", dest="decoy", required=False,
                        help="decoy prefix (default: rev_)", default="rev_")
    parser.add_argument("-p", dest="prefix", required=False,
                        help="prefix for experiment naming", default='substitutions')
    parser.add_argument("-tol", dest="tol", required=False,
                        help="m/z tolerance, used to filter DP–BP couples that resemble substitutions "
                             "and exclude pairs that resemble known PTM", default=0.005, type=float)
    parser.add_argument("-TEST", dest="test", required=False,
                        help="For testing only: use only <X> files", default=-1)
    args = parser.parse_args(args)

    print("Setup")
    tic_total = time.perf_counter()

    ntest_files = int(args.test)
    TESTING = ntest_files > -1

    print("\n\n\n")
    print("--------------------------------------------------------------------")
    print(f"fasta database file: {args.fasta}")
    print(f"psm file: {args.psm}")
    print(f"decoy prefix: {args.decoy}")
    print(f"Output folder: {args.output_folder}")
    print(f"Output file prefix: {args.prefix}")
    print(f"M/Z tolerance: {args.tol}")
    print("--------------------------------------------------------------------")

    # to be set via command line arguments
    delta_mass_tolerance = args.tol  # 0.005
    cds_file = args.fasta  #
    psm_file = args.psm  # 'input/PXD025934_fragpipe/pepXML'
    output_folder = args.output_folder  # 'output/PXD025934_fragpipe/'
    decoy_prefix = args.decoy
    output_prefix = args.prefix

    ms_diff_dict = get_mass_substitution_dict()
    codons = get_codons()
    amino_acids = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'  # corresponds to codons
    codon_table = dict(zip(codons, amino_acids))
    inverted_codon_table = invert_codon_table(codon_table)
    inverted_codon_table['L'] = inverted_codon_table['L'] + inverted_codon_table['I']

    print("Reading sequences")
    tic = time.perf_counter()
    cds_dict = SeqIO.to_dict(SeqIO.parse(cds_file, 'fasta'))
    toc = time.perf_counter()
    print(f"\tfinished in {toc - tic:0.4f} seconds")
    print(f"\t# of sequences in database: {len(cds_dict)}")

    print('Reading and preparing PSM file')
    tic = time.perf_counter()
    psm_df = pd.read_csv(psm_file, sep='\t', index_col=0)
    psm_df = prepare(psm_df, dm_mass_tol=delta_mass_tolerance, decoy=decoy_prefix, cds_names=cds_dict.keys())
    toc = time.perf_counter()
    print(f"\tfinished in {toc - tic:0.4f} seconds")

    print('Finishing up substitution detection')
    tic = time.perf_counter()
    p = Path(__file__).with_name('danger_mods.csv')
    danger_mods = pd.read_csv(p)  # pd.read_csv('atplab_workflow/danger_mods.csv') #

    print("\tMark dangerous PTMs")
    psm_df = mark_danger_mods(psm_df, danger_mods, mass_tol=delta_mass_tolerance)
    psm_df = mark_substitutions(psm_df, ms_diff_dict, delta_mass_tolerance)
    psm_subs = retain_subs_with_basepeptide(psm_df)
    # psm_subs['found_elsewhere'] = psm_subs['modified_peptide'].map(lambda x: peptide_in_proteome(x, cds_dict))

    near_cognate_mask = define_near_cognate_mask(codons, amino_acids, inverted_codon_table)

    psm_subs['codon'] = psm_subs.apply(lambda row: fetch_substituted_codon(row, cds_dict), axis=1)
    psm_subs['origin'] = psm_subs['substitution'].map(lambda x: x.split(' ')[0])
    psm_subs['destination'] = psm_subs['substitution'].map(lambda x: x.split(' ')[2])
    psm_subs['near_cognate'] = psm_subs.apply(lambda row: near_cognate_mask.loc[row['codon'], row['destination']],
                                              axis=1)

    psm_subs = psm_subs[['Protein', 'Peptide', 'raw_file', 'MSFragger Localization', 'Prev AA', 'Next AA',
                         'PeptideProphet Probability', 'Delta Mass', 'Protein Start', 'Protein End',
                         'mod_loc_in_protein', 'codon', 'origin', 'destination', 'substitution', 'near_cognate']]

    psm_subs.rename(columns={'raw_file': 'Rawfile', 'MSFragger Localization': 'Modified_Peptide', 'Prev AA': 'Prev_AA',
                             'Next AA': 'Next_AA', 'PeptideProphet Probability': 'PeptideProphet_Probability',
                             'Delta Mass': 'Delta_Mass', 'Protein Start': 'Protein_Start', 'Protein End': 'Protein_End',
                             'mod_loc_in_protein': 'Localization_in_Protein'}, inplace=True)

    psm_subs = psm_subs.astype({'Protein': str, 'Peptide': str, 'Rawfile': str, 'Modified_Peptide': str, 'Prev_AA': str,
                                'Next_AA': str, 'PeptideProphet_Probability': float, 'Delta_Mass': float,
                                'Protein_Start': int, 'Protein_End': int, 'Localization_in_Protein': int, 'codon': str,
                                'origin': str, 'destination': str, 'substitution': str, 'near_cognate': bool})

    toc = time.perf_counter()
    print(f"\tfinished in {toc - tic:0.4f} seconds")
    print(f"\tDetected {psm_subs.shape[0]} substitutions")

    print('Calculating Protein and Peptide error rates')
    tic = time.perf_counter()
    # peptide count
    psm_pc = pd.DataFrame.from_dict(clt.Counter(psm_df['Protein']), orient='index')
    psm_zs_pc = pd.DataFrame.from_dict(clt.Counter(psm_df.loc[psm_df['zero_shift_peptide'], 'Protein']), orient='index')
    psm_subs_pc = pd.DataFrame.from_dict(clt.Counter(psm_subs['Protein']), orient='index')
    psm_pc = psm_pc.join(psm_zs_pc, lsuffix='Total', rsuffix='zero_shift')
    psm_pc = psm_pc.join(psm_subs_pc, lsuffix='Total', rsuffix='subs')
    psm_pc['Error_rate'] = psm_pc[0] / psm_pc['0Total']
    psm_pc['ZS_Error_rate'] = psm_pc[0] / psm_pc['0zero_shift']
    psm_pc = psm_pc.reset_index()
    psm_pc.fillna(0, inplace=True)
    psm_pc.columns = ['Protein', 'Total', 'No_Mass_Shift', 'Erroneous', 'Total_Error_Rate', 'No_Mass_Shift_Error_Rate']

    # codon counting
    base_codon_count = count_observed_codons(psm_df.query('zero_shift_peptide'), cds_dict)
    basepeptide_codon_count = pd.DataFrame.from_dict(base_codon_count, orient='index')
    subs_codon_count = pd.DataFrame.from_dict(clt.Counter(psm_subs['codon']), orient='index')
    total_codon_count = basepeptide_codon_count.join(subs_codon_count, lsuffix='base', rsuffix='substitution')
    total_codon_count['total'] = total_codon_count['0base'] + total_codon_count['0substitution']
    total_codon_count['error_rate'] = total_codon_count['0substitution'] / total_codon_count['total']
    total_codon_count = total_codon_count.reset_index()
    total_codon_count.fillna(0, inplace=True)
    total_codon_count.columns = ['codon', 'base_count', 'error_count', 'total_count', 'detection_rate']
    psm_cc = total_codon_count.astype({'codon': str, 'base_count': int, 'error_count': int, 'total_count': int,
                                       'detection_rate': float})
    toc = time.perf_counter()
    print(f"\tfinished in {toc - tic:0.4f} seconds")

    psm_subs.to_csv(os.path.join(output_folder, output_prefix + '_substitution_errors.csv'))
    psm_cc.to_csv(os.path.join(output_folder, output_prefix + '_codon_counts.csv'))
    psm_pc.to_csv(os.path.join(output_folder, output_prefix + '_peptide_counts.csv'))

    toc_total = time.perf_counter()
    print(f"Analysis finished in {toc_total - tic_total:0.4f} seconds")

