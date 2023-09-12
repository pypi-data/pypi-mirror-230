from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from Bio import SeqIO, SeqUtils
from scipy import stats

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import collections as clt
import seaborn as sns
import pandas as pd
import numpy as np

import os
import re
import argparse
from jinja2 import Environment, FileSystemLoader

#### FUNCTION DEFINITIONS AND GLOBAL VARIABLES (probably shouldn't have global variables)
aas = list('ACDEFGHIKLMNPQRSTVWY')
aas = [SeqUtils.seq3(aa) for aa in aas]
CODONTABLE = {'ATA': 'Ile', 'ATC': 'Ile', 'ATT': 'Ile', 'ATG': 'Met', 'ACA': 'Thr', 'ACC': 'Thr', 'ACG': 'Thr',
              'ACT': 'Thr', 'AAC': 'Asn', 'AAT': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys', 'AGC': 'Ser', 'AGT': 'Ser',
              'AGA': 'Arg', 'AGG': 'Arg', 'CTA': 'Leu', 'CTC': 'Leu', 'CTG': 'Leu', 'CTT': 'Leu', 'CCA': 'Pro',
              'CCC': 'Pro', 'CCG': 'Pro', 'CCT': 'Pro', 'CAC': 'His', 'CAT': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
              'CGA': 'Arg', 'CGC': 'Arg', 'CGG': 'Arg', 'CGT': 'Arg', 'GTA': 'Val', 'GTC': 'Val', 'GTG': 'Val',
              'GTT': 'Val', 'GCA': 'Ala', 'GCC': 'Ala', 'GCG': 'Ala', 'GCT': 'Ala', 'GAC': 'Asp', 'GAT': 'Asp',
              'GAA': 'Glu', 'GAG': 'Glu', 'GGA': 'Gly', 'GGC': 'Gly', 'GGG': 'Gly', 'GGT': 'Gly', 'TCA': 'Ser',
              'TCC': 'Ser', 'TCG': 'Ser', 'TCT': 'Ser', 'TTC': 'Phe', 'TTT': 'Phe', 'TTA': 'Leu', 'TTG': 'Leu',
              'TAC': 'Tyr', 'TAT': 'Tyr', 'TAA': 'Stop', 'TAG': 'Stop', 'TGC': 'Cys', 'TGT': 'Cys', 'TGA': 'Stop',
              'TGG': 'Trp'}
INV_CODON_TABLE = {'Ile': ['ATA', 'ATC', 'ATT'], 'Met': ['ATG'], 'Thr': ['ACA', 'ACC', 'ACG', 'ACT'],
                   'Asn': ['AAC', 'AAT'], 'Lys': ['AAA', 'AAG'], 'Ser': ['TCT', 'TCC', 'TCA', 'TCG', 'AGC', 'AGT'],
                   'Phe': ['TTT', 'TTC'], 'Arg': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
                   'Leu': ['CTA', 'CTC', 'CTG', 'CTT', 'TTA', 'TTG'], 'Pro': ['CCT', 'CCC', 'CCA', 'CCG'],
                   'His': ['CAT', 'CAC'], 'Gln': ['CAA', 'CAG'], 'Val': ['GTT', 'GTC', 'GTA', 'GTG'],
                   'Ala': ['GCT', 'GCC', 'GCA', 'GCG'], 'Asp': ['GAT', 'GAC'], 'Glu': ['GAA', 'GAG'],
                   'Gly': ['GGT', 'GGC', 'GGA', 'GGG'], 'Tyr': ['TAT', 'TAC'], 'Cys': ['TGC', 'TGT'], 'Trp': ['TGG'],
                   'Stop': ['TGA', 'TAG', 'TAA']}


def get_codons_by_aa():
    codons_by_aa = []
    for aa in aas:
        codons_by_aa = codons_by_aa + INV_CODON_TABLE[aa]

    return codons_by_aa


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def aa_limits(codon_list, ct):
    aas = []
    for c in codon_list:
        aas.append(ct[c])
    cc = dict(clt.Counter(aas))
    cc["Ala"] = 3.5
    cumsum = [0]
    for key, value in cc.items():
        cumsum.append(cumsum[-1] + value)
    cumsum.pop(0)
    del cumsum[-1]
    return cumsum


