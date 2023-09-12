import matplotlib
matplotlib.use('Agg')

import pandas as pd
import json

import argparse
import os

import ms_deisotope

parser = argparse.ArgumentParser()
parser.add_argument("-b", dest="base_folder", required=True,
                    help="base folder name", metavar="FILE")
parser.add_argument("-f", dest="rawfile_folder", required=True,
                    help="rawfile folder name", metavar="FILE")
parser.add_argument("-o", dest="output_folder", required=True,
                    help="Output folder", metavar="FILE")

args = parser.parse_args()

print("\n")
print("--------------------------------------------------------------------")
print(f"base_folder: {args.base_folder}")
print(f"rawfile_folder: {args.rawfile_folder}")
print(f"Output folder: {args.output_folder}")

report_folder = os.path.join(args.output_folder, 'report')
out_folder = os.path.join(args.output_folder, 'report', args.rawfile_folder)
dataset_name = args.rawfile_folder
rawfile_folder = os.path.join(args.base_folder, args.rawfile_folder)
substitution_error_file = os.path.join(args.output_folder, args.rawfile_folder + '_substitution_errors.csv')

peptides = []

psm = pd.read_csv(substitution_error_file)
os.chdir(report_folder)

groupedByRawfile = psm.groupby("Raw_file")
for name, group in groupedByRawfile:
    rawfile_name = str(name)
    print('\n')
    print(rawfile_name + '.raw')
    raw_file = os.path.join(args.base_folder, args.rawfile_folder, rawfile_name + '.raw')
    reader = ms_deisotope.MSFileLoader(raw_file)

    for index, row in group.iterrows():
        #         print(row)
        pep = {'rawfile_name': rawfile_name, 'scan_number': row.SCAN_NUM,
               'precursor_mass': row.calc_neutral_pep_mass, 'precursor_charge': row.charge,
               'retention_time': row.retention_time, 'origin': row.origin, 'destination': row.destination,
               'peptide': row.modified_peptide, 'best_locs': row.best_locs,
               'mod_loc': row.mod_loc, 'peptide_length': row.peptideLength}
        print(pep)

        scan = reader.get_scan_by_id(row.SCAN_NUM)
        scan.pick_peaks()
        peak_list = []
        for peak in scan.peak_set.peaks:
            peak_list.append([peak.mz, peak.intensity])

        pep['peak_list'] = peak_list
        peptides.append(pep)

f = open(dataset_name + "_peptides.js", "w")
f.write(json.dumps(peptides))
f.close()

