#!/usr/bin/env python

import facebook
import entities
import webapp2
import string
import random
import json

FACEBOOK_APP_ID = "530821850262515"
FACEBOOK_APP_SECRET = "ba52337c7a1065d5051a132da9dfd831"

class AuthHandler(webapp2.RequestHandler):
	def get(self):
		# Check signed request for uid
		uid = self.request.GET['userID']
		signedRequest = self.request.GET['signedRequest']
		if not uid or not signedRequest:
			return self.abort(400)

		parsed_request = facebook.parse_signed_request(self.request.GET['signedRequest'], FACEBOOK_APP_SECRET)
		if not parsed_request or uid != parsed_request['user_id']:
			return self.abort(403)

		try:
			result = facebook.get_access_token_from_code(parsed_request["code"], "", FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
			profile = facebook.GraphAPI(result['access_token']).get_object("me")
		except facebook.GraphAPIError:
			return self.abort(403)

		# Fetch existant user or create new one
		user = entities.User.get_by_key_name(profile['id'])
		if not user:
			api_key = ''. join(random.choice(string.hexdigits) for x in range(64))
			user = entities.User(key_name = str(profile['id']),
								uid = int(profile['id']),
								first_name = profile['first_name'], last_name = profile['last_name'],
								api_key = api_key, access_token = result['access_token'], active = True)
		else:
			user.access_token = result['access_token']
		user.put();

		profile['api_key'] = user.api_key
		profile['access_token'] = user.access_token
		self.response.out.write(json.dumps(profile))