def read_codon_proteome(filename):
    proteome = list(SeqIO.parse(filename, "fasta"))

    codonified_proteome = clt.defaultdict(list)

    for protein in proteome:
        sequence = str(protein.seq).upper()
        codon_seq = [sequence[i: i+3] for i in range(0, len(sequence), 3)]
        codonified_proteome[protein.id] = codon_seq

    return codonified_proteome


def read_all_substitutions(folder, codon_proteome):
    files = os.listdir(folder)
    sub_files = sorted([os.path.join(folder, s) for s in files if 'errors' in s])
    substitution = pd.DataFrame(None, columns=['protein', 'destination', 'origin', 'codon', 'position_in_protein',
                                               'dataset'])
    for sf in sub_files:
        tmp = pd.read_csv(sf, sep=',', header=0,
                          usecols=['protein', 'destination', 'origin', 'codon', 'position_in_protein'])
        tmp['dataset'] = os.path.basename(sf).split('_')[0]
        substitution = pd.concat([substitution, tmp])

    substitution.dropna(axis=0, inplace=True)
    substitution['length'] = substitution['protein'].map(lambda x: len(codon_proteome[x]))
    substitution.query('length > 0', inplace=True)
    substitution['fractional_pos_in_prot'] = (substitution['position_in_protein'] / substitution[
        'length']) * 100

    return substitution


def read_peptide_counts(folder):
    files = os.listdir(folder)
    count_files = sorted([os.path.join(folder, s) for s in files if 'peptide_counts' in s])
    pep_count = pd.DataFrame(None, columns=['error_peptide', 'errorfree_peptide', 'total_peptide', 'dataset'])
    for cf in count_files:
        pxd_id = list(filter(lambda x: re.search(r'PXD', x), re.split('_|/', cf)))[0]
        tmp = pd.read_csv(cf, sep=',', header=0, index_col=0, usecols=['protein', 'error_peptide', 'errorfree_peptide',
                                                                       'total_peptide'])
        tmp['dataset'] = pxd_id
        pep_count = pd.concat([pep_count, tmp])

    return pep_count


def get_substitution_counts(subs_df):
    aa_substitution_count = pd.DataFrame(0, index=aas, columns=aas, dtype=int)

    codons = []
    for aa in aas:
        codons = codons + INV_CODON_TABLE[aa]

    codon_substitution_count = pd.DataFrame(0, index=codons, columns=aas, dtype=int)

    for row in subs_df.iterrows():
        r = row[1]
        o = SeqUtils.seq3(r['origin'])
        d_one = r['destination']
        if d_one == 'I/L':
            d_one = 'L'
        d = SeqUtils.seq3(d_one)
        aa_substitution_count.at[o, d] += 1
        codon_substitution_count.at[r['codon'], d] += 1

    return aa_substitution_count, codon_substitution_count


def read_substitutions_as_dict(folder, codon_proteome):
    files = os.listdir(folder)
    sub_files = sorted([os.path.join(folder, s) for s in files if 'errors' in s])
    substitution = {}

    for sf in sub_files:
        pxd_id = list(filter(lambda x: re.search(r'PXD', x), re.split('_|/', sf)))[0]
        tmp = pd.read_csv(sf, sep=',', header=0, usecols=['protein', 'destination', 'origin', 'codon',
                                                          'position_in_protein'])
        tmp.dropna(axis=0, inplace=True)
        tmp['length'] = tmp['protein'].map(lambda x: len(codon_proteome[x]))
        tmp.query('length > 0', inplace=True)
        tmp['fractional_pos_in_prot'] = (tmp['position_in_protein'] / tmp['length']) * 100

        substitution[pxd_id] = tmp

    return substitution


def read_codon_counts_as_dict(folder):
    files = os.listdir(folder)
    count_files = sorted([os.path.join(folder, s) for s in files if 'codon_counts' in s])
    codon_counts = {}
    for cf in count_files:
        pxd_id = list(filter(lambda x: re.search(r'PXD', x), re.split('_|/', cf)))[0]
        tmp = pd.read_csv(cf, sep=',', header=0, index_col=0, usecols=['Codon', 'total_count', 'error_count', 'detection_rate'])

        codon_counts[pxd_id] = tmp

    return codon_counts


