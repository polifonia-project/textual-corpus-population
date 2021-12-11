import csv

from internet_culturale_scraper import *
import argparse
import os


def get_search_result(search_url: str):
    ids_entire = []
    ids_splitted = []
    resources = []
    titles = []
    years = []
    authors = []
    for pag_num in range(1):
        pag_url = search_url + str(pag_num)
        page = requests.get(pag_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = [x for x in soup.find_all(class_='block-item-search-result')]
        if len(results) > 0:
            titles.append([r.find(class_='block-item-text').find(class_='block-title dc_title').text.strip() for r in results])
            years.append([r.find(class_='block-item-text').find(class_='dc_issued').text.strip() for r in results])
            resources.append([r.find(class_='block-item-img').find('a')['href'] for r in results])
            authors.append([r.find(class_='block-item-text').find(class_='dc_creator').text.strip() if r.find(class_='block-item-text').find(class_='dc_creator') != None else '' for r in results])
            ids_ = [r.find(class_='block-item-text').find(class_='dc_id').text.strip() if r.find(class_='block-item-text').find(class_='dc_creator') != None else '' for r in results]
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


def download_images(image_link: str, title : str, start_resource_url: str, end_resource_url: str, base_path: str = ''):
    image_link = image_link.replace('&fulltext=1', '')\
        .split('id=oai%3A')[-1].replace('+', '%20')
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # check that the search_url contains the '&pag=' but NOT the page number
    parser.add_argument('--search_url', type=str, default='https://www.internetculturale.it/it/16/search?q=musica&instance=magindice&__meta_typeTipo=testo+a+stampa&__meta_typeLivello=monografia&pag=')
    parser.add_argument('--output_path', type=str, default='/Users/andreapoltronieri/Documents/Polifonia/WP4/OCR')

    args = parser.parse_args()

    ids_entire, ids_splitted, titles, years, authors, resources = get_search_result(args.search_url)
    with open(args.output_path+'/books_metadata.tsv', 'w') as fw:
    #with open('books_metadata.tsv', 'w') as fw:
        writer = csv.writer(fw, delimiter='\t')
        writer.writerow(['id_entire', 'id_splitted', 'author', 'title', 'year'])
        for i, resource_page in enumerate(resources):
            for i2, music_resource in enumerate(resource_page):
                id_entire = ids_entire[i][i2]
                id_splitted = ids_splitted[i][i2]
                title = titles[i][i2]
                year = years[i][i2]
                author = authors[i][i2]
                resource = resources[i][i2]
                writer.writerow([id_entire, id_splitted, author, title, year])
                path = create_path(id_splitted, args.output_path)
                #path = create_path('',id_splitted)
                download_images(music_resource, title,
                                'http://www.internetculturale.it/jmms/objdownload?id=oai%3A',
                                '&resource=img&mode=raw&start=0&offset=1',
                                path)
