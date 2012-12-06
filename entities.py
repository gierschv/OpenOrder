#!/usr/bin/env python

from google.appengine.ext import db

#
#	Class User
#

class User(db.Model):
	uid = db.IntegerProperty(required = True)
	api_key = db.StringProperty(required = True)
	access_token = db.StringProperty()
	first_name = db.StringProperty()
	last_name = db.StringProperty()
	active = db.BooleanProperty()

class Step(db.Model):
	name = db.StringProperty()
	number = db.IntegerProperty()
	type = db.StringProperty(required = True, choices=set(["one", "multi", "warning"]))


class Component(db.Model):
	name = db.StringProperty(required = True)
	stock = db.IntegerProperty(required = True)
	prix = db.FloatProperty(required = True)
	Step = db.ReferenceProperty(Step)

class favoritOrder(db.Model):
	name = db.StringProperty(required = True)
	ingredient = db.ListProperty(db.Key)
	nbVote = db.IntegerProperty()
	User = db.ReferenceProperty(User)

class Order(db.Model):
	ingredient = db.ListProperty(db.Key)
	dateCommand = db.DateProperty()
	Sold = db.DateProperty()
	User = db.ReferenceProperty(User)

#
#	Class to get back any kind of entities. request is based on the key, useful with foreign key
#

class apiMain():
	def get(self, key):
		return db.get(key)
#
#	Class apiOrder, use to do operations on the Order entities
#

class apiOrder():
	def add(self, listCom, dateBuy, id):
		O = Order(ingredient=listCom, dateCommand=dateBuy, User=User.get_by_id(id).key())
		O.put()

	def search():
		pass

	def getCurrentOrder(self, pLimit):
		q = Order.all()
		return q.filter('Sold =', None).order('-dateCommand').fetch(limit=pLimit)

	def getUserOrder(self, id, pLimit):
		q = Order.all()
		return q.filter('User =', User.get_by_id(id).key()).order('-dateCommand').fetch(limit = pLimit)

	def getUserfavOrder(self, id, pLimit):
		q = favoritOrder.all()
		return q.filter('User =', User.get_by_id(id).key()).order('-nbVote').fetch(limit = pLimit)

	def delete(self, ):
		O = db.get(key)
		O.delete()
	
	def update(self, ingredient, idOrder, dateSoldOut, idUser):
		O = Order.get_by_id(idOrder)
		O.ingredient = ingredient
		O.Sold = dateSoldOut
		O.User = User().get_by_id(idUser).key()
		O.put()

#
#	Class apiFavoriteOder, manage operation on users favortie Order
#	Link are made on User and Component
#

class apifavoriteOrder():
	def add(self, listCom, nbVote, idUser, pname):
		O = FavOrder(ingredient=listCom, nbVote=nbVote, User=User.get_by_id(idUser).key(), name=pname)
		O.put()

	def search():
		pass

	def delete(self, id):
		O = FavOrder.get_by_id(id)
		O.delete()
	
	def update(self, ingredient, idFav, pName, pNbVote, idUser):
		O = FavOrder.get_by_id(idFav)
		O.ingredient = ingredient
		O.name = pName
		O.User = User.get_by_id(idUser).key()
		O.nbVote = pNbVote
		O.put()

#
#	Class Api Step, Step are managed by this class, BEWARE with delete when the function 
#	is called all the component linked with are dropped.
#

class apiStep():
	def add(self, Name, number, pType):
		s = Step(name=Name, number=number, type=pType)
		s.put()

	def delete(self, idStep):
		c = Component.all()
		c.filter('Step =', Step.get_by_id(idStep).key()).delete()
		q = Step.get_by_id(idStep)
		q.delete()

	def search(self, pName):
		if pName is None:
			return Step.all().fetch(limit=10);
		else:
			q = Step.all()
			return q.filter('name =', pName).get()

	def update(self, name, number, pType, idStep):
		oStep = Step.get_by_id(idStep)
		oStep.name = name
		oStep.number = number
		oStep.step = pType
		oStep.put()

	def getChoice(self):
		return ["one", "multi", "warning"];

	def ifexist(self, index):
		q = Step.all()
		return q.filter('index =', index).get()

class apiComponent():
	def add(self, Name, Stock, idStep, pPrix):
		C = Component(name = Name, stock = Stock, prix = pPrix, Step = Step.get_by_id(idStep).key())
		C.put()

	def delete(self, idCom):
		q = Component.get_by_id(idCom)
		q.delete()

	def update(self, idCom, Name, Stock, idStep, pPrix):
		com = Component.get_by_id(idCom)
		com.name = Name
		com.stock = Stock
		com.Step = Step.get_by_id(idStep).key()
		com.prix = pPrix
		com.put()

	def search(self, pName):
		if pName is None:
			return Component.all().fetch(limit=100);
		else:
			q = Component.all()
			return q.filter('name =', pName).get()