import argparse
import csv
import os
import urllib
from os import listdir
import pandas as pd
import csv

import requests
from bs4 import BeautifulSoup
#driver = webdriver.Chrome(ChromeDriverManager().install())

import time
#from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
#driver = webdriver.Chrome(ChromeDriverManager().install())

TIMEOUT = 20

search_url_pt1 = 'https://www.delpher.nl/nl/boeken/results?query=muziek&'
search_url_pt2 = '&maxperpage=50&coll=boeken'
download_path = '/Users/arianna/Desktop/Polifonia/WP4/D4_2/prove_download/delpher_books_nl_290422/'

from_tsv_to_crawling = []
with open("df_for_crawling.tsv") as file:
  for line in file:
    l=line.split('\t')
    from_tsv_to_crawling.append(l)

for persistent_url in from_tsv_to_crawling:
    resource_id = persistent_url[0].replace(':', '_')
    download_url = persistent_url[1]
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
