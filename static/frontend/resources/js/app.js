$(document).ready(function() {
 // Handler for .ready() called.
	FB.init({
		appId      : '530821850262515', // App ID
		channelUrl : '//open-order.appspot.com/static/common/views/channel.html', // Channel File
		status     : true, // check login status
		cookie     : true, // enable cookies to allow the server to access the session
		xfbml      : true  // parse XFBML
	});
 
	var accessToken, profile;
	var alreadyConnected = 0;
	var displayFriends = function () {
		var url_friends =  "https://graph.facebook.com/fql?q=SELECT%20name,%20uid,%20pic_square%20FROM%20user%20WHERE%20has_added_app=1%20and%20uid%20IN%20(SELECT%20uid2%20FROM%20friend%20WHERE%20uid1%20=%20805037276)&access_token="+ accessToken;
		console.log(url_friends);
		$.get(url_friends, null, function (data) {
			friends_obj = $.parseJSON(data);
			for (i = 0; i < 2; i++) {
				$("#friends_list").append("<li><a href=''><img id='friend_pic_"+i+"' src='"+friends_obj.data[i].pic_square+"' align='middle'/><h3 id='friend_name_" + i + "'>"+friends_obj.data[i].name+"</h3></a></li>").trigger("create");
			}
			$("#friends_list").append("<li><a href='#friendsAll'><h3 id='friends_all'> All my friends </h3></a></li>").trigger("create");
			$("#friends_list").listview("refresh");
			for (i = 0; i < friends_obj.data.length; i++) {
				$("#friends_all_page").append("<li><a href=''><h3 id='friend_name_" + i + "'>"+friends_obj.data[i].name+"</h3><img id='friend_pic_"+i+"' src='"+friends_obj.data[i].pic_square+"' /></a></li>").trigger("create");
			}
		});
	}
	var displayFamous = function () {
		$.get(url_friends, null, function (data) {
			friends_obj = $.parseJSON(data);
			for (i = 0; i < 2; i++) {
				$("#friends_list").append("<li><a href=''><img id='friend_pic_"+i+"' src='"+friends_obj.data[i].pic_square+"' align='middle'/><h3 id='friend_name_" + i + "'>"+friends_obj.data[i].name+"</h3></a></li>").trigger("create");
			}
			$("#friends_list").append("<li><a href='#friendsAll'><h3 id='friends_all'> All my friends </h3></a></li>").trigger("create");
			$("#friends_list").listview("refresh");
			for (i = 0; i < friends_obj.data.length; i++) {
				$("#friends_all_page").append("<li><a href=''><h3 id='friend_name_" + i + "'>"+friends_obj.data[i].name+"</h3><img id='friend_pic_"+i+"' src='"+friends_obj.data[i].pic_square+"' /></a></li>").trigger("create");
			}
		});
	}
	
	var eventLogin = function(response) {
		if (alreadyConnected == 1) {
			return;
		}
		if (response.status === 'connected') {
			console.log(response);
			accessToken = response.authResponse.accessToken;
			alreadyConnected = 1;
			displayFriends();
			displayFamous();
			if (profile === undefined) {
				$.get('/api/auth', response.authResponse , function (data) {
					profile = data;
				});	
			}

			$.mobile.changePage("#homeFB", { transition: "slideup" });
		}
		else {
			$.mobile.changePage('#login',  { transition: "slideup" });
		}
	}
	
	FB.Event.subscribe('auth.authResponseChange', eventLogin);
	FB.getLoginStatus(eventLogin);

	$('.FBLogin').click(function() {
		FB.login();
		return false;
	});
});