#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class User(db.Model):
	first_name = db.StringProperty()
	last_name = db.StringProperty()
	inscription = db.DateProperty()
	active = db.BooleanProperty()
	facebookToken = db.StringProperty(required=True)
	uid = db.IntegerProperty(required=True)
	email = db.EmailProperty()

class Component(db.Model):
	name = db.StringProperty(required=True)
	stock = db.IntegerProperty(required=True)
	Step = db.IntegerProperty(required=True)

class favoritOrder(db.Model):
	name = db.StringProperty(required=True)
	ingredient = db.ListProperty(db.Key)
	nbVote = db.IntegerProperty()

class CurrentOrder(db.Model)

