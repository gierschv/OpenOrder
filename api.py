import webapp2

class API(webapp2.RequestHandler):
    def get(self):
    	self.response.headers['Content-Type'] = 'text/plain'

    	mapping = {
    		'add':    self.add,
    		'remove': self.remove
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
    	self.response.write(argumentMap)

    def remove(self, argumentMap):
    	self.response.write('Called function remove, arguments:\n')
    	self.response.write(argumentMap)
