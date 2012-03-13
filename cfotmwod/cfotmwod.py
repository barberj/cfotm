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
import logging
import wod
logging.root.level = logging.DEBUG
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class CronHandler(webapp2.RequestHandler):
    def get(self):
        daily_wod_key = wod.get()
        self.response.out.write('Created wod with key %s' % daily_wod_key.id_or_name())

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainHandler, name='main'),
    webapp2.Route(r'/wod/get', handler=CronHandler, name='tasks'),
], debug=True)
