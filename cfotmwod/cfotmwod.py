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
from webapp2_extras import sessions, auth, jinja2

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import datetime
import json

import model
from schema import SignupForm

import logging

def jinja2_factory(app):
    "True ninja method for attaching additional globals/filters to jinja"

    j = jinja2.Jinja2(app)
    j.environment.globals.update({
        'uri_for': webapp2.uri_for,
    })
    return j

class jsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime('%B %d, %Y')
        elif isinstance(obj, db.Model):
            return dict((p, getattr(obj, p))
                        for p in obj.properties())
        else:
            return json.JSONEncoder.default(self,obj)

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(backend="datastore")

    def dispatch(self):
        try:
            super(BaseHandler, self).dispatch()
        finally:
            # Save the session after each request
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth(request=self.request)

    @webapp2.cached_property
    def user(self):
        user = self.auth.get_user_by_session()
        return user

    @webapp2.cached_property
    def user_model(self):
        user_model, timestamp = self.auth.store.user_model.get_by_auth_token(
                self.user['user_id'],
                self.user['token']) if self.user else (None, None)
        return user_model

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(factory=jinja2_factory, app=self.app)

    def render_response(self, _template, **context):
        ctx = {'user': self.user_model}
        ctx.update(context)
        rv = self.jinja2.render_template(_template, **ctx)
        self.response.write(rv)

class SignupHandler(BaseHandler):
    "Serves up a signup form, creates new users"
    def get(self):
        self.render_response("signup.html",
                form=SignupForm(),
                action=self.request.path)

    def post(self):
        form = SignupForm(self.request.POST)
        error = None
        if form.validate():
            success, info = self.auth.store.user_model.create_user(
                "auth:" + form.email.data,
                unique_properties=['email'],
                email= form.password.data,
                password_raw= form.password.data)

            if success:
                self.auth.get_user_by_password("auth:"+form.email.data,
                                                form.password.data)
                return self.redirect_to("login")
            else:
                error = "That email is already in use." if 'email'\
                        in user else "Something has gone horrible wrong."

        if form.errors and not error:
            for field_error in form.errors:
                logging.info(getattr(form,field_error).description)

        self.render_response("signup.html", form=form, error=error)

class ViewWodsHandler(BaseHandler):
    def get(self):

        # check cache
        cached_wods = memcache.get('wods')
        if not cached_wods:
            logging.info('WODs collection not cached')
            # wods aren't in the cache
            # lets go to the datastore
            query = model.WOD.query()
            wods = [w for w in query.order('-wod_date')]
            wods = json.dumps(wods, cls=jsonEncoder)
            # add to cache
            memcache.add('wods',wods)

        # update our headers for returning json
        self.response.headers.add_header('content-type', 'application/json',
                    charset='utf-8')
        return self.response.out.write(cached_wods or wods)

class MainHandler(BaseHandler):
    def get(self):
        return self.response.out.write(template.render('index.html',
                               {}))

class CronHandler(BaseHandler):
    def get(self):
        model.get_wod()
        self.redirect('/')

config = {'webapp2_extras.sessions': {'secret_key': 'zomg-this-key-is-so-secret' }, 'webapp2_extras.auth': {'user_model': model.OTMUser}}

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainHandler, name='main'),
    webapp2.Route(r'/wod/get', handler=CronHandler, name='tasks'),
    webapp2.Route(r'/wods', handler=ViewWodsHandler, name='wods'),
    webapp2.Route(r'/signup', handler=SignupHandler, name='signup'),
], config=config, debug=True)
