import argparse
from os import listdir

import requests
from bs4 import BeautifulSoup


def get_pdf_list(url: str, out_path: str):
    """

    Takes the url of the 'Hemeroteca Digital' and returns the list of parsed link to download.

    :param url: the base url of a journal on 'Hemeroteca Digital'
    :param out_path: the local path in which to save the downloaded resources
    :return: a list of links, each of which is the url to a resource page
    """
    for num in range(1000):
        page = requests.get(f"{url.split('&s=')[0]}&s={str(num * 10)}&lang=es")
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find_all(class_='list-record')
        if page.status_code != 500 and len([x.find('p').text.strip() for x in results]) != 0:
            print(f'SCRAPING RESULTS PAGE {num + 1}')
            # print(f"{url.split('&s=')[0]}&s={str(num * 10)}&lang=es")
            results = soup.find_all(class_='list-record')
            for result in results:
                title = result.find('p').text.strip()
                link = result.find('a', href=True)['href']
                link_id = f"http://hemerotecadigital.bne.es/{link.split('id.')[-1].split('&amp;')[0]}"
                res_page = requests.get(link_id)
                res_soup = BeautifulSoup(res_page.content, 'html.parser')
                res_res = res_soup.find(id='page')['src']
                res_id = link.split('?id=')[-1].split('&search')[0]
                res_rev = res_res.split('/')[-1]
                res_date = title.split('. ')[1].split('. ')[0].split(', n.º ')[0].replace('/', '-')
                try:
                    res_num = f"%2C+n.%C2%BA+{title.split('). ')[1].split('. (')[0].split(', n.º ')[1]}"
                except IndexError:
                    res_num = ''
                download_link = f'http://hemerotecadigital.bne.es/pdf.raw?query=parent%3A{res_id}+type%3Apress%2Fpage&name={res_rev}.+{res_date}{res_num}'
                if res_num != '' and f'{res_date}_{res_num.replace("%2C+n.%C2%BA+", "")}.pdf'in [f for f in listdir(out_path)]:
                    print('FILE ALREADY IN DIRECTORY, SKIPPING ', f'{out_path}/{res_date}_{res_num.replace("%2C+n.%C2%BA+", "")}.pdf' if res_num != '' else f'{out_path}/{res_date}.pdf')
                    pass
                elif res_num == '' and f'{res_date}.pdf' in [f for f in listdir(out_path)]:
                    print('FILE ALREADY IN DIRECTORY, SKIPPING ',
                          f'{out_path}/{res_date}.pdf' if res_num != '' else f'{out_path}/{res_date}.pdf')
                    pass
                else:
                    print(f'DOWNLOADING RESOURCE: {download_link}')
                    file = requests.get(download_link)
                    pdf = open(f'{out_path}/{res_date}_{res_num.replace("%2C+n.%C2%BA+", "")}.pdf' if res_num != '' else f'{out_path}/{res_date}.pdf', 'wb')
                    print('FILE SAVED AS: ', f'{out_path}/{res_date}_{res_num.replace("%2C+n.%C2%BA+", "")}.pdf' if res_num != '' else f'{out_path}/{res_date}.pdf')
                    pdf.write(file.content)
                    pdf.close()
        else:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads resources from "Hemeroteca DIgital".')

    parser.add_argument('--resource_url',
                        type=str,
                        help='the url of a resource page on "Hemeroteca Digital" (e.g. "http://hemerotecadigital.bne.es/results.vm?q=parent%3A0003894964&s=0&lang=es"',)
    parser.add_argument('--output_path',
                        type=str,
                        help='the existing path in with to save the downloaded resource')

    args = parser.parse_args()

    get_pdf_list(args.resource_url, args.output_path)
