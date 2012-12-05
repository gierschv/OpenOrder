#!/usr/bin/env python

import webapp2
from google.appengine.ext import db

import authfacebook

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api/auth', authfacebook.AuthHandler)
], debug = True)
