$(document).ready)(function() {
	var eventLogin = function(response) {
		console.log(response);
	};
	
	FB.Event.subscribe('auth.authResponseChange', eventLogin);
	FB.getLoginStatus(eventLogin);
	jQuery.get('/api/auth')


	var steps = jQuery.getJSON("/api/step.json");
	console.log(steps.responseText);


});

