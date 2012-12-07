import webapp2
import json
import entities

class API(webapp2.RequestHandler):

    #
    # Request handling, GET/POST/DELETE
    #

    def get(self):
    	self.response.headers['Content-Type'] = 'application/json'

    	mapping = {
            'step' : self.get_steps,
            'step.json' : self.get_steps,
            'component' : self.get_components,
            'component.json' : self.get_components
#            'get_components_from_step_index' : get_components_from_step_index
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

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'

        mapping = {
            'step'          : self.add_step,
            'step.json'     : self.add_step,
            'component'     : self.add_component,
            'component.json': self.add_component
        }

        # Recuperation de la methode appelee
        func = self.request.path_info[len("/api/"):]

        if func not in mapping:
            self.response.write('Supported functions:\n')
            for func in mapping.keys():
                self.response.write(func + '\n')
        else:
            mapping[func](self.request.body)

    def delete(self):
        self.response.headers['Content-Type'] = 'text/plain'

        mapping = {
            'step'            : self.remove_step,
            'step.json'       : self.remove_step,
            'component'       : self.remove_component,
            'component.json'  : self.remove_component
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

    def serializableDataFromComponent(self, component):
        componentData = {
            'name'  : component.name,
            'stock' : component.stock,
            'price' : component.prix,
            'id'    : component.key().id()
        }
        return componentData

    def serializableDataFromStep(self, step):
        stepData = {
            'name'  : step.name,
            'index' : step.number,
            'type'  : step.type,
            'id'    : step.key().id()
        }
        return stepData

    #
    # GET methods
    #

    # def add(self, argumentMap, requestBody):
    # 	self.response.write('Called function add, arguments:\n')
    #     entities.apiStep().add("starters", 1, "multi")
    #     entities.apiComponent().add("chips", 152, entities.apiStep().search('starters').key().id(), 5.25)
    # 	self.response.write(argumentMap)

    def get_steps(self, argumentMap):
        steps = entities.apiStep().search(None)
        stepsData = []
        for step in steps:
            stepData = self.serializableDataFromStep(step)

            components = entities.apiComponent().compByStep(step.key().id())

            componentsData = []
            for component in components:
                componentsData.append(self.serializableDataFromComponent(component))

            stepData['components'] = componentsData

            stepsData.append(stepData)

        json.dump(stepsData, self.response)

    def get_components(self, argumentMap):
        components = entities.apiComponent().search(None)

        componentsData = []
        for component in components:
            componentsData.append(self.serializableDataFromComponent(component))

        json.dump(componentsData, self.response)

    # def get_components_from_step_index(self, argumentMap):
    #     requiredParams = ['step_index']
    #     if not self.checkRequiredKeys(argumentMap, requiredParams):
    #         self.response.write('Error, missing required key in POST data. Required keys are:\n')
    #         for key in requiredKeys:
    #             self.response.write(key + '\n')
    #         return

    # def update(self, argumentMap, requestBody):
    #     self.response.write('Called functions update, arguments:\n')
    #     obj = entities.apiComponent().search("chips")
    #     entities.apiComponent().update(obj.key().id(), obj.name, obj.stock - 1, obj.Step.key().id(), 12.0)

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
        requiredKeys = ['name', 'number', 'type']
        if not self.checkRequiredKeys(postData, requiredKeys):
            self.response.write('Error, missing required key in POST data. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation des donnees utiles
        stepName  = stepDescription.pop('name')
        stepIndex = stepDescription.pop('number')
        stepType  = stepDescription.pop('type')

        # On previent qu'on ignore les donnees inutiles
        for extraKey in stepDescription:
            self.response.write('Ignoring extra key "' + extraKey + '"\n')

        entities.apiStep().add(stepName, long(stepIndex), stepType)

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
            stepKey = matchingStep.key().id()

        # Ajout du component a la step
        entities.apiComponent().add(compName, long(compStock), stepKey, float(compPrice))

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
            stepKey = matchingStep.key().id()

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
            compKey = matchingComp.key().id()

        entities.apiComponent().delete(compKey)

        self.response.write('comp "' + compName + '" removed successfully.')
