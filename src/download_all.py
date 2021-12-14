import argparse
import csv
import os
import urllib
from os import listdir

import requests
from bs4 import BeautifulSoup

TIMEOUT = 20


def get_search_result(search_url: str):
    ids_entire = []
    ids_splitted = []
    resources = []
    titles = []
    years = []
    authors = []
    print('\nRETRIEVING SEARCH RESULTS...\n')
    for pag_num in range(1000):
        pag_url = search_url + str(pag_num)
        page = requests.get(pag_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = [x for x in soup.find_all(class_='block-item-search-result')]
        if len(results) > 0:
            titles.append([r.find(class_='block-item-text').find(class_='block-title dc_title').text.strip() for r in results])
            years.append([r.find(class_='block-item-text').find(class_='dc_issued').text.strip() for r in results])
            resources.append([r.find(class_='block-item-img').find('a')['href'] for r in results])
            authors.append([r.find(class_='block-item-text').find(class_='dc_creator').text.strip() if r.find(class_='block-item-text').find(class_='dc_creator') is not None else '' for r in results])
            ids_ = [r.find(class_='block-item-text').find(class_='dc_id').text.strip() if r.find(class_='block-item-text').find(class_='dc_id').text.strip() is not None else '' for r in results]
            ids_entire.append(ids_)
            ids__ = []
            for id_ in ids_:
                if '\\\\' in id_:
                    id_ = id_.split('\\\\')[-1]
                else:
                    id_ = id_.split(':')[-1]
                ids__.append(id_)
            ids_splitted.append(ids__)
        else:
            break
    return [ids_entire, ids_splitted, titles, years, authors, resources]


def create_path(title, base_path):
    title = title.replace(' ', '_').replace('/', '-')
    try:
        os.makedirs(f"{base_path}/{title}")
    except FileExistsError:
        pass
    return f"{base_path}/{title}"


def download_images(image_link: str, start_resource_url: str, end_resource_url: str, base_path: str = ''):
    image_link = image_link.replace('&fulltext=1', '').split('id=oai%3A')[-1].replace('+', '%20')
    base_url = f'{start_resource_url}{image_link}{end_resource_url}'
    image_url = base_url.split('case=')[0] + 'teca=' + base_url.split('Level2')[1]

    for page in range(1000):
        file_name = f'{base_path}/{base_path.split("/")[-1]}_{page}.jpeg'

        if file_name.split('/')[-1] not in [f for f in listdir(base_path)]:
            try:
                image_composed_url = image_url[:-1] + str(page + 1)
                file = urllib.request.urlopen(image_composed_url)
                size = file.headers.get('content-length')
                if int(size) > 100:
                    with open(file_name, "wb") as f:
                        f.write(requests.get(image_composed_url).content)
                        print(f'SAVED FILE AS: {file_name}')
                else:
                    break
            except:
                print(f'ERROR ENCOUNTERED WHILE HANDLING THE FILE: {image_url}')
                pass
        else:
            print(f'FILE ALREADY IN DIRECTORY, SKIPPING: {file_name}')


def download_pdf(resource_id, split_id, download_path):
    resource_id = resource_id.replace('oai:', '').replace(':', '%3A').replace('/', '%2F').replace('\\', '%5C')
    download_url = None
    if 'bncf' in resource_id:
        download_url = f'http://www.internetculturale.it/jmms/objdownload?id=oai%3A{resource_id}&teca=Bncf&resource=img&mode=all'
    elif 'internetculturale.sbn' in resource_id:
        download_url = f'http://www.internetculturale.it/jmms/objdownload?id=oai%3A{resource_id}&teca=MagTeca%20-%20ICCU&resource=img&mode=all'
    elif 'braidense' in resource_id:
        download_url = f'http://www.internetculturale.it/jmms/objdownload?id=oai%3A{resource_id}&teca=Braidense&resource=img&mode=all'
    else:
        print('RESOURCE NOT MAPPED', resource_id)

    if download_url:
        if f'{split_id}.pdf' in os.listdir(download_path):
            print(f'FILE ALREADY IN DIRECTORY, SKIPPING {download_url}')
            return True
            pass
        else:
            try:
                file = requests.get(download_url, timeout=TIMEOUT)
                print(f'DOWNLOADING RESOURCE {split_id}.pdf')
                pdf = open(f'{download_path}/{split_id}.pdf', 'wb')
                pdf.write(file.content)
                pdf.close()
                return True
            except requests.exceptions.ReadTimeout:
                print(f'DOWNLOAD FAILED, NOT DOWNLOADED {split_id}.pdf')
                return False
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # check that the search_url contains the '&pag=' but NOT the page number
    parser.add_argument('--search_url', type=str, default='https://www.internetculturale.it/it/16/search?q=musica&instance=magindice&__meta_typeTipo=testo+a+stampa&__meta_typeLivello=monografia&pag=1')
    parser.add_argument('--output_path', type=str, default='/Users/andreapoltronieri/Documents/Polifonia/WP4/')

    args = parser.parse_args()

    ids_entire, ids_splitted, titles, years, authors, resources = get_search_result(args.search_url)

    with open(f'{args.output_path}/books_metadata.tsv', 'w') as fw:
        writer = csv.writer(fw, delimiter='\t')
        writer.writerow(['id_entire', 'id_splitted', 'author', 'title', 'year', 'downloaded'])
        for i, resource_page in enumerate(resources):
            for i2, music_resource in enumerate(resource_page):
                id_entire = ids_entire[i][i2]
                id_splitted = ids_splitted[i][i2]
                title = titles[i][i2]
                year = years[i][i2]
                author = authors[i][i2]
                resource = resources[i][i2]
                downloaded = download_pdf(id_entire, id_splitted, args.output_path)
                writer.writerow([id_entire, id_splitted, author, title, year, downloaded])
