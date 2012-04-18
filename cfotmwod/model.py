# wod.py
"""
Library that gets and sets the WOD data
"""

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models as auth_models

from datetime import datetime
from BeautifulSoup import BeautifulSoup

import logging
class WOD(ndb.Model):
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    wod_date = ndb.DateProperty(required=True)
    wod = ndb.TextProperty()

class OTMUser(auth_models.User):
    email = ndb.StringProperty()

def get_wod():
    # other urlfetch options
    # http://code.google.com/appengine/docs/python/urlfetch/overview.html
    url = "http://www.crossfitonthemove.com/"
    soup = BeautifulSoup(urlfetch.fetch(url, headers={'Cache-Control' : 'max-age=300'}).content)

    # get our date
    # if there is more then one date, parser needs updating
    date = soup("p",{"class":"date"})[0].text
    date = datetime.strptime(date,'%B %d, %Y').date()

    # wod with tags
    wod = soup.find("div",{"id":"content"}).find("div",{"class":"right"})
    wodlst = wod.findAll(lambda tag: tag.name=="p" and not tag.attrs)

    # make a string of of wod parts list
    wod = ''
    for line in wodlst:
        wod += line.prettify().replace('\xc2\xa0',' ').\
                               replace('\xc3\x97',' x ').\
                               replace('\xe2\x80\x9d','"')

    logging.debug('Wod is %s', date)
    logging.debug('Wod is %s', wod)
    # wods are unique by date, so if we don't
    # have this wod_date then add the wod

    # check the cache
    cache_key = date.strftime('%Y%m%d')
    cached = memcache.get(cache_key)

    if not cached:
        logging.debug('Wod is not cached')
        # add to the cache
        memcache.add(key=cache_key, value=wod, time=60*60*24) # store for a day

        # pull from data store to ensure it
        # wasn't just cleared from cache
        current_wod = WOD.query(WOD.wod_date==date).get()
        if not current_wod:
            # add the new wod
            WOD(wod=db.Text(wod),wod_date=date).put()
            memcache.delete(key='wods')
        else:
            # see if the wod has changed
            if current_wod.wod != wod:
                # update the wod to the new value
                current_wod.wod = db.Text(wod)
                current_wod.put()
                memcache.delete(key='wods')
    else:
        logging.debug('Wod is cached')
        # verify cached value is same as new
        if cached != wod:
            logging.debug('Going to update Wod as it has changed')
            # update the wod to the new value
            current_wod = WOD.query(WOD.wod_date==date).get()
            # should never not have a current wod
            # since its cached, but just in case
            if current_wod:
                current_wod.wod = db.Text(wod)
                current_wod.put()
            else:
                logging.debug('Cached, but not...')
                WOD(wod=db.Text(wod),wod_date=date).put()

            # update the cache
            memcache.set(key=cache_key, value=wod, time=60*60*24) # store for a day
            # we made a wod change so we need to remove the wods collection cache
            memcache.delete(key='wods')
