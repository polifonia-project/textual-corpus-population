from image_scraper import *
import os


def get_search_result(search_url: str):
    resources = []
    titles = []
    for pag_num in range(3):
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


def download_images(image_link: str, start_resource_url: str, end_resource_url: str, base_path: str = ''):
    print(image_link)
    image_link = image_link.replace('&fulltext=1', '')\
        .split('id=oai%3A')[-1].replace('+', '%20')
    image_url = f'{start_resource_url}{image_link}{end_resource_url}'

    for page in range(1000):
        # print(image_link)
        file_name = f'{base_path}/{base_path}_{page}.jpeg'
        if file_name.split('/')[-1] not in [f for f in listdir(base_path)]:
            print(image_url)
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
    # links = get_documents(PATH)
    # for link in links:
    #     download_images(link, IMG_PATH_START, IMG_PATH_END, OUTPUT_PATH)
    title, all_music = get_search_result(SEARCH_PATH)
    for i, resource_page in enumerate(all_music):
        for i2, music_resource in enumerate(resource_page):
            path = create_path(title[i][i2], '/Users/andreapoltronieri/PycharmProjects/image_scraper')
            download_images(music_resource,
                            'http://www.internetculturale.it/jmms/objdownload?id=oai%3A',
                            '&resource=img&mode=raw&start=0&offset=1',
                            path)

# http://www.internetculturale.it/jmms/objdownload?id=oai%3Awww.internetculturale.sbn.it%2FTeca%3A20%3ANT0000%3AN%3AIT%5C%5CICCU%5C%5CCSA%5C%5C0085808&teca=MagTeca+-+ICCU&resource=img&mode=raw&start=0&offset=1
# https://www.internetculturale.it/jmms/iccuviewer/iccu.jsp?id=oai%3Awww.internetculturale.sbn.it%2FTeca%3A20%3ANT0000%3AN%3AIT%5C%5CICCU%5C%5CCSA%5C%5C0085808&mode=all&teca=MagTeca%20-%20ICCU&fulltext=1

# http://www.internetculturale.it/jmms/objdownload?id=oai%3Awww.internetculturale.sbn.it%2FTeca%3A20%3ANT0000%3AN%3AIT%5C%5CICCU%5C%5CUM%5C%5C10041524&teca=MagTeca%20-%20ICCU&resource=img&mode=raw&start=0&offset=1