'use strict';

/* Services */
angular.module('openorderServices', ['ngResource']).
    factory('Step', function($resource){
      return $resource('/api/step.json/:stepId', {}, {
        query: { method: 'GET', isArray: true },
        
      });
});
