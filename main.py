# A new beginning, let the behaviour be known
from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import re
import wget
import PyPDF2
import os

# Start up script to create an initial empty database with headings
cols = ['Subject', 'Date', 'Names_Supporters', 'char_supporters', 'Parties', 'Vote', 'Text', 'Title', 'Document_Number', 'State_Document']
database = pd.DataFrame(columns=cols)
database.to_csv('Database.csv', index=False)


# This is initially where the pages are being loaded.
def ind_page(sub_url, database):
    url = 'https://www.tweedekamer.nl' + sub_url
    #url = 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2021Z0221j4&did=2021D04897'
    rall = requests.get(url)
    r = rall.content
    loaded_page = BeautifulSoup(r, "lxml")

    # Catching the Vote (if the vote has been casted)
    if loaded_page.find('h2', class_='section__title') == None:
        vote_list = 'De stemming is niet bekend.'
    else:
        vote_list = []
        for strong_tag in loaded_page.find_all('tr'):
            party = strong_tag.span
            if party == None:
                voted_what = strong_tag.th.text
            else:
                vote_count = strong_tag.select('td > span')[1].text
                vote_list.append([party.text, int(vote_count), voted_what])

    # Catching information of the motion and of the persons who drew or supported the motion
    inf = loaded_page.find('h2')
    gen_info = loaded_page.find('div', class_="col-md-3").find_all('div', class_="link-list__text")
    date = gen_info[0].text
    doc_number = gen_info[1].text
    state_doc = gen_info[2].text
    subject = loaded_page.find('h1', class_='section__title').text
    subject = re.sub(' +', ' ', subject.replace('\n', ''))
    page_title = loaded_page.title.text
    char_supporters = []
    name_supporters = []
    party_supporters = []
    while inf.next_sibling.next_sibling != None:
        inf = inf.next_sibling.next_sibling
        char_supporters.append(inf.select('div > strong')[0].text)
        name_supporters.append(inf.select('div > a')[0].text)
        party_supporters.append(inf.select('div > a')[1].text)
    #for i in range(0, cnt_ondertekenaars):
    #    print(subject)
    #    char_supporters.append(inf[i].select('div > strong')[0].text)
    #    name_supporters.append(inf[i].select('div > a')[0].text)
    #    party_supporters.append(inf[i].select('div > a')[1].text)

    sub_url_pdf = loaded_page('a', class_='button ___rounded ___download')[0]['href']
    if sub_url_pdf[-3::] == 'pdf':
        pdf_url = 'https://www.tweedekamer.nl/' + sub_url_pdf
        reader = PyPDF2.PdfFileReader(wget.download(pdf_url, 'downloaded_motie.pdf'))
        pdf_text = reader.getPage(0).extractText()
        t_begin = pdf_text.find('De Kamer,')
        ending_note = 'en gaat over tot de orde van de dag.'
        t_end = pdf_text.find(ending_note)
        motion_text = pdf_text[t_begin:t_end] + ending_note
        motion_text = motion_text.replace('\n', '')
        os.remove("downloaded_motie.pdf")
    else:
        motion_text = 'Het document is geen PDF-formaat'

    # database = pd.read_csv('Database.csv')
    database = database.append(
        {"Subject": subject, 'Date': date, 'Names_Supporters': name_supporters, 'char_supporters': char_supporters,
         'Parties': party_supporters, 'Vote': vote_list, 'Text': motion_text, 'Title': page_title,
         'Document_Number': doc_number, 'State_Document': state_doc}, ignore_index=True)
    # database.to_csv('Database.csv', index=False)
    return database

# By defining the range (which will eventually account for every list page), the scraping can begin.
def run():
    database = pd.read_csv('Database.csv')
    for i in range(1,3):
        print('This is page {}'.format(i))
        url = 'https://www.tweedekamer.nl/kamerstukken/moties?qry=*&fld_prl_kamerstuk=Moties&fld_tk_categorie=kamerstukken&srt=date%3Adesc%3Adate&page='+str(i)
        rall = requests.get(url)
        r = rall.content
        soup = BeautifulSoup(r,"lxml")
        for x in soup.select('h3 > a'):
            sub_url = x['href']
            database = ind_page(sub_url, database)
    database.to_csv('Database.csv', index=False)
    return print('\n ready steady')