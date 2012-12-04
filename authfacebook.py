#!/usr/bin/env python
#temporary files with basics functions 

import facebook
import os.path
import wsgiref.handlers
import logging
import urllib2
import entities


#o = entities.Order(name="sauter de porc", nbVote=0)
#        q = entities.Component.all()
#       	q.filter("name = ", "concombre")
#        for p in q.run() :
#	        o.ingredient.append(p.key())
#		o.put()

FACEBOOK_APP_ID = "530821850262515"
FACEBOOK_APP_SECRET = "your app secret"

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api.urlfetch import fetch

class authFacebook(long uid, string ApiKey)
	user = User.get_by_uid(uid)
		if not user:
			graph = facebook.GraphAPI(cookie["access_token"])
			profile = graph.get_object("me")
			user = User(key_name=str(profile["id"]),
						id=str(profile["id"]),
						name=profile["name"])


