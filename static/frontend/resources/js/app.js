$(document).ready(function() {
 // Handler for .ready() called.
  FB.init({
    appId      : '530821850262515', // App ID
    channelUrl : '//open-order.appspot.com/static/common/views/channel.html', // Channel File
    status     : true, // check login status
    cookie     : true, // enable cookies to allow the server to access the session
    xfbml      : true  // parse XFBML
  });
 
  var accessToken, profile = {};
  var eventLogin = function(response) {
    console.log(response);
    if (response.status === 'connected') {
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

    // console.log(response.authResponse);
    
    // $.get('https://graph.facebook.com/me/friends?access_token=' + response.authResponse.accessToken, null, function (data) {
    //  console.log('hello');
    //  console.log(data);
    // });


    //$.get()
    //$fql_queryurl"SELECT uid FROM user WHERE has_added_app=1 and uid IN (SELECT uid2 FROM friend WHERE uid1 = $user)"
    // /fql?q=query 
  };

  // Facebook events
  FB.Event.subscribe('auth.authResponseChange', eventLogin);
  FB.getLoginStatus(eventLogin);

  $('.FBLogin').click(function() {
    FB.login();
    return false;
  });

  // Format prices
  var toFixed = function(value, precision) {
      var precision = precision || 2,
      neg = value < 0,
      power = Math.pow(10, precision),
      value = Math.round(value * power),
      integral = String((neg ? Math.ceil : Math.floor)(value / power)),
      fraction = String((neg ? -value : value) % power),
      padding = new Array(Math.max(precision - fraction.length, 0) + 1).join('0');

      return precision ? integral + '.' +  padding + fraction : integral;
  };

  // Create the new order view
  var newOrderView = function() {
    var order = $('#order'), orderFooter = order.find('div[data-role="footer"]'),
      steps = [], total = 0;

    // Display a step
    var displayStepView = function(idx) {
      var step = steps[idx];

      console.log(step);
      order.find('.content').empty();
      
      // Footer
      orderFooter.find('h4').text(step.name);
      orderFooter.find('.total span').text(toFixed(total));

      // Step description and content
      order.find('.step-desc').hide();
      if (step.type === 'one') {
        order.find('.step-one').show();

        // Componenents
        var container = order.find('.components').empty().append('<fieldset data-role="controlgroup"></fieldset>').find('fieldset');
        for (var i = 0 ; i < step.components.length ; ++i) {
          container.append('<input type="radio" name="components" value="' + step.components[i].id + '" id="component-' + step.components[i].id + '" /><label for="component-' + step.components[i].id + '">' + step.components[i].name + ' <div class="price">' + toFixed(step.components[i].price) + ' &pound;</div></label>');
          if (i === 0) {
            container.find('input').attr('checked', true);
          }
        }
      }
      else {
        order.find('.step-multiple').show();
      }

      // Display view
      $.mobile.changePage('#order', { transition: "slidedown" });
      $('#order').trigger('create');

      // Actions
      $('.order-previous').click(function() {
        // Go back home
        if (idx === 0) {
          $.mobile.changePage('#splash');
          FB.getLoginStatus(eventLogin);
        }
      });
    };

    // Init
    $.mobile.loading('show');
    $.get('/api/step.json', { api_key: profile.api_key }, function(result) {
      steps = result;
      return displayStepView(0);
    });
  };

  $('.newOrder').click(newOrderView);
});