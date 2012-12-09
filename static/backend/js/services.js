'use strict';

/* Services */
angular.module('openorderServices', ['ngResource']).
    factory('Step', function($resource) {
      return $resource('/api/step.json');
    }).
    factory('Component', function($resource) {
      return $resource('/api/component.json');
    }).
    factory('Order', function($resource) {
      return $resource('/api/order.json');
    });
