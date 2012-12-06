'use strict';

function AuthCtrl($scope, $http, $location, $rootScope) {
  var eventLogin = function(response) {
    // Non-connected or unauthorized user
    if (response.status !== 'connected') {
      document.location.href = '/';
    }
    else {
      // Fetch api_key
      $http.get('/api/auth', {'params': response.authResponse }).success(function(profile) {
        $rootScope['profile'] = profile;
        $location.path('/home');
      });
    }
  };

  FB.Event.subscribe('auth.authResponseChange', eventLogin);
  FB.getLoginStatus(eventLogin);
}

function HomeCtrl($location, $rootScope) {
  if ($rootScope['profile'] === undefined) {
    return $location.path('/auth');
  }
  $('.navbar').show();
}

function LogoutCtrl() {
  $('.navbar').hide();
}