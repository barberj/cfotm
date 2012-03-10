# wod.py
"""
Library that gets and sets the WOD data
"""
import logging

import re
import json
import urllib2
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

def soup_line_break(soup_results):
    """
    The soup results have line breaks which we want
    converted to spaces
    """

    line_break_pattern = '<br\s*/*>'

    br = re.compile(line_break_pattern, re.I)

    for result in soup_results:
        for conent in result.contents:
            br.sub(result.content)

    return result

def brs(soup_results):

    out = ''
    for result in soup_results:
        brs = result.findAll('br')
        for br in brs:
            next = br.nextSibling
            if not (next and isinstance(next,NavigableString)):
                continue
            next2 = next.nextSibling
            if next2 and isinstance(next2,Tag) and next2.name == 'br':
                text = str(next).strip()
                if text:
                    out += '\n%s' % text

    print out

def get_wod():
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

    brs(_content)

    print _content
    wod = ''
    for txt in _content:
        wod += '%s\n' % txt.text

    print "On %s the wod is:\n%s" % (date, wod)
    return _content
