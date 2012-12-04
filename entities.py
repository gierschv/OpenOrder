#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class User(db.Model):
	first_name = db.StringProperty()
	last_name = db.StringProperty()
	inscription = db.DateProperty()
	active = db.BooleanProperty()
	facebookToken = db.StringProperty()
	Uid = db.IntegerProperty();
	email = db.EmailProperty()

class Component(db.Model):
	name = db.StringProperty()
	stock = db.IntegerProperty()
	Step = db.IntegerProperty()


class Order(db.Model):
	nbVote = db.IntegerProperty()