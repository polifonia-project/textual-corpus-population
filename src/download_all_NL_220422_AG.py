import os
import requests

TIMEOUT = 20

download_path = '/Users/arianna/Desktop/Polifonia/WP4/D4_2/prove_download/delpher_books_nl_300922_5/'

from_tsv_to_crawling = []
with open("from_tsv_to_crawling_input.tsv") as file:
  for line in file:
    l=line.split('\t')
    from_tsv_to_crawling.append(l)

for persistent_url in from_tsv_to_crawling:
    resource_id = persistent_url[0].replace(':', '_')
    download_url = None
    if 'dbnl' in resource_id:
        persistent_url_dbnl = persistent_url[0].split("=")[-1].split('_')[-1]
        download_url = 'https://www.dbnl.org/tekst/' + persistent_url_dbnl + '_01' + '/' + persistent_url_dbnl + '_01.pdf'
    else:
        download_url = persistent_url[1][:-1]
    if download_url:
        if f'{resource_id}.pdf' in os.listdir(download_path):
            print(f'FILE ALREADY IN DIRECTORY, SKIPPING {download_url}')
            print(True)
            pass
        else:
            try:
                file = requests.get(download_url, timeout=TIMEOUT)
                print(f'DOWNLOADING RESOURCE {resource_id}.pdf')
                pdf = open(f'{download_path}/{resource_id}.pdf', 'wb')
                pdf.write(file.content)
                pdf.close()
                print(True)
            except requests.exceptions.ReadTimeout:
                print(f'DOWNLOAD FAILED, NOT DOWNLOADED {resource_id}.pdf')
                print(False)
                pass
