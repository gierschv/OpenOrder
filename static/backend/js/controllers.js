'use strict';

function AuthCtrl($scope, $http, $location, $rootScope) {
  FB.init({
    appId      : '530821850262515', // App ID
    channelUrl : '//open-order.appspot.com/static/common/views/channel.html', // Channel File
    status     : true, // check login status
    cookie     : true, // enable cookies to allow the server to access the session
    xfbml      : true  // parse XFBML
  });

  FB.Event.subscribe('auth.login', function(response) {
    // Non-connected or unauthorized user
    if (response.status !== 'connected') {
      //document.location.href = '/';
    }
    else {
      // Fetch api_key
      $http.get('/api/auth', {'params': response.authResponse }).success(function(profile) {
        $rootScope['profile'] = profile;
        $location.path('/home');
      });
    }
  });
}


function HomeCtrl() {


}