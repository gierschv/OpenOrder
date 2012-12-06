#!/usr/bin/env python

from google.appengine.ext import db

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
	Step = db.ReferenceProperty(required=True)

class Step(db.Model):
	name = db.StringProperty()
	number = db.IntegerProperty()
	type = db.StringProperty(required = True, choices=set(["one", "multi", "warning"]))

class favoritOrder(db.Model):
	name = db.StringProperty(required=True)
	ingredient = db.ListProperty(db.Key)
	nbVote = db.IntegerProperty()

class Order(db.Model):
	ingredient = db.ListProperty(db.Key)
	dateCommand = db.DateProperty()
	Sold = db.DateProperty()
	User = db.ReferenceProperty(User)

class apiStep():
	def add(self, Name, number, pType):
		s = Step(name=Name, number=number, type=pType)
		s.put()

	def delete(self, stepKey):
		Component.all().ancestor(stepKey).delete()
		db.delete(stepKey)

	def search(self, pName):
		if pName is None:
			return Step.all().fetch(limit=10);
		else:
			q = Step.all()
			return q.filter('name =', pName).get()

	def update(self, name, number, pType, key):
		oStep = db.get(key)
		oStep.name = name
		oStep.number = number
		oStep.step = pType
		oStep.put()

class apiComponent():
	def add(self, Name, Stock, keyStep):
		Component(name = Name, stock = Stock, Step = keyStep).put()

	def delete(self, comKey):
		Component.all().ancestor(comKey).delete()

	def update(self, comKey, Name, Stock, stepKey):
		com = db.get(comKey)
		com.name = Name
		com.stock = Stock
		com.Step = stepKey
		com.put()

	def search(self, pName):
		if pName is None:
			return Component.all().fetch(limit=100);
		else:
			q = Component.all()
			return q.filter('name =', pName).get()
		