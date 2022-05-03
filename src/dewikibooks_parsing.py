from bs4 import BeautifulSoup

xmlfile = r'/Users/arianna/Desktop/Polifonia/WP4/D4_2/dewikibooks/dewikibooks-20220420-pages-articles-multistream.xml'
with open(xmlfile) as xmlFile:
    fileContent = BeautifulSoup(xmlFile, "lxml")

dicts = {}
count = 0
for page in fileContent.find_all("page"):
    count += 1
    if not page.find("text").contents == None:
        text_content = str(page.find("text").contents)
        if "Musik" in text_content:
            dicts[f'Dict{count}'] = {}
            print(page.find("id").contents, "done")
            if not page.find("id").contents == None:
                dicts[f'Dict{count}']["id"] = page.find("id").contents
            else:
                pass
            if not page.find("title").contents == None:
                dicts[f'Dict{count}']["title"] = page.find("title").contents
            else:
                pass
            if not page.find("text").contents == None:
                dicts[f'Dict{count}']["text"] = page.find("text").contents
            else:
                pass
            #dicts[f'Dict{count}']["title"] = page.find("title").contents
            #dicts[f'Dict{count}']["ns"] = page.find("ns").contents
            #dicts[f'Dict{count}']["parentid"] = page.find("parentid").contents
            #dicts[f'Dict{count}']["timestamp"] = page.find("timestamp").contents
            #dicts[f'Dict{count}']["contributor_username"] = page.find("username").contents
            #dicts[f'Dict{count}']["comment"] = page.find("comment").contents
            #dicts[f'Dict{count}']["model"] = page.find("model").contents
            #dicts[f'Dict{count}']["format"] = page.find("format").contents
            #dicts[f'Dict{count}']["text"] = page.find("text").contents
        else:
            print(page.find("id").contents, "not done")
    else:
        pass

with open('dewikibooks_music.tsv', 'w', newline='') as tsvfile:
    fieldnames = ['id', 'title', 'text']
    writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for key, value in dicts.items():
        writer.writerow(value)







    if "Musik" in text_content:
        dicts[f'Dict{count}'] = {}
        dicts[f'Dict{count}']["id"] = page.find("id").contents
        dicts[f'Dict{count}']["title"] = page.find("title").contents
        dicts[f'Dict{count}']["ns"] = page.find("ns").contents
        dicts[f'Dict{count}']["parentid"] = page.find("parentid").contents
        dicts[f'Dict{count}']["timestamp"] = page.find("timestamp").contents
        dicts[f'Dict{count}']["contributor_username"] = page.find("username").contents
        dicts[f'Dict{count}']["comment"] = page.find("comment").contents
        dicts[f'Dict{count}']["model"] = page.find("model").contents
        dicts[f'Dict{count}']["format"] = page.find("format").contents
        dicts[f'Dict{count}']["text"] = page.find("text").contents
        print(page.find("id").contents, "done")
    else:
        print(page.find("id").contents, "not done")





            print(page.find("text").contents[0])
        dicts[f'Dict{count}'] = {}
    if 'Musik' in page.find("text").contents:
        print("True")

        dicts[f'Dict{count}']["id"] = page.find("id").contents
        dicts[f'Dict{count}']["title"] = page.find("title").contents
        dicts[f'Dict{count}']["ns"] = page.find("ns").contents
        dicts[f'Dict{count}']["parentid"] = page.find("parentid").contents
        dicts[f'Dict{count}']["timestamp"] = page.find("timestamp").contents
        dicts[f'Dict{count}']["contributor_username"] = page.find("username").contents
        dicts[f'Dict{count}']["comment"] = page.find("comment").contents
        dicts[f'Dict{count}']["model"] = page.find("model").contents
        dicts[f'Dict{count}']["format"] = page.find("format").contents
        dicts[f'Dict{count}']["text"] = page.find("text").contents





        dicts[f'Dict{count}']["text"] = page.find("text".contents)
        id.append(page.find("id").contents)
        id.append(page.find("id").contents)
        parentid.append(page.find("parentid").contents)
        timestamp.append(page.find("timestamp").contents)
        contributor_username.append(page.find("contributor").contents)
    for text in page.find_all("text"):
        text.append(text.contents)
        count += 1
        if count <= 1:
            print(result)











'''
xmlfile = r'/Users/arianna/Desktop/Polifonia/WP4/D4_2/dewikibooks/dewikibooks-20220420-pages-articles-multistream.xml'
root = etree.parse(xmlfile).getroot()'''









'''
for child in root:
    for page in child.findall("page"):
        print(etree.dump(page))

class Node():
    @staticmethod
    def childTexts(node):
        texts={}
        for child in list(node):
            texts[child.tag]=child.text
        return texts

for node in root.xpath('//page'):
    texts = Node.childTexts(node)
    print(texts)

xmlfile = r'/Users/arianna/Desktop/Polifonia/WP4/D4_2/dewikibooks/dewikibooks-20220420-pages-articles-multistream.xml'
root = etree.parse(xmlfile).getroot()

for x in root[1]:
     print(x.tag, x.attrib)

for child in root.xpath(root[1].xpath):
    etree.dump(child)

page_list = []
for page in root.findall("page"):
    print(page)
    #page_list.append(etree.dump(page))


    # empty news dictionary
    news = {}

    # iterate child elements of item
    for child in page:

        # special checking for namespace object content:media
        if child.tag == '{http://search.yahoo.com/mrss/}content':
            news['media'] = child.attrib['url']
        else:
            news[child.tag] = child.text.encode('utf8')

    # append news dictionary to news items list
    newsitems.append(news)

# return news items list
return newsitems


def savetoCSV(newsitems, filename):
    # specifying the fields for csv file
    fields = ['guid', 'title', 'pubDate', 'description', 'link', 'media']

    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(newsitems)


def main():
    # load rss from web to update existing xml file
    loadRSS()

    # parse xml file
    newsitems = parseXML('topnewsfeed.xml')

    # store news items in a csv file
    savetoCSV(newsitems, 'topnews.csv')


if __name__ == "__main__":
    # calling main function
    main()'''