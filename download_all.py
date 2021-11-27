from image_scraper import *
import argparse
import os


def get_search_result(search_url: str):
    resources = []
    titles = []
    for pag_num in range(1000):
        pag_url = search_url + str(pag_num)
        page = requests.get(pag_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = [x for x in soup.find_all(class_='block-item-search-result')]
        if len(results) > 0:
            titles.append([r.find(class_='block-item-text').find(class_='block-title dc_title').text.strip() for r in results])
            resources.append([r.find(class_='block-item-img').find('a')['href'] for r in results])
        else:
            break
    return titles, resources


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
        # print(image_link)
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
    parser.add_argument('--output_path', type=str, default='/Users/andreapoltronieri/PycharmProjects/image_scraper')

    args = parser.parse_args()

    title, all_music = get_search_result(args.search_url)
    for i, resource_page in enumerate(all_music):
        for i2, music_resource in enumerate(resource_page):
            path = create_path(title[i][i2], args.output_path)
            download_images(music_resource, title[i][i2],
                            'http://www.internetculturale.it/jmms/objdownload?id=oai%3A',
                            '&resource=img&mode=raw&start=0&offset=1',
                            path)

