import os
import time
import json


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['list']


def pride_filter(dataset):
    instrument_names = dataset['instrumentNames']
    return_value = False
    if len(instrument_names) == 1:
        return_value = 'LTQ Orbitrap' in instrument_names[0]

    return return_value


dict_list = load_json('pride/s_cerevisiae.json') # load json created with prideCrawler.py
filtered_pride_ids = [dataset['accession'] for dataset in dict_list] # get pride IDs, filter if needed, only basic filter for testing implemented but any filter can be build here
filtered_ftp_url = [dataset['_links']['datasetFtpUrl']['href'] for dataset in dict_list] # get needed ftp link

# download files and store them in correct directory. Each file will be placed in a directory named after the PRIDE id
for url, id in zip(filtered_ftp_url, filtered_pride_ids):
    if not os.path.isdir(id):
        os.system(f'mkdir {id}')
    os.system(f'cd {id}')
    os.system(f'wget "{url}/*.raw"')
    os.system('cd ..')
    time.sleep(1)
