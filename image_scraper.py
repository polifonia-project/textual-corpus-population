import argparse
import urllib.request
from os import listdir

import requests
from bs4 import BeautifulSoup


def get_documents(url: str):
    """

    Takes the url of the 'Emeroteca digitale italiana' and returns the list of parsed link to download.

    :param url: the base url of a journal on 'Emeroteca digitale italiana'
    :return: a list of links, each of which is the
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id='js-navigator')
    documents = results.find_all('li', class_='js-time')
    document_links = [document.find('a', href=True)['href'].split('?')[-1].split('&')[0]
                      for document in documents if 'showPeriodic=true' in document.find('a', href=True)['href']]
    return document_links


def download_images(image_link: str, start_resource_url: str, end_resource_url: str, base_path: str = ''):
    """

    Takes the url of an image and downloads it into a specific directory.

    :param image_link: the url of the image to download
    :param start_resource_url: the start url of the download page of the resource
    :param end_resource_url: the start url of the download page of the resource
    :param base_path: the path where to save the downloaded image
    """
    image_url = f'{start_resource_url}{image_link}{end_resource_url}'
    for page in range(1000):
        # print(image_link)
        file_name = f'{base_path}/{image_link.split("%3")[-1][3:]}-{page+1}.jpeg'
        if file_name.split('/')[-1] not in [f for f in listdir(base_path)]:
            try:
                image_composed_url = image_url + str(page + 1)
                file = urllib.request.urlopen(image_composed_url)
                size = file.headers.get('content-length')
                if int(size) > 100:
                    with open(file_name, "wb") as f:
                        f.write(requests.get(image_composed_url).content)
                        print(f'SAVED FILE AS: {file_name}')
                else:
                    break
            except:
                print(f'ERROR ENCOUNTERED WHILE HANDLING THE FILE: {image_link}')
                pass
        else:
            print(f'FILE ALREADY IN DIRECTORY, SKIPPING: {file_name}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--resource_url',
                        type=str,
                        default='https://www.internetculturale.it/it/913/emeroteca-digitale-italiana/periodic/testata'
                                '/8670')
    parser.add_argument('--img_path_start',
                        type=str,
                        default='http://www.internetculturale.it/jmms/objdownload?')
    parser.add_argument('--img_path_end',
                        type=str,
                        default='&teca=Casa%20della%20musica%20di%20Parma&resource=img&mode=raw&start=0&offset=')
    parser.add_argument('--output_path',
                        type=str,
                        default='/Volumes/MUST/OCR/Arpa')

    args = parser.parse_args()

    links = get_documents(args.resource_url)
    for link in links:
        download_images(link, args.img_path_start, args.img_path_end, args.output_path)
