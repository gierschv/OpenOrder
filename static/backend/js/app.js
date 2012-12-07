'use strict';

var app = angular.module('openorder', ['ui', 'openorderServices']).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/auth', { templateUrl: '/backend/_auth.html', controller: AuthCtrl }).
      when('/logout', { templateUrl: '/backend/_logout.html', controller: LogoutCtrl }).
      when('/home', { templateUrl: '/backend/_home.html', controller: HomeCtrl }).
      when('/components', { templateUrl: '/backend/_components.html', controller: ComponentsCtrl }).
      when('/orders', { templateUrl: '/backend/_orders.html', controller: OrdersCtrl }).
      otherwise({redirectTo: '/auth'});
}]);


app.run(function($rootScope) {
  // Facebook init
  FB.init({
    appId      : '530821850262515', // App ID
    channelUrl : '//open-order.appspot.com/static/common/views/channel.html', // Channel File
    status     : true, // check login status
    cookie     : true, // enable cookies to allow the server to access the session
    xfbml      : true  // parse XFBML
  });

  $rootScope.FBlogout = function() {
    console.log('FBlogout');
    FB.logout(function(response) {
      console.log(resonse);
      document.location.href = '/';
    });
  };
});
