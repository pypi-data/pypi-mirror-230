from datetime import date

import os
import re
import json
import time
import math

import pandas as pd
import requests


def pride_filter(dataset):
    instrument_names = dataset['instruments']
    return_value = False
    if len(instrument_names) == 1:
        return_value = 'LTQ Orbitrap' in instrument_names[0]

    return return_value


# updated to work with new PRIDE API
def get_species_sets(species, outfile=None, removeMultiSpecies=False):
    time.sleep(0.5)
    url = f"https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?filter=organisms%3D%3D{species}"
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError('Wrong responds from website: ' + str(r.status_code))
        return None

    data = json.loads(r.content)
    saved_data = data['_embedded']['compactprojects']
    npages = data['page']['totalPages']
    print(f'number of pages: {npages}')
    print(f'finished page 1')
    pageurl = data['_links']['self']['href']
    for i in range(1, npages):
        current_url = re.sub('page=0', f'page={i}', pageurl, count=0, flags=0)
        r = requests.get(current_url)
        data = json.loads(r.content)
        saved_data += data['_embedded']['compactprojects']
        print(f'finished page {i+1}')

    if removeMultiSpecies:
        saved_data = [sd for sd in saved_data if len(sd['organisms']) == 1]

    if outfile is not None:
        with open(outfile, 'w', encoding='utf-8') as f:
            json.dump(saved_data, f, ensure_ascii=False, indent=4)

    return saved_data


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['list']


# e.g. find all datasets that contain 'sapiens' and store in json for future use
dict_list = get_species_sets('sapiens', 'h_sapiens.json',
                             removeMultiSpecies=True)

###### get number of potential datasets ##########
# Just examples if one is interested how many potential datasets are present per ...
#r = requests.get('https://www.ebi.ac.uk/pride/ws/archive/v2/stats/SUBMISSIONS_PER_ORGANISM')
#r = requests.get('https://www.ebi.ac.uk/pride/ws/archive/v2/stats/SUBMISSIONS_PER_DISEASES')
r = requests.get('https://www.ebi.ac.uk/pride/ws/archive/v2/stats/SUBMISSIONS_PER_INSTRUMENT')
data = json.loads(r.content)
df = pd.DataFrame(index=range(len(data)), columns=['Disease', 'nDatasets'])
for i, d in enumerate(data):
    df.iloc[i] = [d["key"], d["value"]]
df.to_csv('ndata_per_instrument_' + str(date.today()) + '.csv', index=False)

# in case you already created a json
#dict_list = load_json('h_sapiens.json')
# estimate storage space needed, likely an over estimate since only *.raw files will be downloaded but other formats are also considered 'RAW' by PRIDE
filtered_pride_ids = [dataset['accession'] for dataset in dict_list] # you could filter datasets here
nraw_files = []
for id in filtered_pride_ids:
    r = requests.get(f'https://www.ebi.ac.uk/pride/ws/archive/v2/files/byProject?accession={id}')
    if r.status_code != 200:
        continue
    data = json.loads(r.content)
    nraw_files.append(sum([d['fileSizeBytes'] * 1e-12 for d in data if d['fileCategory']['value'] == 'RAW']))
    time.sleep(0.5)

print(f'Estimated storage space required (TB): {math.ceil(sum(nraw_files))}')


