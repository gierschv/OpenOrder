import webapp2
import json
import entities
import datetime
import time

class API(webapp2.RequestHandler):

    #
    # Request handling, OPTIONS/GET/POST/DELETE
    #

    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE'

    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

    	mapping = {
            'step'           : self.get_steps,
            'step.json'      : self.get_steps,
            'component'      : self.get_components,
            'component.json' : self.get_components,
            'order'          : self.get_orders,
            'order.json'     : self.get_orders
    	}

        # Get called method
        func = self.request.path_info[len("/api/"):]

        # Check if method exists
    	if func not in mapping:
            return self.abort(404)

        args = {}
        for argumentName in self.request.arguments():
            args[argumentName] = self.request.get(argumentName)

        mapping[func](args)

    def post(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        mapping = {
            'step'                 : self.update_step,
            'step.json'            : self.update_step,
            'component'            : self.update_component,
            'component.json'       : self.update_component,
            'order'                : self.update_order,
            'order.json'           : self.update_order,
            'order/sell'           : self.sell_order,
            'order.json/sell'      : self.sell_order,
            'order/favourite'      : self.add_order_to_favourites,
            'order.json/favourite' : self.add_order_to_favourites
        }

        # Get called method
        func = self.request.path_info[len("/api/"):]

        # Check if method exists
        if func not in mapping:
            return self.abort(404)

        # GAE issue, url encodes the body when fetching arguments ?!
        body = self.request.body

        args = {}
        for argumentName in self.request.arguments():
            args[argumentName] = self.request.get(argumentName)

        self.request.body = body

        mapping[func](args)

    def delete(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        mapping = {
            'step'           : self.remove_step,
            'step.json'      : self.remove_step,
            'component'      : self.remove_component,
            'component.json' : self.remove_component,
            'order'          : self.remove_order,
            'order.json'     : self.remove_order
        }

        # Get called method
        func = self.request.path_info[len("/api/"):]

        # Check if method exists
        if func not in mapping:
            return self.abort(404)

        args = {}
        for argumentName in self.request.arguments():
            args[argumentName] = self.request.get(argumentName)

        mapping[func](args)

    #
    # Utils
    #

    def checkApiKeyIsAdmin(self, apiKey):
        if not apiKey:
            return False
        apiUser = entities.apiUser().getApiKey(apiKey)
        if not apiUser or not apiUser.admin:
            return False
        return True

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
            'dateSold'    : time.mktime(order.Sold.timetuple()) if order.Sold else None,
            'components'  : componentsIds,
            'user'        : order.User.key().name() if order.User else None,
            'id'          : order.key().id()
        }

        return orderData

    def serializableDataFromFavourite(self, order):
        componentsIds = [componentKey.id() for componentKey in order.ingredient]

        orderData = {
            'components'  : componentsIds,
            'user'        : order.User.key().name() if order.User else None,
            'name'        : order.name,
            'nbVote'      : order.nbVote,
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
        # Check API key
        apiKey = argumentMap.get('api_key')
        if not apiKey:
            return self.abort(403)
        apiUser = entities.apiUser().getApiKey(apiKey)
        if not apiUser:
            return self.abort(403)

        if 'filter' in argumentMap and argumentMap['filter'] == 'favourite':
            if 'user' in argumentMap:
                orders = entities.apifavoriteOrder().getUserfavOrder(argumentMap['user'], None)
            else:
                orders = entities.apifavoriteOrder().getTopFav(10)
            json.dump([self.serializableDataFromFavourite(order) for order in orders], self.response)
        elif 'filter' in argumentMap:
            filters = {
                'sold':   lambda: entities.apiOrder().getSoldOrder(None),
                'unsold': lambda: entities.apiOrder().getCurrentOrder(None)
            }
            filter = argumentMap['filter']
            if filter not in filters:
                return self.abort(400)
            else:
                if apiUser.admin:
                    # Fetch all orders
                    orders = [self.serializableDataFromOrder(order) for order in filters[filter]()]
                else:
                    # Fetch only the user's orders
                    orders = [self.serializableDataFromOrder(order) for order in filters[filter]() if order.User and order.User.key() == apiUser.key()]
                json.dump(orders, self.response)

        elif 'user' in argumentMap:
            user = entities.apiUser().get(argumentMap['user'])
            if user == None:
                return self.abort(400)

            if apiUser.admin or apiUser.key() == user.key():
                orders = [self.serializableDataFromOrder(order) for order in entities.apiOrder().getUserOrder(argumentMap['user'], None)]
                json.dump(orders, self.response)
            else:
                return self.abort(403)

        else:
            # All orders of just a specific one
            if 'id' in argumentMap:
                order = entities.apiOrder().get(long(argumentMap['id']))
                if apiUser.admin or (order.User and apiUser.key() == order.User.key()):
                    if order:
                        json.dump(self.serializableDataFromOrder(order), self.response)
                else:
                    return self.abort(403)
            else:
                # Only an admin can list all orders
                if apiUser.admin:
                    orders = entities.apiOrder().getAll(None)
                else:
                    orders = entities.apiOrder().getUserOrder(apiUser.key().name(), None)

                ordersData = []
                for order in orders:
                    ordersData.append(self.serializableDataFromOrder(order))

                json.dump(ordersData, self.response)

    #
    # POST methods
    #

    def update_step(self, argumentMap):

        # Decode JSON
        stepDescription = {}
        try:
            stepDescription = json.loads(self.request.body)
        except ValueError:
            return self.abort(400)

        # Check API key
        if not self.checkApiKeyIsAdmin(stepDescription.get('api_key')) and not self.checkApiKeyIsAdmin(argumentMap.get('api_key')):
            return self.abort(403)

        # Check parameters
        requiredKeys = ['name', 'number', 'type']
        if not self.checkRequiredKeys(stepDescription, requiredKeys):
            return self.abort(400)

        # Fetch elements
        stepName  = stepDescription.pop('name')
        stepIndex = stepDescription.pop('number')
        stepType  = stepDescription.pop('type')
        stepId    = stepDescription.pop('id', None)

        # Check type
        if not stepType in ['multi', 'warning', 'one']:
            return self.abort(400)

        # If 'id' is in query string, update, otherwise add the new one
        if stepId != None:
            entities.apiStep().update(stepName, long(stepIndex), stepType, long(stepId))
            self.response.write(json.dumps({ 'success': True }))
        else:
            entities.apiStep().add(stepName, long(stepIndex), stepType)
            self.response.write(json.dumps({ 'success': True }))

    def update_component(self, argumentMap):
        # Decode JSON
        componentDescription = {}
        try:
            componentDescription = json.loads(self.request.body)
        except ValueError:
            return self.abort(400)

        # Check API key
        if not self.checkApiKeyIsAdmin(componentDescription.get('api_key')) and not self.checkApiKeyIsAdmin(argumentMap.get('api_key')):
            return self.abort(403)

        # Check parameters
        requiredKeys = ['name', 'stock', 'price', 'step']
        if not self.checkRequiredKeys(componentDescription, requiredKeys):
            return self.abort(400)

        compName  = componentDescription.pop('name')
        compStock = componentDescription.pop('stock')
        compPrice = componentDescription.pop('price')
        compStep  = componentDescription.pop('step')
        compId    = componentDescription.pop('id', None)

        # If 'id' is in query string, update, otherwise add the new one
        if compId != None:
            entities.apiComponent().update(long(compId), compName, long(compStock), long(compStep), float(compPrice))
            self.response.write(json.dumps({ 'success': True }))
        else:
            entities.apiComponent().add(compName, long(compStock), long(compStep), float(compPrice))
            self.response.write(json.dumps({ 'success': True }))

    def update_order(self, argumentMap):
        # Decode JSON
        orderData = {}
        try:
            orderData = json.loads(self.request.body)
        except ValueError:
            return self.abort(409)

        # Check parameters
        requiredKeys = ['components']
        if not self.checkRequiredKeys(orderData, requiredKeys):
            return self.abort(408)

        orderComponents   = orderData.pop('components')
        orderDateCreation = orderData.pop('dateCreation', time.time())
        orderDateSelling  = orderData.pop('dateSelling', None)
        orderId           = orderData.pop('id', None)
        orderFId          = orderData.pop('fid', None)

        # Check API key
        if argumentMap.get('api_key'):
            orderData['api_key'] = argumentMap.pop('api_key')

        apiUser = None
        if orderData.has_key('api_key'):
            apiUser = entities.apiUser().getApiKey(orderData['api_key'])
            if not apiUser:
                return self.abort(407)
            orderUser = apiUser.key().name()
        else:
            orderUser = None

        # Build components list
        componentsIds = []
        steps = {}
        for compId in orderComponents:
            compQuantity = orderComponents[str(compId)]

            # Fetch component
            component = entities.apiComponent().get(long(compId))
            if component == None:
                return self.abort(406)

            # Fetch step
            if component.Step.key().id() not in steps:
                step = entities.apiStep().get(component.Step.key().id())
                if step == None:
                    return self.abort(405)
                steps[component.Step.key().id()] = step
            else:
                step = steps[component.Step.key().id()]

                # Check number of components for type `one`
                if step.type == "one":
                    return self.abort(402)

            # Decrease component stock
            component.stock -= compQuantity
            component.put()

            for i in range(compQuantity):
                componentsIds.append(long(compId))

        # Favorite Hits
        if orderFId != None:
            favourite = entities.apifavoriteOrder().get(orderFId)
            if not favourite:
                return slef.abort(401)
            favourite.nbVote += 1
            favourite.put()

        # Ajout/Update de l'order
        if orderId != None:
            if not apiUser or not apiUser.admin:
                return self.abort(403)
            order = entities.apiOrder().update(componentsIds, long(orderId), datetime.datetime.fromtimestamp(orderDateSelling), str(orderUser))
            self.response.write(json.dumps({ 'orderId': order.key().id() }))
        else:
            order = entities.apiOrder().add(componentsIds, datetime.datetime.fromtimestamp(orderDateCreation), str(orderUser))
            self.response.write(json.dumps({ 'orderId': order.key().id() }))

    def sell_order(self, argumentMap):
        # Decode JSON
        data = {}
        try:
            data = json.loads(self.request.body)
        except ValueError:
            return self.abort(400)

        # Check API key
        if not self.checkApiKeyIsAdmin(data.get('api_key')) and not self.checkApiKeyIsAdmin(argumentMap.get('api_key')):
            return self.abort(403)

        # Get order id
        if 'id' not in data:
            return self.abort(400)

        orderId = long(data['id'])

        # Get sell date or set it to now
        if 'date' in data:
            dateSold = datetime.datetime.fromtimestamp(data['date'])
        else:
            dateSold = datetime.datetime.fromtimestamp(time.time())

        # Set order as sold
        entities.apiOrder().setSold(orderId, dateSold)

        self.response.write(json.dumps({ 'success': True }))

    def add_order_to_favourites(self, argumentMap):
        # Decode JSON
        data = {}
        try:
            data = json.loads(self.request.body)
        except ValueError:
            return self.abort(400)

        # Check API key
        if argumentMap.get('api_key'):
            apiKey = argumentMap.pop('api_key')
        else:
            apiKey = data.get('api_key')

        if not apiKey:
            return self.abort(403)
        apiUser = entities.apiUser().getApiKey(apiKey)
        if not apiUser:
            return self.abort(403)

        # Get order id
        if 'id' not in data:
            return self.abort(400)

        orderId = long(data['id'])

        # Get the order itself
        order = entities.apiOrder().get(orderId)
        if order == None:
            return self.abort(400)

        # Get the name given to the favourite
        if 'name' not in data:
            return self.abort(400)
        orderName = data['name']

        # If the apiUser is an admin, he can specify another user who the order will be favourite to
        user = data.get('user')
        if apiUser.admin and user:
            entities.apifavoriteOrder().add(order.ingredient, 0, user.key().name(), orderName)
        else:
            entities.apifavoriteOrder().add(order.ingredient, 0, apiUser.key().name(), orderName)

        json.dump({'success': True}, self.response)

    #
    # DELETE methods
    #

    def remove_step(self, queryStringArguments):
        # Check API key
        if not self.checkApiKeyIsAdmin(queryStringArguments.get('api_key')):
            return self.abort(403)

        # Check parameters
        requiredKeys = ['id']
        if not self.checkRequiredKeys(queryStringArguments, requiredKeys):
            return self.abort(400)

        # Get Step id
        stepId = queryStringArguments.pop('id')

        # Delete step
        entities.apiStep().delete(long(stepId))

        json.dump({'success': True}, self.response)

    def remove_component(self, queryStringArguments):
        # Check API key
        if not self.checkApiKeyIsAdmin(queryStringArguments.get('api_key')):
            return self.abort(403)

        # Check si l'id du component est present
        requiredKeys = ['id']
        if not self.checkRequiredKeys(queryStringArguments, requiredKeys):
            return self.abort(400)

        # Get component id
        compId = queryStringArguments.pop('id')

        # Delete component
        entities.apiComponent().delete(long(compId))

        json.dump({'success': True}, self.response)

    def remove_order(self, queryStringArguments):
        # Check API key
        if not self.checkApiKeyIsAdmin(queryStringArguments.get('api_key')):
            return self.abort(403)

        # Check parameters
        requiredKeys = ['id']
        if not self.checkRequiredKeys(queryStringArguments, requiredKeys):
            return self.abort(400)

        # Get order id
        orderId = queryStringArguments.pop('id')

        # Delete order
        entities.apiOrder().delete(long(orderId))

        json.dump({'success': True}, self.response)