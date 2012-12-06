import webapp2
import json
import entities
import urllib

class API(webapp2.RequestHandler):

    #
    # Request handling, GET or POST
    #

    def get(self):
    	self.response.headers['Content-Type'] = 'text/plain'

    	mapping = {
    		'add':      self.add,
    		'remove':   self.remove,
            'update':   self.update
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

    		mapping[func](args, self.request.body)

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'

        if 'data' not in self.request.POST:
            self.response.write('Missing "data" key in POST variables')
            return

        mapping = {
            'add_step': self.add_step,
            'add_component': self.add_component
        }

        # Recuperation de la methode appelee
        func = self.request.path_info[len("/api/"):]

        if func not in mapping:
            self.response.write('Supported functions:\n')
            for func in mapping.keys():
                self.response.write(func + '\n')
        else:
            mapping[func](self.request.POST['data'])

    #
    # Utils
    #

    def checkRequiredKeys(self, dictionary, requiredKeys):
        missingRequiredKey = False
        for requiredKey in requiredKeys:
            if requiredKey not in dictionary:
                missingRequiredKey = True

        return False if missingRequiredKey else True

    #
    # GET methods
    #

    def add(self, argumentMap, requestBody):
    	self.response.write('Called function add, arguments:\n')
        entities.apiStep().add("starters", 1, "multi")
        entities.apiComponent().add("chips", 152, entities.apiStep().search('starters').key(), 5.25)
    	self.response.write(argumentMap)

    def remove(self, argumentMap, requestBody):
    	self.response.write('Called function remove, arguments:\n')
    	self.response.write(argumentMap)

    def update(self, argumentMap, requestBody):
        self.response.write('Called functions update, arguments:\n')
        obj = entities.apiComponent().search("chips")
        entities.apiComponent().update(obj.key(), obj.name, obj.stock - 1, obj.Step, 12.0)

    #
    # POST methods
    #

    def add_step(self, postData):

        # Decode le JSON pour recuperer les donnees qui concernent la step a creer
        stepDescription = {}
        try:
            stepDescription = json.loads(postData)
        except ValueError:
            self.response.write('Invalid JSON')
            return

        # Check si tous les champs sont presents dans les donnees POST
        requiredKeys = ['name', 'index', 'type']
        if not self.checkRequiredKeys(postData, requiredKeys):
            self.response.write('Error, missing required key in POST data. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation des donnees utiles
        stepName  = stepDescription.pop('name')
        stepIndex = stepDescription.pop('index')
        stepType  = stepDescription.pop('type')

        # On previent qu'on ignore les donnees inutiles
        for extraKey in stepDescription:
            self.response.write('Ignoring extra key "' + extraKey + '"\n')

        entities.apiStep().add(stepName, stepIndex, stepType)

        self.response.write('Step "' + stepName + '" added successfully.\n')

    def add_component(self, postData):

        # Decode le JSON pour recuperer les donnees qui concernent le component a creer
        componentDescription = {}
        try:
            componentDescription = json.loads(postData)
        except ValueError:
            self.response.write('Invalid JSON')
            return

        # Check si tous les champs sont presents dans les donnees POST
        requiredKeys = ['name', 'stock', 'price', 'step']
        if not self.checkRequiredKeys(postData, requiredKeys):
            self.response.write('Error, missing required key in POST data. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation des donnees utiles
        compName  = componentDescription.pop('name')
        compStock = componentDescription.pop('stock')
        compPrice = componentDescription.pop('price')
        compStep  = componentDescription.pop('step')

        # On previent qu'on ignore les donnees inutiles
        for extraKey in componentDescription:
            self.response.write('Ignoring extra key "' + extraKey + '"\n')

        self.response.write('Looking for step with name "' + compStep + '"...')

        matchingSteps = entities.apiStep().search(compStep)
        stepKey = None

        if matchingSteps == None:
            self.response.write('Step not found\n')
            return
        else:
            self.response.write('Found step:\n')
            self.response.write('Step name: ' + matchingSteps.name + '\n')
            self.response.write('Step key: ')
            self.response.write(matchingSteps.key())
            self.response.write('\n')
            stepKey = matchingSteps.key()

        entities.apiComponent().add(compName, compStock, stepKey, compPrice)

        self.response.write('Component "' + compName + '" successfully added to step "' + compStep + '"\n')
