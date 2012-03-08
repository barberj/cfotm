# wod.py
"""
Library that gets and sets the WOD data
"""
import logging

import json
import urllib2
from BeautifulSoup import BeautifulSoup

url = "http://www.crossfitonthemove.com/"
html = BeautifulSoup(urllib2.urlopen(url)).prettify()
soup = BeautifulSoup(html)

# pull out just the HTML containing the WOD
wod_content = soup.find("div",{"id":"content"}).find("div",{"class":"right"})

# get our date
date_content = wod_content.find("p",{"class":"date"})
date = date_content.text

# make soup again
_content= wod_content.findAll(lambda tag: tag.name=="p" and not tag.attrs)

print _content
wod = ''
for txt in _content:
    wod += txt.text

print "On %s the wod is %s" % (date, wod)
