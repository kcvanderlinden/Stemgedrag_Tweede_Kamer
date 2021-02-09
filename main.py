#A new beginning, let the behaviour be known
#Libraries
from bs4 import BeautifulSoup
import requests
import html
import pandas as pd
#import csv
#from datetime import datetime
import re
import wget
import PyPDF2
import os

# This is initially where the pages are being loaded.
def url():
    url = "https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2021Z01484&did=2021D03367"
    # url = 'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2021Z02214&did=2021D04897'
    rall = requests.get(url)
    r = rall.content
    soup = BeautifulSoup(r, "html")
    return soup

# Catching the Vote (if the vote has been casted)
def vote():
    loaded_page = url()
    if loaded_page.find('h2', class_='section__title') == None:
        data = 'De stemming is niet bekend.'
    else:
        cols = ['Party', 'Count', 'Vote']
        data = pd.DataFrame(columns=cols)
        for strong_tag in loaded_page.find_all('tr'):
            a = strong_tag.span
            if a == None:
                c = strong_tag.th.text
            else:
                b = strong_tag.select('td > span')[1].text
                data = data.append({'Party': a.text, 'Count': int(b), 'Vote': c}, ignore_index=True)
    return data

# Catching information of the motion and of the persons who drew or supported the motion
def page_info():
    inf = url().find_all('div', class_="link-list__item")
    date = inf[-3]('div', class_='link-list__text')[0].text
    doc_number = inf[-2]('div', class_='link-list__text')[0].text
    state_doc = inf[-1]('div', class_='link-list__text')[0].text
    cnt_ondertekenaars = len(inf) - 3
    for i in range(0, cnt_ondertekenaars):
        headline = inf[i].select('div > strong')[0].text
        name = inf[i].select('div > a')[0].text
        pol_party = inf[i].select('div > a')[1].text
    return headline, name, pol_party, date, doc_number, state_doc

def read_pdf_motion():
    loaded_page = url()
    pdf_url = 'https://www.tweedekamer.nl/' + loaded_page('a', class_='button ___rounded ___download')[0]['href']
    reader = PyPDF2.PdfFileReader(wget.download(pdf_url, 'downloaded_motie.pdf'))
    pdf_text = reader.getPage(0).extractText()
    t_begin = pdf_text.find('De Kamer,')
    ending_note = 'en gaat over tot de orde van de dag.'
    t_end = pdf_text.find(ending_note)
    only_text = pdf_text[t_begin:t_end] + ending_note
    only_text = only_text.replace('\n', '')
    os.remove("downloaded_motie.pdf")
    return only_text
