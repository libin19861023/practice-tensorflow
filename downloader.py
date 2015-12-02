#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup as bs4
from nltk.tokenize import RegexpTokenizer

BASE_URL = "http://www.imsdb.com/scripts/%s.html"

movies = [
    "Star Wars: A New Hope", # 1997
    "Star Wars: The Empire Strikes Back", # 1980
    "Star Wars: Return of the Jedi", # 1983
    "Star Wars: The Phantom Menace", # 1999
    "Star Wars: Attack of the Clones", # 2002
    "Star Wars: Revenge of the Sith", # 2005
]

punctuation_remover = RegexpTokenizer(r'\w+')

def clean_text(text):
    return " ".join(text.strip().lower().split())

for movie in movies[5:6]:
    url = BASE_URL % "-".join(punctuation_remover.tokenize(movie))
    print "="*40
    print movie
    print "="*40
    print url
    r = requests.get(url)

    soup = bs4(r.text.replace(u'é', u'e').replace(u'É',u'E').encode('utf-8'))
    text_td = soup.find('td',{'class':'scrtext'})

    # remove useless table
    [t.extract() for t in text_td('table')]

    scripts = []

    if "The Phantom Menace" in movie:
        text = text_td.text
        text = re.sub(r'(?<=.)\n(?=[A-Z0-9\-\. ]+ [:;] )', '\n\n', text)
        text = re.sub(r'(?<=\w)\n(?=\w)', ' ', text)

        elems = re.findall(r'\n[A-Z0-9\-\. ]+ [:;] .*\n', text)
    elif "Revenge of the Sith" in movie:
        text = text_td.text
        text = re.sub(r' : ',': ',text)

        elems = re.findall(r'\n\n[A-Z0-9\-\. ]+ ?[:;] .*\n\n', text)
    else:
        elems = text_td.find_all('b')[3:]

    for b in elems:
        if "The Phantom Menace" in movie:
            texts = b.strip().split(' : ',1)

            if len(texts) == 1:
                texts = b.strip().split(' ; ',1)

            character = texts[0]
            lines = texts[1]

            if character in ['TITLE CARD']:
                continue
        elif "Revenge of the Sith" in movie:
            texts = b.strip().split(': ',1)

            if len(texts) == 1:
                texts = b.strip().split(' ; ',1)

            character = texts[0]
            lines = texts[1]

            if character in ['TITLE CARD']:
                continue
        else:
            t = b.text

            if bool(re.match('^ {37}[^ ].*\n$', t)) and \
                    "A New Hope" in movie:
                pass
            elif bool(re.match('^\t{4}[^\t].*\n$', t)) and \
                    "The Empire Strikes Back" in movie:
                pass
            elif bool(re.match('^\t{4}[^\t].*\n$', t)) and \
                    "Attack of the Clones" in movie:
                pass
            elif bool(re.match('^[^\d+ {4}].*\n$', t.lstrip())) and \
                    "Return of the Jedi" in movie:
                pass
            else:
                continue

            if b.text.strip() in ['END CREDITS OVER STAR FIELD', \
                                'FADE OUT', \
                                'THE END']:
                continue

            character = clean_text(t)
            try:
                lines = clean_text(b.next_sibling.split('\n\n',1)[0])
            except:
                lines = clean_text(b.next_sibling.text.split('\n\n',1)[0])

        scripts.append((character, lines))

    for script in scripts[:10]:
        print script[0], ":", script[1]
    print "..."
    for script in scripts[-10:]:
        print script[0], ":", script[1]