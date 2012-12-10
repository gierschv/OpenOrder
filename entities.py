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
	active = db.BooleanProperty(default=True)
	admin = db.BooleanProperty(default=False)

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
	nbVote = db.IntegerProperty(default=1)
	User = db.ReferenceProperty(User)

class Order(db.Model):
	ingredient = db.ListProperty(db.Key)
	dateCommand = db.DateTimeProperty()
	Sold = db.DateTimeProperty()
	User = db.ReferenceProperty(User)

class apiUser():
	def get(self, id):
		return User.get_by_key_name(id)

	def delete(self, idUser):
		u = User.get_by_key_name(idUser)
		if u:
			u.delete()

	def getApiKey(self, ApiKey):
		q = User.all()
		return q.filter('api_key =', ApiKey).get()

	def Update(self, firstname, lastname, pActive, pAdmin, id):
		q = User.get_by_key_name(id)
		if q == None:
			return None
		if firstname != None:
			q.first_name = firstname
		if lastname != None:
			q.last_name = lastname
		if active != None:
			q.active = pActive
		if admin != None:
			q.admin = pAdmin
		q.put()
		return q

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
		ingredientsKeys = [Component.get_by_id(componentId).key() for componentId in listCom]
		O = Order(ingredient=ingredientsKeys, dateCommand=dateBuy)
		if id != None:
			O.User = User.get_by_key_name(id).key()
		O.put()
		return O

	def getAll(self, pLimit):
		q = Order.all()
		if pLimit == None:
			return q.fetch(limit=q.count())
		else:
			return q.fetch(limit=pLimit)

	def getCurrentOrder(self, pLimit):
		q = Order.all()
		return q.filter('Sold =', None).order('dateCommand').fetch(limit=pLimit)

	def getSoldOrder(self, pLimit):
		q = Order.all()
		return q.filter('Sold !=', None).order('Sold').fetch(limit=pLimit)

	def getUserOrder(self, id, pLimit):
		q = Order.all()
		return q.filter('User =', User.get_by_key_name(id).key()).order('dateCommand').fetch(limit = pLimit)


	def delete(self, idOrder):
		O = Order.get_by_id(idOrder)
		if O:
			O.delete()
	
	def update(self, components, idOrder, dateSoldOut, idUser):
		O = Order.get_by_id(idOrder)
		if O:
			O.ingredient = [Component.get_by_id(componentId).key() for componentId in components]
			O.Sold = dateSoldOut
			O.User = User().get_by_id(idUser).key()
			O.put()

	def get(self, id):
		return Order.get_by_id(id)

	def setSold(self, idOrder, dateSold):
		O = Order.get_by_id(idOrder)
		if O:
			O.Sold = dateSold
			O.put()

#
#	Class apiFavoriteOder, manage operation on users favortie Order
#	Link are made on User and Component
#

class apifavoriteOrder():
	def add(self, listCom, nbVote, idUser, pname):
		O = favoritOrder(ingredient=listCom, nbVote=nbVote, User=User.get_by_key_name(idUser).key(), name=pname)
		O.put()

	def getTopFav(self, pLimit):
		q = favoritOrder.all().order('-nbVote')
		nb = q.count()
		if pLimit == None:
			return q.fetch(limit=nb)
		else:
			return q.fetch(limit = pLimit)

	def delete(self, id):
		O = favoritOrder.get_by_id(id)
		O.delete()
	
	def update(self, ingredient, idFav, pName, pNbVote, idUser):
		O = favoritOrder.get_by_id(idFav)
		if O:
			O.ingredient = ingredient
			O.name = pName
			O.User = User.get_by_key_name(idUser).key()
			O.nbVote = pNbVote
			O.put()
	
	def getUserfavOrder(self, id, pLimit):
		if pLimit == None:
			q = favoritOrder.all().filter('User =', User.get_by_key_name(id).key())
			nb = q.count()
			return q.order('-nbVote').fetch(limit = nb)
		else:	
			return q.order('-nbVote').fetch(limit = pLimit)

	def get(self, id):
		return favoritOrder.get_by_id(id)

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
		s = Step.get_by_id(idStep)
		if s:
			c.filter('Step =', s.key())
			for component in c.run():
				component.delete()
			s.delete()

	def search(self, pName):
		if pName is None:
			return Step.all().order('number').fetch(limit=Step.all().count());
		else:
			q = Step.all()
			return q.filter('name =', pName).get()

	def update(self, name, number, pType, idStep):
		oStep = Step.get_by_id(idStep)
		if oStep:
			oStep.name = name
			oStep.number = number
			oStep.step = pType
			oStep.put()

	def getChoice(self):
		return ["one", "multi", "warning"];

	def ifexist(self, index):
		q = Step.all()
		return q.filter('index =', index).get()

	def get(self, id):
		return Step.get_by_id(id)

class apiComponent():
	def add(self, Name, Stock, idStep, pPrix):
		C = Component(name = Name, stock = Stock, prix = pPrix, Step = Step.get_by_id(idStep).key())
		C.put()

	def delete(self, idCom):
		q = Component.get_by_id(idCom)
		if q:
			q.delete()

	def update(self, idCom, Name, Stock, idStep, pPrix):
		com = Component.get_by_id(idCom)
		if com:
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

	def compByStep(self, id):
		q = Component.all()
		return q.filter('Step =', Step.get_by_id(id).key()).order('-name')

	def get(self, id):
		return Component.get_by_id(id)