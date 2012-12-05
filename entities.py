#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class User(db.Model):
	uid = db.IntegerProperty(required = True)
	api_key = db.StringProperty(required = True)
	access_token = db.StringProperty()
	first_name = db.StringProperty()
	last_name = db.StringProperty()
	active = db.BooleanProperty()

class Component(db.Model):
	name = db.StringProperty(required = True)
	stock = db.IntegerProperty(required = True)
	Step = db.IntegerProperty(required = True)

class favoritOrder(db.Model):
	name = db.StringProperty(required = True)
	ingredient = db.ListProperty(db.Key)
	nbVote = db.IntegerProperty()


