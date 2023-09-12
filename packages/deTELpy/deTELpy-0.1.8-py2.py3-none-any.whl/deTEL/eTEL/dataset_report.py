import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import os
import re
import argparse

fdr = 0.01

#### FUNCTION DEFINITIONS
def plot_codon_counts(cc, f):
    fig, ax1 = plt.subplots(1, 1, figsize=(10, 6))
    ax1.bar(cc.index, cc['total_count'])
    ax1.set_ylabel('Codon count', fontweight='bold')
    ax1.set_xlabel('Codons', fontweight='bold')
    ax1.set_xticklabels(cc.index, rotation=90)
    ax2 = ax1.twinx()
    ax2.plot(cc.index, cc['error_count'] / cc['total_count'], color='k',
             linestyle='dashed')
    ax2.plot(cc.index, cc['error_count'] / cc['total_count'], color='k', marker='o')
    ax2.set_ylabel('Error rate', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f + '/1.png', format='png')


def plot_peptide_hist(pc, f):
    fig, ax1 = plt.subplots(1, 1, figsize=(7, 5))
    ax1.hist(pc['errorfree_peptide'], bins=100, histtype="stepfilled", alpha=0.8)
    ax1.set_xlabel('Error free peptides per protein', fontweight='bold')
    ax1.set_ylabel('Frequency', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f + '/2.png', format='png')


def plot_hyperscore_distribution(psm, f):
    psm.sort_values('hyperscore', ascending=False, inplace=True)
    psm = psm.assign(is_decoy=psm['protein'].map(lambda x: re.search(r'rev_', x) is not None))
    ratio = np.array([i / float(j) for i, j in zip(psm['is_decoy'].cumsum(), range(1, len(psm.index) + 1))])

    if np.min(ratio) < fdr:
        cut_off = np.max(np.where(ratio < fdr))
        hyperscore_th = np.array(psm['hyperscore'])[cut_off]

    psm_real = psm.query('is_decoy == False')
    psm_decoy = psm.query('is_decoy == True')

    fig, ax1 = plt.subplots(1, 1, figsize=(7, 5))
    x = ax1.hist(psm_real['hyperscore'], bins=100, histtype="stepfilled", alpha=0.8, density=False, label='Identified')
    ax1.hist(psm_decoy['hyperscore'], bins=x[1], histtype="stepfilled", alpha=0.8, density=False, label='Decoys')
    ax1.set_xlabel('Hyperscore', fontweight='bold')
    ax1.set_ylabel('Density', fontweight='bold')
    if np.min(ratio) < fdr:
        ax1.axvline(hyperscore_th, color='k', linestyle='dashed')
    ax1.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(f + '/3.png', format='png')


parser = argparse.ArgumentParser()
parser.add_argument("-f", dest="rawfile_folder", required=True,
                    help="rawfile folder name", metavar="FILE")
parser.add_argument("-b", dest="base_folder", required=True,
                    help="base folder name", metavar="FILE")
parser.add_argument("-s", dest="search_res_dir", required=True,
                    help="search result dir", metavar="FILE")
parser.add_argument("-o", dest="output_folder", required=True,
                    help="Output folder", metavar="FILE")

args = parser.parse_args()

print("\n\n\n")
print("--------------------------------------------------------------------")
print(f"base_folder: {args.base_folder}")
print(f"rawfile_folder: {args.rawfile_folder}")
print(f"search_res_dir_folder: {args.search_res_dir}")
print(f"Output folder: {args.output_folder}")


#### FILENAMES AND STUFF
# 'yeast_results_ionquant/PXD014119'
infolder = os.path.join(args.output_folder, args.rawfile_folder)
cf = '_'.join([infolder, 'codon_counts.csv'])
pf = '_'.join([infolder, 'peptide_counts.csv'])

tsv_folder = os.path.join(args.base_folder, args.rawfile_folder, args.search_res_dir, 'tsv')
out_folder = os.path.join(args.output_folder, 'report', args.rawfile_folder)

image_out_folder = os.path.join(args.output_folder, 'report/images', args.rawfile_folder)

os.makedirs(image_out_folder, exist_ok=True)

print(f"infolder: {infolder}")
print(f"cf: {cf}")
print(f"pf: {pf}")
print(f"tsv_folder: {tsv_folder}")

print("--------------------------------------------------------------------")

# after detection of substitution
codon_counts = pd.read_csv(cf, sep=',', header=0, index_col=0, usecols=['Codon', 'total_count', 'error_count'])
plot_codon_counts(codon_counts, image_out_folder)

peptide_counts = pd.read_csv(pf, sep=',', header=0, index_col=0)
plot_peptide_hist(peptide_counts, image_out_folder)

# after open search
tsv_files = [os.path.join(tsv_folder, f) for f in os.listdir(tsv_folder) if
             os.path.isfile(os.path.join(tsv_folder, f)) and ('.tsv' in f)]
psm_data = pd.DataFrame()
for tsvf in tsv_files:
    tmp_base = pd.read_csv(tsvf, sep='\t', header=0, usecols=['protein', 'retention_time', 'hyperscore'])
    psm_data = pd.concat([psm_data, tmp_base])
plot_hyperscore_distribution(psm_data, image_out_folder)



