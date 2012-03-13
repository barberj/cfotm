# wod.py
"""
Library that gets and sets the WOD data
"""
import logging

from google.appengine.ext import db

import urllib2
from datetime import datetime
from BeautifulSoup import BeautifulSoup

class WOD(db.Model):

    created_at = db.DateTimeProperty(auto_now_add=True)
    wod_date = db.DateProperty(required=True)
    wod = db.StringProperty(multiline=True)

def get():
    # other urlfetch options
    # http://code.google.com/appengine/docs/python/urlfetch/overview.html
    url = "http://www.crossfitonthemove.com/"
    soup = BeautifulSoup(urllib2.urlopen(url))

    # get our date
    # if there is more then one date, parser needs updating
    date = soup("p",{"class":"date"})[0].text

    # only 1 wod for the day
    wod_soup = soup('a',{'href':'blog/category/wod'})[0]

    # the actual exercises are in
    # paragraph tags in the wod soup
    wod = ''
    for tag in wod_soup('p'):
        # skip paragraph tags with attributes
        # such as the date class
        if not tag.attrs:
            wod += '%s\n' % tag.prettify()

    return WOD(wod=wod,wod_date=datetime.strptime(date,'%B %d, %Y').date()).put()
