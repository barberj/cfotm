# wod.py
"""
Library that gets and sets the WOD data
"""
import logging

import requests
from datetime import datetime
from BeautifulSoup import BeautifulSoup

def get():
    url = "http://www.crossfitonthemove.com/"
    soup = BeautifulSoup(requests.get(url).content)

    # get our date
    # if there is more then one date, parser needs updating
    date = soup("p",{"class":"date"})[0].text

    # only 1 wod for the day
    # JUST WOD TEXT
    # only 1 wod for the day so grab first element from soup
    # then slice to avoid first 3 list elements
    # (the WOD header tag and the date)
    wodlst = soup('a',{'href':'blog/category/wod'})[0].findAll(text=True)[4:]

    # wod with tags
    wod = soup.find("div",{"id":"content"}).find("div",{"class":"right"})
    wodlst = wod.findAll(lambda tag: tag.name=="p" and not tag.attrs)

    # the actual exercises are in
    # paragraph tags in the wod soup
    wod = ''
    for line in wodlst:
        # skip paragraph tags with attributes
        # such as the date class
        wod += line.prettify()

    print wod