def get_all_codon_count(cc_dict, subs_dict):
    all_codon_counts = pd.DataFrame(None, columns=['total_count', 'error_count', 'detection_rate'])
    for key in codon_count_dict.keys():
        cc = cc_dict[key]
        sub = subs_dict[key].groupby('codon').count()
        cc['subs'] = sub['protein']
        all_codon_counts = pd.concat([all_codon_counts, cc], axis=0)

    all_codon_counts['Codon'] = all_codon_counts.index
    all_codon_counts['AA'] = all_codon_counts['Codon'].map(lambda x: CODONTABLE[x])
    all_codon_counts['log_detection_rate'] = all_codon_counts['detection_rate'].map(np.log10)
    all_codon_counts.replace([np.inf, -np.inf], np.nan, inplace=True)
    all_codon_counts.dropna(subset=["log_detection_rate"], inplace=True)

    return all_codon_counts


def plot_substitution_identified(all_substitutions, peptide_count, cutoff=0.5, substitution_folder=None,
                                 filtered_folder=None, out_folder=None):

    n_subs = all_substitutions.groupby('dataset').count().loc[:, 'protein']
    n_peptides = peptide_count.groupby('dataset').sum().loc[:, 'total_peptide']

    x = np.array(np.log10(n_peptides))
    y = np.array(np.log10(n_subs))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    keep = np.where(((slope * x + intercept + cutoff) > y) & ((slope * x + intercept - cutoff) < y) & (y > 1))
    fig, axs = plt.subplots(1, 1, figsize=(6, 5))
    axs.scatter(x, y, color='0.25', alpha=0.3)
    axs.scatter(x[keep], y[keep], color='b', alpha=0.3)
    axs.set_xlabel(r'log$_{10}$[Identified peptides]', fontweight='bold')
    axs.set_ylabel(r'log$_{10}$[Identified substitutions]', fontweight='bold')
    axs.annotate(text=r"R$^2$ = {0:0.2f}".format(r_value), xy=(2, 3.2))
    axs.annotate(text=r"y = {0:.1f}x + {1:.1f}".format(slope, intercept), xy=(2, 3))
    axs.annotate(text=r"$\rho$ = {0:.4f}".format(p_value), xy=(2, 2.8))
    axs.axline(xy1=(min(x), slope * min(x) + intercept), slope=slope, color='0.25', linestyle='--')
    axs.axline(xy1=(min(x), slope * min(x) + intercept + cutoff), slope=slope, color='b', linestyle='--', alpha=0.3)
    axs.axline(xy1=(min(x), slope * min(x) + intercept - cutoff), slope=slope, color='b', linestyle='--', alpha=0.3)
    axs.axline(xy1=(min(x), 1), slope=0, color='b', linestyle='--', alpha=0.3)
    fig.tight_layout()
    plt.savefig(image_out_folder + '/global-1.png', format='png')

    # For HongKee: This part is tricky, of course the function should only plot. I took this whole routine from my
    # filtering function which I use to filter my datasets, only keeping what I deem useful.
    # Maybe it should be done separately which requires that we can ensure that the cutoff parameter is not changed
    # between the plot and the copying of files.
    if substitution_folder is not None and filtered_folder is not None:
        # keep only these datasets for fitting
        datasets = np.array(n_subs.index)[keep]
        for d in datasets:
            os.system(f'cp {substitution_folder}/{d}* filtered_folder')


def plot_substitution_pos_hist(all_substitutions, out_folder=None):
    fig, axs = plt.subplots(1, 1, figsize=(6, 5))
    # Ref: https://github.com/mwaskom/seaborn/issues/2652#issuecomment-916114304
    all_substitutions = all_substitutions.reset_index(drop=True)
    g = sns.histplot(data=all_substitutions, x='fractional_pos_in_prot', ax=axs, bins=100, color='0.25')
    g.set_xlabel('Percent Protein Length', fontweight='bold')
    g.set_ylabel('Detected Substitutions', fontweight='bold')
    fig.tight_layout()
    plt.savefig(image_out_folder + '/global-2.png', format='png')


