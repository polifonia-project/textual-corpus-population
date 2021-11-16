import urllib.request

import requests
from bs4 import BeautifulSoup
from os import listdir

PATH: str = 'https://www.internetculturale.it/it/913/emeroteca-digitale-italiana/periodic/testata/8660'

IMG_PATH_START: str = 'http://www.internetculturale.it/jmms/objdownload?'
IMG_PATH_END: str = '&teca=Casa%20della%20musica%20di%20Parma&resource=img&mode=raw&start=0&offset='  # no offset number

OUTPUT_PATH: str = 'IlTrovatore'


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
        file_name = f'{base_path}/{image_link.split("ADB")[1]}-{page+1}.jpeg'
        if file_name.split('/')[1] not in [f for f in listdir(base_path)]:
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
    links = get_documents(PATH)
    for link in links:
        download_images(link, IMG_PATH_START, IMG_PATH_END, OUTPUT_PATH)
