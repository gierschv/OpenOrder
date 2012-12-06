'use strict';

var app = angular.module('openorder', []).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/auth', { templateUrl: '/backend/_auth.html', controller: AuthCtrl }).
      when('/logout', { templateUrl: '/backend/_logout.html', controller: LogoutCtrl }).
      when('/home', { templateUrl: '/backend/_home.html', controller: HomeCtrl }).
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