def plot_heatmap(count_array, aabounds=None, colmap="bwr", log=False, include_total=False, out_folder=None):
    if include_total:
        columns = list(count_array.columns) + ["Total"]
    else:
        columns = list(count_array.columns)

    max_val = count_array.max().max()

    total = count_array.sum(axis=1)
    if log:
        total = np.log(total)
        count_array = np.log10(count_array)
        max_val = np.log10(max_val)
        count_array[np.isinf(count_array)] = float('NaN')

    img_data = pd.DataFrame(float('NaN'), index=count_array.index, columns=columns)
    img_data.at[count_array.index, count_array.columns] = count_array

    fig, ax = plt.subplots(figsize=(6.5, 10))
    plt.subplots_adjust(left=0.11, right=0.74, top=0.99, bottom=0.1)
    ima = ax.imshow(img_data, cmap=colmap, aspect='auto', vmax=max_val) #

    if include_total:
        img_data = pd.DataFrame(float('NaN'), index=count_array.index, columns=columns)
        img_data["Total"] = total
        imb = ax.imshow(img_data, cmap="Blues", aspect='auto', vmax=img_data.max().max())

    # Create colorbar
    if include_total:
        axins = inset_axes(ax, width="5%", height="45%", loc='lower left', bbox_to_anchor=(1.13, 0., 1, 1),
                           bbox_transform=ax.transAxes, borderpad=0)
        axins1 = inset_axes(ax, width="5%", height="45%", loc='upper left', bbox_to_anchor=(1.13, 0., 1, 1),
                            bbox_transform=ax.transAxes, borderpad=0)
    else:
        axins1 = inset_axes(ax, width="5%", height="45%", loc='center left', bbox_to_anchor=(1.13, 0., 1, 1),
                            bbox_transform=ax.transAxes, borderpad=0)

    if include_total:
        cbar = ax.figure.colorbar(imb, cax=axins, extend='both')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), weight='bold')

    #ticks = np.linspace(0, np.ceil((10**max_val)/100), 5, endpoint=True)*100
    cbar2 = ax.figure.colorbar(ima, cax=axins1, extend='both')
    plt.setp(cbar2.ax.yaxis.get_ticklabels(), weight='bold')

    xlab = columns
    codons = count_array.index
    ylab = [c.replace('T', 'U') for c in count_array.index]

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(xlab)))
    ax.set_yticks(np.arange(len(ylab)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(xlab, weight='bold')
    ax.set_yticklabels(ylab, weight='bold')

    # put x label on top
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)

    ax.set_xlabel("Destination Amino Acid", weight='bold')
    ax.set_ylabel("Original Codon", weight='bold')

    if aabounds is not None:
        ax.hlines(aabounds, *ax.get_xlim(), color='k')

        # second y-axis with AA labels
        ax1 = ax.twinx()
        ax1.set_ylim(ax.get_ylim())

        y2_tick_pos = [ax.get_ylim()[1]] + aabounds + [ax.get_ylim()[0]]
        y2_tick_pos = [sum(y2_tick_pos[i:i + 2]) / 2 for i in range(len(y2_tick_pos) - 2 + 1)]

        y2lab = unique([CODONTABLE[c] for c in codons])
        ax1.set_yticks(y2_tick_pos)
        ax1.set_yticklabels(y2lab, weight='bold', rotation=0)

        ax1.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)


        ax1.autoscale(False)

    ax.autoscale(False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=90, ha="center", va="top", rotation_mode="default")
    plt.savefig(image_out_folder + '/global-3.png', format='png')


