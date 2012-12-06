import webapp2
import entities

class API(webapp2.RequestHandler):
    def get(self):
    	self.response.headers['Content-Type'] = 'text/plain'

    	mapping = {
    		'add':    self.add,
    		'remove': self.remove,
            'update': self.update
    	}

        # Recuperation de la methode appelee
        func = self.request.path_info[len("/api/"):]

    	if func not in mapping:
    		self.response.write('Supported functions:\n')
    		for func in mapping.keys():
    			self.response.write(func + '\n')
    	else:
    		args = {}
    		for argumentName in self.request.arguments():
    			args[argumentName] = self.request.get(argumentName)

    		mapping[func](args)


    def add(self, argumentMap):
    	self.response.write('Called function add, arguments:\n')
        #entities.apiStep().add("starters", 1, "multi")
        #entities.apiComponent().add("chips", 152, entities.apiStep().search('starters').key())
    	self.response.write(argumentMap)

    def remove(self, argumentMap):
    	self.response.write('Called function remove, arguments:\n')
    	self.response.write(argumentMap)

    def update(self, argumentMap):
        self.response.write('Called functions update, arguments:\n')
        obj = entities.apiComponent().search("chips")
        entities.apiComponent().update(obj.key(), obj.name, obj.stock - 1, obj.Step)
    