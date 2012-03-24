# wod.py
"""
Library that gets and sets the WOD data
"""

from google.appengine.ext import db
import urllib2
from datetime import datetime
from BeautifulSoup import BeautifulSoup

import logging
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
    date = datetime.strptime(date,'%B %d, %Y').date()

    # only 1 wod for the day so grab first element from soup
    # then slice to avoid first 3 list elements
    # (the WOD header tag and the date)
    wodlst = soup('a',{'href':'blog/category/wod'})[0].findAll(text=True)[4:]

    # make a string of of wod parts list
    wod = ''
    for line in wodlst:
        wod += line

    logging.info('Wod is %s', date)
    # wods are unique by date, so if we don't
    # have this wod_date then add the wod
    if not WOD.gql("WHERE wod_date=:date", date=date).get():
        WOD(wod=wod,wod_date=date).put()

