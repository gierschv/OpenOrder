'use strict';

angular.module('openorder', []).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/auth', { templateUrl: '/backend/_auth.html', controller: AuthCtrl }).
      when('/home', { templateUrl: '/backend/_home.html', controller: HomeCtrl }).
      otherwise({redirectTo: '/auth'});
}]);