def plot_detection_rate(all_codon_counts, codons_by_aa, aabounds, out_folder=None):
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 12))
    col1 = '#a6cee3'
    col2 = '#b2df8a'
    palette = {'Ala': col1, 'Cys': col2, 'Asp': col1, 'Glu': col2, 'Phe': col1, 'Gly': col2, 'His': col1, 'Ile': col2,
               'Lys': col1, 'Leu': col2, 'Met': col1, 'Asn': col2, 'Pro': col1, 'Gln': col2, 'Arg': col1, 'Ser': col2,
               'Thr': col1, 'Val': col2, 'Trp': col1, 'Tyr': col2}
    all_codon_counts.Codon = all_codon_counts.Codon.map(lambda x: x.replace('T', 'U'))
    codons = codons_by_aa
    codons_by_aa = [c.replace('T', 'U') for c in codons_by_aa]
    g = sns.boxplot(ax=ax, y="Codon", x="log_detection_rate", data=all_codon_counts, saturation=1,
                    order=codons_by_aa, hue='AA', dodge=False, fliersize=0, palette=palette)#'Set3')
    g = sns.stripplot(ax=ax, y="Codon", x="log_detection_rate", data=all_codon_counts, color='0.25',
                      order=codons_by_aa, alpha=0.1)
    g.set_xlabel('log$_{10}$[Error Detection Rate]', fontweight='bold')
    g.set_ylabel('Codon', fontweight='bold')
    plt.legend([], [], frameon=False)

    if aabounds is not None:
        ax.hlines(aabounds, *ax.get_xlim(), color='k')
        # second y-axis with AA labels
        ax1 = ax.twinx()
        ax1.set_ylim(ax.get_ylim())

        y2_tick_pos = [ax.get_ylim()[1]] + aabounds + [ax.get_ylim()[0]]
        y2_tick_pos = [sum(y2_tick_pos[i:i + 2]) / 2 for i in range(len(y2_tick_pos) - 2 + 1)]

        y2lab = unique([CODONTABLE[c] for c in codons])
        ax1.set_yticks(y2_tick_pos)
        ax1.set_yticklabels(y2lab, weight='bold', rotation=0)

        ax1.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)
        ax1.autoscale(False)
    ax.autoscale(False)

    fig.tight_layout()
    plt.savefig(image_out_folder + '/global-4.png', format='png')

def plot_substitutions_detected(subs_dict, out_folder=None):
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 5))
    n_subs_detected = [len(df.index) for df in subs_dict.values()]
    g = sns.histplot(n_subs_detected, log_scale=True, color='0.25')
    g.set_ylabel('Datasets', fontweight='bold')
    g.set_xlabel('Detected Substitutions', fontweight='bold')
    fig.tight_layout()
    plt.savefig(image_out_folder + '/global-5.png', format='png')

parser = argparse.ArgumentParser()
parser.add_argument("-c", dest="cds_file", required=True,
                    help="cds filename", metavar="FILE")
parser.add_argument("-s", dest="substitution_folder", required=True,
                    help="substitution folder", metavar="FILE")

args = parser.parse_args()

print("\n\n\n")
print("--------------------------------------------------------------------")
print(f"cds_file: {args.cds_file}")
print(f"substitution_folder: {args.substitution_folder}")


#### FILENAMES AND STUFF
# substitution_folder = 'yeast_results_ionquant'
# cds_filename = '../fasta/s228c_orf_cds.fasta'
cds_filename = args.cds_file
substitution_folder = args.substitution_folder
out_folder = os.path.join(args.substitution_folder, 'report')
image_out_folder = os.path.join(out_folder, "images/global")

os.makedirs(image_out_folder, exist_ok=True)

peptide_count = read_peptide_counts(substitution_folder)
codon_prot = read_codon_proteome(cds_filename)
all_substitutions = read_all_substitutions(substitution_folder, codon_prot)
codon_count_dict = read_codon_counts_as_dict(substitution_folder)
substitution_dict = read_substitutions_as_dict(substitution_folder, codon_prot)

# plots require that all datasets have been processed
plot_substitution_identified(all_substitutions, peptide_count, cutoff=0.5, out_folder=out_folder)
plot_substitution_pos_hist(all_substitutions, out_folder=out_folder)

aa_sub_matrix, codon_sub_matrix = get_substitution_counts(all_substitutions)
aabounds = aa_limits(list(codon_sub_matrix.index), CODONTABLE)
plot_heatmap(codon_sub_matrix, aabounds=aabounds, colmap="Reds", log=True, include_total=False, out_folder=out_folder)

all_cc = get_all_codon_count(codon_count_dict, substitution_dict)
codons_by_aa = get_codons_by_aa()
plot_detection_rate(all_cc, codons_by_aa, aabounds, out_folder=out_folder)

plot_substitutions_detected(substitution_dict, out_folder=out_folder)

### HTML Report
lines = []
with open(out_folder + '/report_items.txt') as f:
    lines = f.readlines()

rawfiles = []
for line in lines:
    rawfiles.append({'name': line.rstrip("\n")})

# HTML Template creation
file_loader = FileSystemLoader('/workflow/templates')
env = Environment(loader=file_loader)
template = env.get_template('report.html')
output = template.render(pxds=rawfiles)

# Create results HTML file
html_file = open(out_folder + '/index.html', 'w')
html_file.write(output)
html_file.close()

