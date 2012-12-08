$(function() {
 // Handler for .ready() called.
	FB.init({
		appId      : '530821850262515', // App ID
		channelUrl : '//open-order.appspot.com/static/common/views/channel.html', // Channel File
		status     : true, // check login status
		cookie     : true, // enable cookies to allow the server to access the session
		xfbml      : true  // parse XFBML
	});
 
	var eventLogin = function(response) {
		console.log(response.authResponse);
		$.get('/api/auth', response.authResponse , function (data) {
			console.log("hello");
			console.log(data);
		});
		$.get('https://graph.facebook.com/me/friends?access_token=' + response.authResponse.accessToken, null, function (data) {
			console.log('hello');
			console.log(data);
		});
		//$.get()
		//$fql_queryurl"SELECT uid FROM user WHERE has_added_app=1 and uid IN (SELECT uid2 FROM friend WHERE uid1 = $user)"
		// /fql?q=query 
	}
	FB.Event.subscribe('auth.authResponseChange', eventLogin);
	//FB.getLoginStatus(eventLogin);
});