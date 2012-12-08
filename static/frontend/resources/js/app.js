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
      steps = [], newOrder = [], total = 0;

    // Calcul total
    var calculTotal = function() {
      total = 0;
      for (var i = 0 ; i < newOrder.length ; ++i) {
        total += newOrder[i].price;
      }
    };

    // Display a step
    var displayStepView = function(idx) {
      var step = steps[idx];

      //order.find('.content').empty();
      
      // Footer
      orderFooter.find('h4').text(step.name);
      orderFooter.find('.total span').text(toFixed(total));

      // Step description and content
      order.find('.step-desc').hide();
      var container = order.find('.components').empty().append('<fieldset data-role="controlgroup"></fieldset>').find('fieldset');
      if (step.type === 'one') {
        order.find('.step-one').show();
        // Componenents
        for (var i = 0 ; i < step.components.length ; ++i) {
          container.append('<input type="radio" name="components" value="' + step.components[i].id + '" idx="' + i + '" id="component-' + step.components[i].id + '" /><label for="component-' + step.components[i].id + '">' + step.components[i].name + ' <div class="price">&pound; ' + toFixed(step.components[i].price) + '</div></label>');
          if (i === 0) {
            container.find('input').attr('checked', true);
          }
        }
      }
      else {
        order.find('.step-multiple').show();
        for (var i = 0 ; i < step.components.length ; ++i) {
          container.append('<input type="checkbox" name="components" value="' + step.components[i].id + '" idx="' + i + '" id="component-' + step.components[i].id + '" /><label for="component-' + step.components[i].id + '">' + step.components[i].name + ' <div class="price">&pound; ' + toFixed(step.components[i].price) + '</div></label>');
        }
      }

      // Display view
      $.mobile.changePage('#order', { transition: "slidedown" });
      $('#order').trigger('create');

      // Actions
      $('.order-previous').unbind().click(function() {
        // Go back home
        if (idx === 0) {
          $.mobile.changePage('#splash');
          FB.getLoginStatus(eventLogin);
        }
        else {
          newOrder.splice(idx - 1, 1);
          calculTotal();
          return displayStepView(idx - 1);
        }
      });

      $('.order-validate').unbind().click(function() {
        newOrder[idx] = { components: [], price: 0 };

        if (step.type === 'one') {
          var input = order.find('input[type="radio"]:checked');
          newOrder[idx].components.push({ id: input.val() , idx: input.attr('idx') });
          newOrder[idx].price = steps[idx].components[input.attr('idx')].price;
        }
        else {
          $('input[type="checkbox"]:checked').each(function() {
            newOrder[idx].components.push({ id: $(this).val() , idx: $(this).attr('idx') });
            newOrder[idx].price += steps[idx].components[$(this).attr('idx')].price;
          });
        }

        calculTotal();
        if (idx + 1 === steps.length) {
          return displayOrder();
        }
        else {
          return displayStepView(idx + 1);
        }
      });
    };

    // Display order summary
    var displayOrder = function() {
      order.find('.step-desc').hide();
      order.find('.step-summary').show();

      // Footer
      orderFooter.find('h4').text('Order summary');
      orderFooter.find('.total span').text(toFixed(total));

      var container = order.find('.components').empty().append('<ul class="order-summary" data-role="listview"></ul>').find('ul');
      for (var i = 0 ; i < newOrder.length ; ++i) {
        for (var j = 0 ; j < newOrder[i].components.length ; ++j) {
          var component = newOrder[i].components[j];
          container.append('<li>' + steps[i].components[component.idx].name + ' <span class="ui-li-count">&pound; '+ toFixed(steps[i].components[component.idx].price) + '</span></li>');
        }
      }

      $.mobile.changePage('#order', { transition: "slidedown" });
      $('#order').trigger('create');

      // Actions
      $('.order-previous').unbind().click(function() {
        newOrder.splice(newOrder.length - 1, 1);
        calculTotal();
        return displayStepView(newOrder.length);
      });

      $('.order-validate').unbind().click(function() {
        console.log('Validation:', newOrder);
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