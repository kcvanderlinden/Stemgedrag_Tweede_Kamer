# A new beginning, let the behaviour be known
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import wget
import PyPDF2
import os
from tqdm import tqdm

# if not existent, create empty tables
def create_tables():
    cols = ['motie_id', 'Subject', 'Date', 'Text', 'Title', 'State_Document']
    motie_table = pd.DataFrame(columns=cols)
    motie_table.to_csv('motie_table.csv', index=False)

    cols = ['motie_id', 'name_submitter', 'submitter_type', 'party_submitter', 'personal_page']
    indieners_table = pd.DataFrame(columns=cols)
    indieners_table.to_csv('indieners_table.csv', index=False)

    cols = ['motie_id', 'party_name', 'vote_count', 'vote']
    vote_table = pd.DataFrame(columns=cols)
    vote_table.to_csv('vote_table.csv', index=False)

    cols = ['motie_id', 'activities']
    activities_table = pd.DataFrame(columns=cols)
    activities_table.to_csv('activities_table.csv', index=False)
    return motie_table, indieners_table, vote_table, activities_table

# This is initially where the pages are being loaded.
def ind_page(sub_url, motie_table, indieners_table, vote_table, activities_table):
    url = 'https://www.tweedekamer.nl' + sub_url
    rall = requests.get(url)
    r = rall.content
    loaded_page = BeautifulSoup(r, "lxml")

    # Catching information of the motion and of the persons who drew or supported the motion
    supporter_info_0 = loaded_page.find('h2')
    general_info = loaded_page.find('div', class_="col-md-3").find_all('div', class_="link-list__text")
    date = general_info[0].text
    doc_number = general_info[1].text

    # if the motion, identified by the doc_number, is already in the table, then nothing is appended and the function is ended.
    if doc_number in motie_table.motie_id.values:

        return motie_table, indieners_table, vote_table, activities_table

    state_doc = general_info[2].text
    subject = loaded_page.find('h1', class_='section__title').text
    subject = re.sub(' +', ' ', subject.replace('\n', ''))
    page_title = loaded_page.title.text
    while supporter_info_0.next_sibling.next_sibling is not None:
        supporter_info_0 = supporter_info_0.next_sibling.next_sibling
        supporter_info_1 = supporter_info_0.select('div > a')
        indieners_table = indieners_table.append(
            {'motie_id': doc_number, 'name_submitter': supporter_info_1[0].text, 'submitter_type': supporter_info_0.select('div > strong')[0].text, 'party_submitter': supporter_info_1[1].text, 'personal_page': 'https://www.tweedekamer.nl' + supporter_info_1[0]['href']},
            ignore_index=True)

    # Catching the Vote (if the vote has been casted)
    if loaded_page.find('table', class_='vote-result-table') is None:
        vote_list = 'De stemming is niet bekend.'
    else:
        tables = loaded_page.find_all('table', class_='vote-result-table')
        for table in tables:
            choice = table.th.text
            parties = table.find_all('tr')
            for party in parties[1::]:
                party_name = party.select('td')[0].text
                count_vote = 0
                if len(party.select('td')) > 1:
                    count_vote = int(party.select('td > span')[1].text)
                vote_table = vote_table.append({'motie_id': doc_number, 'party_name': party_name.replace('\n', ''), 'vote_count': count_vote, 'vote': choice}, ignore_index=True)

    # Reading the motion from the PDF. PDF is temporarily downloaded and only the text of the motion is scraped
    sub_url_pdf = loaded_page('a', class_='button ___rounded ___download')[0]['href']
    if sub_url_pdf[-3::] == 'pdf':
        pdf_url = 'https://www.tweedekamer.nl/' + sub_url_pdf
        reader = PyPDF2.PdfFileReader(wget.download(pdf_url, 'downloaded_motie.pdf'))
        pdf_text = reader.getPage(0).extractText()
        t_begin = pdf_text.find('De Kamer')
        ending_note = 'en gaat over tot de orde van de dag.'
        t_end = pdf_text.find(ending_note)
        motion_text = pdf_text[t_begin:t_end] + ending_note
        motion_text = motion_text.replace('\n', '')
        os.remove("downloaded_motie.pdf")
    else:
        motion_text = 'Het document is geen PDF-formaat'

    # Catching de voting and debate activities that are linked to this debate
    if loaded_page.find('h2', string="Activiteiten"):
        cards = loaded_page.find('h2', string="Activiteiten").parent.find_all('a', class_='card ___small')
        if len(cards) > 0:
            for x in cards:
                activities_url = 'https://www.tweedekamer.nl{}'.format(x['href'])
                activities_table = activities_table.append({'motie_id': doc_number, 'activities': activities_url},
                                                           ignore_index=True)

    motie_table = motie_table.append(
        {'motie_id': doc_number, 'Subject': subject, 'Date': date, 'Text': motion_text, 'Title': page_title, 'State_Document': state_doc}, ignore_index=True)
    return motie_table, indieners_table, vote_table, activities_table

# By defining the range (which will eventually account for every list page), the scraping can begin.
def run(begin_page, end_page=None):
    end_page = begin_page + 1 if end_page == None else end_page
    # check if tables exist

    if os.path.isfile('motie_table.csv'):
        motie_table, indieners_table, vote_table,activities_table  = pd.read_csv('motie_table.csv'), pd.read_csv('indieners_table.csv'), pd.read_csv('vote_table.csv'), pd.read_csv('activities_table.csv')
    else:
        motie_table, indieners_table, vote_table, activities_table  = create_tables()

    # loop trough the range set of index pages on tweedekamer.nl/kamerstukken/moties
    for i in tqdm(range(begin_page, end_page)):
        print('This is page {}'.format(i))
        url = 'https://www.tweedekamer.nl/kamerstukken/moties?qry=*&fld_prl_kamerstuk=Moties&fld_tk_categorie=kamerstukken&srt=date%3Adesc%3Adate&page='+str(i)
        rall = requests.get(url)
        r = rall.content
        soup = BeautifulSoup(r,"lxml")
        for x in soup.select('h3 > a'):
            sub_url = x['href']
            motie_table, indieners_table, vote_table, activities_table = ind_page(sub_url, motie_table, indieners_table, vote_table, activities_table)
        # save at the end of each index page
        motie_table.to_csv('motie_table.csv', index=False), indieners_table.to_csv('indieners_table.csv', index=False), vote_table.to_csv('vote_table.csv', index=False), activities_table.to_csv('activities_table.csv', index=False)
    return

run(12)