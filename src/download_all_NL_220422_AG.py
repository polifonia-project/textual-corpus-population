import argparse
import csv
import os
import urllib
from os import listdir

import requests
from bs4 import BeautifulSoup
driver = webdriver.Chrome(ChromeDriverManager().install())

import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

TIMEOUT = 20

search_url_pt1 = 'https://www.delpher.nl/nl/boeken/results?query=muziek&'
search_url_pt2 = '&maxperpage=50&coll=boeken'
download_path = '/Users/arianna/Desktop/Polifonia/WP4/D4_2/prove_download/delpher_books_nl/'

persistent_urls = []

for pag_num in range(954):
    pag_url = search_url_pt1 + str(pag_num) + search_url_pt2
    page = driver.get(pag_url)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    soup_nice = soup.prettify()
    results = [x for x in soup.find_all('article')]
    if len(results) > 0:
        persistent_urls.append([[r['data-identifier'], 'https://resolver.kb.nl/resolve?urn='+r['data-identifier']+':pdf'] for r in results])
        for persistent_url in persistent_urls:
            for n in range(len(persistent_url)):
                resource_id = persistent_url[n][0].replace(':', '_')
                download_url = persistent_url[n][1]
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
                            print(f'DOWNLOAD FAILED, NOT DOWNLOADED {split_id}.pdf')
                            print(False)
                            pass
                if n >= 3:
                    break
