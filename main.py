# A new beginning, let the behaviour be known
from bs4 import BeautifulSoup
import requests
import pandas as pd
# import csv
import re
import wget
import PyPDF2
import os

# Start up script to create an initial empty database with headings
cols = ['Subject', 'Date', 'Names_Supporters', 'char_supporters', 'Parties', 'Vote', 'Text', 'Title', 'Document_Number',
        'State_Document', 'Personal_Info_Page']
database = pd.DataFrame(columns=cols)
database.to_csv('Database.csv', index=False)


# This is initially where the pages are being loaded.
def ind_page(sub_url, database):
    url = 'https://www.tweedekamer.nl' + sub_url
    # url = 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2021Z0221j4&did=2021D04897'
    rall = requests.get(url)
    r = rall.content
    loaded_page = BeautifulSoup(r, "lxml")

    # Catching the Vote (if the vote has been casted)
    if loaded_page.find('table', class_='vote-result-table') is None:
        vote_list = 'De stemming is niet bekend.'
    else:
        tables = loaded_page.find_all('table', class_='vote-result-table')
        vote_list = []
        for table in tables:
            choice = table.th.text
            parties = table.find_all('tr')
            for party in parties[1::]:
                party_name = party.select('td')[0].text
                count_vote = 0
                if len(party.select('td')) > 1:
                    count_vote = int(party.select('td > span')[1].text)
                vote_list.append([party_name.replace('\n', ''), count_vote, choice])

    # Catching information of the motion and of the persons who drew or supported the motion
    supporter_info_0 = loaded_page.find('h2')
    general_info = loaded_page.find('div', class_="col-md-3").find_all('div', class_="link-list__text")
    date = general_info[0].text
    doc_number = general_info[1].text
    state_doc = general_info[2].text
    subject = loaded_page.find('h1', class_='section__title').text
    subject = re.sub(' +', ' ', subject.replace('\n', ''))
    page_title = loaded_page.title.text
    char_supporters, name_supporters, party_supporters, personal_pages = [], [], [], []
    while supporter_info_0.next_sibling.next_sibling is not None:
        supporter_info_0 = supporter_info_0.next_sibling.next_sibling
        char_supporters.append(supporter_info_0.select('div > strong')[0].text)
        supporter_info_1 = supporter_info_0.select('div > a')
        name_supporters.append(supporter_info_1[0].text)
        personal_pages.append('https://www.tweedekamer.nl' + supporter_info_1[0]['href'])
        party_supporters.append(supporter_info_1[1].text)

    # Reading the motion from the PDF. PDF is temporarily downloaded and only the text of the motion is scraped
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

    database = database.append(
        {"Subject": subject, 'Date': date, 'Names_Supporters': name_supporters, 'char_supporters': char_supporters,
         'Parties': party_supporters, 'Vote': vote_list, 'Text': motion_text, 'Title': page_title,
         'Document_Number': doc_number, 'State_Document': state_doc, 'Personal_Info_Page': personal_pages}, ignore_index=True)
    return database

# By defining the range (which will eventually account for every list page), the scraping can begin.
def run():
    database = pd.read_csv('Database.csv')
    for i in range(1,7):
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