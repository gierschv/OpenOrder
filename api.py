import webapp2
import json
import entities

class API(webapp2.RequestHandler):

    #
    # Request handling, GET/POST/DELETE
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

    def delete(self):
        self.response.headers['Content-Type'] = 'test/plain'

        mapping = {
            'remove_step':      self.remove_step,
            'remove_component': self.remove_component
        }

        # Recuperation de la methode appelee
        func = self.request.path_info[len("/api/"):]

        if func not in mapping:
            self.response.write('Supported functions:\n')
            for func in mapping.keys():
                self.response.write(func + '\n')
        else:
            mapping[func](self.request.body)

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

        # Recuperation de la step
        matchingStep = entities.apiStep().search(compStep)
        stepKey = None

        if matchingStep == None:
            self.response.write('Step not found\n')
            return
        else:
            # Recuperation de la key de la step
            stepKey = matchingStep.key()

        # Ajout du component a la step
        entities.apiComponent().add(compName, compStock, stepKey, float(compPrice))

        self.response.write('Component "' + compName + '" successfully added to step "' + compStep + '"\n')

    #
    # DELETE methods
    #

    def remove_step(self, requestBody):

        requestData = json.loads(requestBody)

        # Check si le nom de la step est present
        requiredKeys = ['step']
        if not self.checkRequiredKeys(requestBody, requiredKeys):
            self.response.write('Error, missing required key in request. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation du nom de la step
        stepName = requestData.pop('step')

        # On previent qu'on ignore les donnees inutiles
        for extraKey in componentDescription:
            self.response.write('Ignoring extra key "' + extraKey + '"\n')

        # Recuperation de l'objet step
        matchingStep = entities.apiStep().search(stepName)
        stepKey = None

        if matchingStep == None:
            self.response.write('Step not found\n')
            return
        else:
            # Recuperation de la key de la step
            stepKey = matchingStep.key()

        entities.apiStep().delete(stepKey)

        self.response.write('Step "' + stepName + '" removed successfully.')

    def remove_component(self, requestBody):

        self.response.write('Request body: "' + requestBody + '"\n')
        componentDescription = json.loads(requestBody)

        # Check si le nom du component est present
        requiredKeys = ['component']
        if not self.checkRequiredKeys(componentDescription, requiredKeys):
            self.response.write('Error, missing required key in request. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation du nom du component
        compName = componentDescription.pop('component')

        # On previent qu'on ignore les donnees inutiles
        for extraKey in componentDescription:
            self.response.write('Ignoring extra key "' + extraKey + '"\n')

        # Recuperation de l'objet component
        matchingComp = entities.apiComponent().search(compName)
        compKey = None

        if matchingComp == None:
            self.response.write('Component not found\n')
            return
        else:
            # Recuperation de la key du component
            compKey = matchingComp.key()

        entities.apiComponent().delete(compKey)

        self.response.write('comp "' + compName + '" removed successfully.')
