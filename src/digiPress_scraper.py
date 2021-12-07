import requests
from bs4 import BeautifulSoup
import argparse
import os


def scrape_dp(title, base, periodical_id, base_api):
    if not os.path.exists(title):
        os.makedirs(title)
    starting_page = base + "/calendar/newspaper/" + periodical_id
    request = requests.get(starting_page)
    soup = BeautifulSoup(request.text, "html")
    years = [a['href'] for a in soup.findAll('a') if 'calendar/' in a['href']]
    for year in years:
        y = year.split('/')[2]
        if not os.path.exists(title+'/'+y):
            os.makedirs(title+'/'+y)
        year_page = base + year
        request_year = requests.get(year_page)
        soup_year = BeautifulSoup(request_year.text, "html")
        issues = [a['href'] for a in soup_year.findAll('a') if 'calendar/' in a['href']]
        for issue in issues:
            issue_page = base + issue
            issue_page_ = issue_page.split('/')[4:7]
            if not issue_page_[-1].isdigit():
                continue
            issue_date = '-'.join(issue_page_)
            if not os.path.exists(title + '/' + y + '/' + issue_date):
                os.makedirs(title + '/' + y + '/' + issue_date)
            request_issue = requests.get(issue_page)
            soup_issue = BeautifulSoup(request_issue.text, "html")
            pages = [a['href'] for a in soup_issue.findAll('a') if 'issue/' in a['href']]
            for page in list(set(pages)):
                view_page = base + page
                request_view = requests.get(view_page)
                soup_view = BeautifulSoup(request_view.text, "html")
                views = list(set([a['src'] for a in soup_view.findAll('img') if '.' not in a['src']]))
                for view in views:
                    view_id = view.split('/')[2]
                    view_id = '_'.join(view_id.split('_')[:2])
                    if not os.path.exists(title + '/' + y + '/' + issue_date + '/' + view_id + '.jpg'):
                        url = base_api + view_id + '/full/full/0/default.jpg'
                        request = requests.get(url)
                        with open(title + '/' + y + '/' + issue_date + '/' + view_id + '.jpg', 'wb') as fw:
                            fw.write(request.content)
                #    req_img = requests.get(base+view)
                #    soup_img = BeautifulSoup(req_img.text, "html")
                #    meta = [m.get('href') for m in soup_img.findAll('link') if m.get('rel') == ['canonical']]
                    #print(meta)
                    #meta = [m for m in meta if 'image' in m.get('property')]
                    #meta = [m.get('content') for m in meta if 'image' in m.get('property')]
                    #if len(meta) > 0:
                    #    view_id = meta[0].split('/')[-2]
                    #    fname = view_id + '.jpeg'
                    #    if not os.path.exists(title + '/' + y + '/' + issue_date + '/' + fname):
                    #        view_id = view.split('/')[2]
                    #        #view_id = '_'.join(view_id.split('_')[:2])
                    #        url = base_api + view_id + '/full/full/0/default.jpg'
                    #        request = requests.get(url)
                    #        with open(title + '/' + y + '/' + issue_date + '/' + fname, 'wb') as fw:
                    #            fw.write(request.content)


    #start_ = "&startRecord=" + str(start)
    #query = "&query=dc.type%20all%20%22monographie"
    #url = base + start_ + query
    #print(url)
    #try:
    #except:
    #    print('ERROR with the above request - skipped')
    #    continue
    #soup = BeautifulSoup('<xml>' + request.text + '</xml>', "xml")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', type=str, default='/media/4TB/rocco/Polifonia/OCR/DE/BerlinerAllgemeineMusikalischeZeitung')
    parser.add_argument('--base', type=str, default='https://digipress.digitale-sammlungen.de')
    parser.add_argument('--periodical_id', type=str, default='bsbmult00000181')
    parser.add_argument('--base_api', type=str, default='https://api.digitale-sammlungen.de/iiif/image/v2/')

    args = parser.parse_args()
    scrape_dp(args.title, args.base, args.periodical_id, args.base_api)