import json

import argparse
import os

from jinja2 import Environment, FileSystemLoader

import spectrum_utils.iplot as sup
import spectrum_utils.spectrum as sus


def replacer(s, newstring, index, nofail=False):
    # raise an error if index is outside of the string
    if not nofail and index not in range(len(s)):
        raise ValueError("index outside given string")

    # if not erroring, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return newstring + s
    if index > len(s):  # add it to the end
        return s + newstring

    # insert the new string between "slices" of the original
    return s[:index] + newstring + s[index + 1:]


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

os.chdir(report_folder)

# Opening JSON file
f = open(dataset_name + '_peptides.js')

# returns JSON object as
# a dictionary
data = json.load(f)

# Closing file
f.close()

sus.static_modification('C', 57.021464)
peptides = []

# Iterating through the json
# list
for row in data:
    rawfile_name = row['rawfile_name']

    peak_list = row['peak_list']
    retention_time = row['retention_time']
    precursor_mz = row['precursor_mass']
    precursor_charge = row['precursor_charge']

    peptide, modifications = row['peptide'], {}
    spectrum_data = sus.MsmsSpectrum('Modified', precursor_mz, precursor_charge,
                                       [x[0] for x in peak_list],
                                       [x[1] for x in peak_list],
                                       peptide=peptide,
                                       retention_time=retention_time,
                                       modifications=modifications)

    org = row['origin']
    dest = row['destination']
    loc = row['mod_loc']

    peptide = replacer(peptide, f'[{org}\u279D{dest}]', loc)

    chart = (sup.spectrum(spectrum_data.annotate_peptide_fragments(0.5, 'Da', ion_types='by'))
             .properties(width=640, height=400, title=peptide))

    jsonSpec = chart.to_json()

    outputFile = dataset_name + '_' + rawfile_name + '_' + str(row['scan_number'])
    peptides.append({'rawfile_name': rawfile_name, 'outputFile': outputFile,
                     'scanNo': row['scan_number'], 'peptide': row['peptide'],
                     'jsonSpec': jsonSpec})


# Clean up
os.remove(f'{os.getcwd()}/{dataset_name}_peptides.js')

# HTML Template creation
file_loader = FileSystemLoader('/workflow/templates')
env = Environment(loader=file_loader)
template = env.get_template('substitution_report.html')
output = template.render(raw_folder=dataset_name, peptides=peptides)

html_file = open(f'{out_folder}.html', 'w')
html_file.write(output)
html_file.close()
