# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import datetime
import simplejson

import wod

import logging

class jsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime('%B %d, %Y')
        elif isinstance(obj, db.Model):
            return dict((p, getattr(obj, p))
                        for p in obj.properties())
        else:
            return simplejson.JSONEncoder.default(self,obj)

class ViewWodsHandler(webapp2.RequestHandler):
    def get(self):

        # check cache
        cached_wods = memcache.get('wods')
        if not cached_wods:
            logging.info('WODs collection not cached')
            # wods aren't in the cache
            # lets go to the datastore
            query = wod.WOD.all()
            wods = [w for w in query.order('-wod_date')]
            wods = simplejson.dumps(wods, cls=jsonEncoder)
            # add to cache
            memcache.add('wods',wods)

        # update our headers for returning json
        self.response.headers.add_header('content-type', 'application/json',
                    charset='utf-8')
        return self.response.out.write(cached_wods or wods)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        return self.response.out.write(template.render('index.html',
                               {}))

class CronHandler(webapp2.RequestHandler):
    def get(self):
        wod.get()
        self.redirect('/')

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainHandler, name='main'),
    webapp2.Route(r'/wod/get', handler=CronHandler, name='tasks'),
    webapp2.Route(r'/wods', handler=ViewWodsHandler, name='wods'),
], debug=True)
