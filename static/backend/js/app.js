'use strict';

angular.module('openorder', []).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/auth', { templateUrl: '_auth.html', controller: AuthCtrl }).
      otherwise({redirectTo: '/auth'});
}]);
