'use strict';

function AuthCtrl($scope, $http) {
  FB.init({
    appId      : '530821850262515', // App ID
    channelUrl : '//open-order.appspot.com/static/common/views/channel.html', // Channel File
    status     : true, // check login status
    cookie     : true, // enable cookies to allow the server to access the session
    xfbml      : true  // parse XFBML
  });

  FB.getLoginStatus(function(response) {
    // Non-connected or unauthorized user
    console.log(response.status !== 'connected');
    if (response.status !== 'connected') {
      //document.location.href = '/';
    }
    else {
      console.log(response);
      // Fetch api_key
      $http.get('/api/auth', {'params': response.authResponse }).success(function(data) {
        console.log(data);
      });
    }
  });
}
