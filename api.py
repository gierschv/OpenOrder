import webapp2
import json
import entities
import datetime
import time

class API(webapp2.RequestHandler):

    #
    # Request handling, GET/POST/DELETE
    #

    def get(self):
    	mapping = {
            'step'           : self.get_steps,
            'step.json'      : self.get_steps,
            'component'      : self.get_components,
            'component.json' : self.get_components,
            'order'          : self.get_orders,
            'order.json'     : self.get_orders
    	}

        # Recuperation de la methode appelee
        func = self.request.path_info[len("/api/"):]

    	if func not in mapping:
            self.abort(404)

    		# self.response.write('Supported functions:\n')
    		# for func in mapping.keys():
    		# 	self.response.write(func + '\n')

    	else:
            self.response.headers['Content-Type'] = 'application/json'

            args = {}
            for argumentName in self.request.arguments():
                args[argumentName] = self.request.get(argumentName)

            mapping[func](args)

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'

        mapping = {
            'step'            : self.update_step,
            'step.json'       : self.update_step,
            'component'       : self.update_component,
            'component.json'  : self.update_component,
            'order'           : self.update_order,
            'order.json'      : self.update_order,
            'order/sell'      : self.sell_order,
            'order.json/sell' : self.sell_order
        }

        # Recuperation de la methode appelee
        func = self.request.path_info[len("/api/"):]

        if func not in mapping:
            self.response.write('Supported functions:\n')
            for func in mapping.keys():
                self.response.write(func + '\n')
        else:
            mapping[func]()

    def delete(self):
        self.response.headers['Content-Type'] = 'text/plain'

        mapping = {
            'step'           : self.remove_step,
            'step.json'      : self.remove_step,
            'component'      : self.remove_component,
            'component.json' : self.remove_component,
            'order'          : self.remove_order,
            'order.json'     : self.remove_order
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

    def serializableDataFromOrder(self, order):
        componentsIds = [componentKey.id() for componentKey in order.ingredient]

        orderData = {
            'dateCreated' : time.mktime(order.dateCommand.timetuple()),
            'dateSold'    : order.Sold,
            'components'  : componentsIds,
            'user'        : order.User.key().name() if order.User else None,
            'id'          : order.key().id()
        }

        return orderData

    #
    # GET methods
    #

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

    def get_orders(self, argumentMap):

        # All orders of just a specific one
        if 'id' in argumentMap:
            order = entities.apiOrder().get(long(argumentMap['id']))
            if order:
                json.dump(self.serializableDataFromOrder(order), self.response)
        else:
            orders = entities.apiOrder().getAll(None)

            ordersData = []
            for order in orders:
                ordersData.append(self.serializableDataFromOrder(order))

            json.dump(ordersData, self.response)

    #
    # POST methods
    #

    def update_step(self):

        # Decode le JSON pour recuperer les donnees qui concernent la step a creer
        stepDescription = {}
        try:
            stepDescription = json.loads(self.request.body)
        except ValueError:
            self.response.write('Invalid JSON')
            return

        # Check si tous les champs sont presents dans les donnees POST
        requiredKeys = ['name', 'number', 'type']
        if not self.checkRequiredKeys(stepDescription, requiredKeys):
            self.response.write('Error, missing required key in POST data. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation des donnees utiles
        stepName  = stepDescription.pop('name')
        stepIndex = stepDescription.pop('number')
        stepType  = stepDescription.pop('type')
        stepId    = stepDescription.pop('id', None)

        # On previent qu'on ignore les donnees inutiles
        for extraKey in stepDescription:
            self.response.write('Ignoring extra key "' + extraKey + '"\n')

        # Si argument 'id' dans la query string, alors update, sinon add
        if stepId != None:
            entities.apiStep().update(stepName, long(stepIndex), stepType, long(stepId))
            self.response.write('Step "' + stepName + '" updated successfully.\n')
        else:
            entities.apiStep().add(stepName, long(stepIndex), stepType)
            self.response.write('Step "' + stepName + '" added successfully.\n')

    def update_component(self):

        # Decode le JSON pour recuperer les donnees qui concernent le component a creer
        componentDescription = {}
        try:
            componentDescription = json.loads(self.request.body)
        except ValueError:
            self.response.write('Invalid JSON')
            return

        # Check si tous les champs sont presents dans les donnees POST
        requiredKeys = ['name', 'stock', 'price', 'step']
        if not self.checkRequiredKeys(componentDescription, requiredKeys):
            self.response.write('Error, missing required key in POST data. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation des donnees utiles
        compName  = componentDescription.pop('name')
        compStock = componentDescription.pop('stock')
        compPrice = componentDescription.pop('price')
        compStep  = componentDescription.pop('step')
        compId    = componentDescription.pop('id', None)

        # On previent qu'on ignore les donnees inutiles
        for extraKey in componentDescription:
            self.response.write('Ignoring extra key "' + extraKey + '"\n')

        # Si argument 'id' dans la query string, alors update, sinon add
        if compId != None:
            entities.apiComponent().update(long(compId), compName, long(compStock), long(compStep), float(compPrice))
            self.response.write('Component successfully updated.\n')
        else:
            entities.apiComponent().add(compName, long(compStock), long(compStep), float(compPrice))
            self.response.write('Component "' + compName + '" successfully added to step ' + str(compStep) + '\n')

    def update_order(self):

        # Decode le JSON pour recuperer les donnees qui concernent l'order a creer
        orderData = {}
        try:
            orderData = json.loads(self.request.body)
        except ValueError:
            self.response.write('Invalid JSON')
            return

        # Check si tous les champs necessaires sont presents dans les donnees POST
        requiredKeys = ['components']
        if not self.checkRequiredKeys(orderData, requiredKeys):
            self.response.write('Error, missing required key in POST data. Required keys are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation des donnees utiles
        orderComponents   = orderData.pop('components')
        orderDateCreation = orderData.pop('dateCreation', time.time())
        orderDateSelling  = orderData.pop('dateSelling', None)
        orderId           = orderData.pop('id', None)

        # Check API key
        if orderData.has_key('api_key'):
            user = entities.apiUser().getApiKey(orderData['api_key'])
            if not user:
                return self.abort(403)
            orderUser = user.key().name()
        else:
            orderUser = None

        # On construit la liste des ids des components
        componentsIds = []
        steps = {}
        for compId in orderComponents:
            compQuantity = orderComponents[str(compId)]

            # Recuperation du component
            component = entities.apiComponent().get(long(compId))
            if component == None:
                self.response.write('Error: Invalid component id "' + str(compId) + '".\n')
                return

            # Recuperation de la step du component si pas deja fait
            if component.Step.key().id() not in steps:
                step = entities.apiStep().get(component.Step.key().id())
                if step == None:
                    self.response.write('Error: Failed to retrieve step for component with id "' + str(compId) + '".\n')
                    return
                steps[component.Step.key().id()] = step
            else:
                step = steps[component.Step.key().id()]

                # Verification qu'il n'y ait pas plusieurs components pour une step de type "one"
                if step.type == "one":
                    self.response.write('Error: Multiple components specified for step "' + step.name + '" (id ' + str(step.id()) + ').\n')
                    return

            for i in range(compQuantity):
                componentsIds.append(long(compId))


        # Ajout/Update de l'order
        # TODO: Checker si les components sont bien du bon type (id ? key ? Component ?)
        # TODO: Checker pourquoi une seule date en parametre
        if orderId != None:
            order = entities.apiOrder().update(componentsIds, long(orderId), datetime.datetime.fromtimestamp(orderDateSelling), str(orderUser))
            self.response.write(json.dumps({ 'orderId': order.key().id() }))
        else:
            order = entities.apiOrder().add(componentsIds, datetime.datetime.fromtimestamp(orderDateCreation), str(orderUser))
            self.response.write(json.dumps({ 'orderId': order.key().id() }))

    def sell_order(self):

        # Decode JSON
        data = {}
        try:
            data = json.loads(self.request.body)
        except ValueError:
            self.response.write('Invalid JSON')
            return

        # Get order id
        if 'id' not in data:
            self.response.write('Error: Missing order id.\n')
            return

        orderId = long(data['id'])

        # Get sell date or set it to now
        if 'date' in data:
            dateSold = datetime.datetime.fromtimestamp(data['date'])
        else:
            dateSold = datetime.datetime.fromtimestamp(time.time())

        # Set order as sold
        entities.apiOrder().setSold(orderId, dateSold)

        self.response.write(json.dumps({ 'success': True }))

    #
    # DELETE methods
    #

    def remove_step(self, queryStringArguments):

        # Check si le nom de la step est present
        requiredKeys = ['id']
        if not self.checkRequiredKeys(queryStringArguments, requiredKeys):
            self.response.write('Error, missing required argument. Required arguments are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation du nom de la step
        stepId = queryStringArguments.pop('id')

        # On previent qu'on ignore les donnees inutiles
        for extraArg in queryStringArguments:
            self.response.write('Ignoring extra argument "' + extraArg + '"\n')

        # Suppression de la step
        entities.apiStep().delete(long(stepId))

        self.response.write('Step ' + str(stepId) + ' removed successfully.')

    def remove_component(self, queryStringArguments):

        # Check si l'id du component est present
        requiredKeys = ['id']
        if not self.checkRequiredKeys(queryStringArguments, requiredKeys):
            self.response.write('Error, missing required argument. Required arguments are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation de l'id du component
        compId = queryStringArguments.pop('id')

        # On previent qu'on ignore les donnees inutiles
        for extraArg in queryStringArguments:
            self.response.write('Ignoring extra argument "' + extraArg + '"\n')

        # Suppression du component
        entities.apiComponent().delete(long(compId))

        self.response.write('Component ' + str(compId) + ' removed successfully.\n')

    def remove_order(self, queryStringArguments):
        # Check si l'id de l'order est present
        requiredKeys = ['id']
        if not self.checkRequiredKeys(queryStringArguments, requiredKeys):
            self.response.write('Error, missing required argument. Required arguments are:\n')
            for key in requiredKeys:
                self.response.write(key + '\n')
            return

        # Recuperation de l'id de l'order
        orderId = queryStringArguments.pop('id')

        # On previent qu'on ignore les arguments inutiles
        for extraArg in queryStringArguments:
            self.response.write('Ignoring extra argument "' + extraArg + '"\n')

        # Suppression de l'order
        entities.apiOrder().delete(long(orderId))

        self.response.write('Order ' + str(orderId) + ' removed successfully.\n')