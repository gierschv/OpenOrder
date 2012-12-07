'use strict';

/* Services */
angular.module('openorderServices', ['ngResource']).
    factory('Step', function($resource) {
      return $resource('/api/step.json/:stepId');
    }).
    factory('Component', function($resource) {
      return $resource('/api/component.json/:componentId');
    });
