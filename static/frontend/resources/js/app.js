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
    if (response.status === 'connected') {
      accessToken = response.authResponse.accessToken;
      if (profile.api_key === undefined) {
        if ($.mobile.activePage.data('url') !== 'splash') {
          $.mobile.changePage("#splash", { transition: "pop" });
        }
        $.get('/api/auth', response.authResponse, function (data) {
          profile = JSON.parse(data);
          $('.user-logged').show();
          $.mobile.changePage("#homeFB", { transition: "slideup" });
        }); 
      }
    }
    else {
      $('.user-logged').hide();
      FB.Event.subscribe('auth.authResponseChange', eventLogin);
      $.mobile.changePage('#login',  { transition: "slideup" });
    }
  }
  
  FB.getLoginStatus(eventLogin);

  $('.FBLogin').click(function() {
    FB.login();
    return false;
  });

  $('.home').click(function() {
    if (profile.api_key === undefined) {
      $.mobile.changePage('#login',  { transition: "slideup" });
    }
    else {
      $.mobile.changePage('#homeFB',  { transition: "slideup" });
    }
    return false;
  });

  // Helpers
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

  var pad2 = function(number) {
    return (number < 10 ? '0' : '') + number;
  };

  var getComponentById = function(components, id) {
    for (var i = 0 ; i < components.length ; ++i) {
      if (components[i].id === id) {
        return components[i];
      }
    }

    return null;
  };

  var getComponentIdxById = function(components, id) {
    for (var i = 0 ; i < components.length ; ++i) {
      if (components[i].id === id) {
        return i;
      }
    }

    return null;
  };

  // Helper to calcul order price
  var orderPrice = function(order, components) {
    var price = 0;
    for (var i = 0 ; i < order.components.length ; ++i) {
      price += getComponentById(components, order.components[i]).price;
    }
    return price;
  };

  // Create the new order view
  var newOrderView = function(importOrderComponents, importComponents, importPreviousPage) {
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
          // TDOO: clean redirect to #
          document.location.href = '/';
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
        // New order
        if (importPreviousPage === undefined) {
          newOrder.splice(newOrder.length - 1, 1);
          calculTotal();
          return displayStepView(newOrder.length);
        }
        // From history, favourite, etc.
        else {
          return importPreviousPage();
        }
      });

      $('.order-validate').unbind().click(function() {
        var components = {};
        for (var i = 0 ; i < newOrder.length ; ++i) {
          for (var j = 0 ; j < newOrder[i].components.length ; ++j) {
            components[newOrder[i].components[j].id] = 1;
          }
        }

        $.post('/api/order.json', JSON.stringify({ api_key: profile.api_key, components: components }), function(result) {
          result = JSON.parse(result);
            $('.order-id').text(result['orderId']);
            $.mobile.changePage("#order-completed", { transition: "pop" });

            $('.order-favourite').unbind().click(function() {
              if ($('#order-favourite-name').val() === '') {
                return false;
              }

              $.post('/api/order.json/favourite', JSON.stringify({ api_key: profile.api_key, id: result['orderId'], name: $('#order-favourite-name').val() }), function() {
                $.mobile.changePage("#homeFB", { transition: "slidedown" });
              });
              return false;
            });
        });
      });
    };

    // Init
    $.mobile.loading('show');
    if (importComponents === undefined) {
      $.get('/api/step.json', { api_key: profile.api_key }, function(result) {
        steps = result;
        return displayStepView(0);
      });
    }
    // From history, favourite, etc.
    else {
      // Virtual-step with all components
      steps = [{ index:1, type: 'multi', components: importComponents }];
      
      // Calcul virtual-order
      var components = [], price = 0;
      for (var i = 0 ; i < importOrderComponents.length ; ++i) {
        var cId = getComponentIdxById(importComponents, importOrderComponents[i]);
        components.push({ idx: cId, id: importComponents[cId].id });
        price += importComponents[cId].price;
      }
      newOrder = [{ price: price, components: components }];

      // Total + display
      calculTotal();
      displayOrder();
      $.mobile.changePage('#order', { transition: "slidedown" });
    }

    return false;
  };

  $('.newOrder').click(newOrderView);
  $('.NoFB').click(newOrderView);

  // History Orders
  var historyOrdersView = function() {
    var components, orders, order = $('#history');

    // View
    var updateDisplay = function() {
      var container = order.find('.order-history').empty();
      for (var i = orders.length - 1; i >= 0 ; i--) {
        var date = new Date(orders[i].dateCreated * 1000);
        container.append('<li><a href="" class="history-reorder" order-idx="' + i + '">' + pad2(date.getDay()) + '/' + pad2(date.getMonth() + 1) + '/' + date.getFullYear() +
                         ' <span class="ui-li-count">&pound; '+ toFixed(orderPrice(orders[i], components)) + '</span></a></li>');
      }

      // Re-order an history command
      $('.history-reorder').unbind().click(function() {
        return newOrderView(orders[$(this).attr('order-idx')].components, components, historyOrdersView);
      });

      $.mobile.changePage("#history", { transition: "slideup" });
      container.listview("refresh");
    };

    // Data
    $.getJSON('/api/component.json', { api_key: profile.api_key }, function(result) {
      components = result;
      $.getJSON('/api/order.json', { api_key: profile.api_key, user: profile.id }, function(result) {
        orders = result;
        return updateDisplay();
      });
    });

    $.mobile.loading('show');
  };
  
  $('.historyOrders').click(historyOrdersView);

  // Favourite Orders
  var favouriteOrdersView = function(type) {
    var components, orders, order = $('#favourites');

    var updateDisplay = function() {
      var container = order.find('.order-favourite').empty();
      for (var i = 0 ; i < orders.length ; ++i) {
        // me
        if (orders[i].user === undefined) {
          container.append('<li><a href="" class="favourite-reorder" order-idx="' + i + '">' + orders[i].name +
                           ' <span class="ui-li-count">&pound; '+ toFixed(orderPrice(orders[i], components)) + '</span></a></li>');
        }
        // friends
        else {
          container.append('<li><a href="" class="favourite-reorder" order-idx="' + i + '"><img src="' +  orders[i].user.pic_square + '" /><h3>' + orders[i].name +
                           '</h3><p>By ' + orders[i].user.name + '</p> <span class="ui-li-count">&pound; '+ toFixed(orderPrice(orders[i], components)) + '</span></a></li>');
        }
      }

      // Re-order an favourite command
      $('.favourite-reorder').unbind().click(function() {
        return newOrderView(orders[$(this).attr('order-idx')].components, components, function() {
          return favouriteOrdersView(type);
        });
      });

      $.mobile.changePage("#favourites", { transition: "slideup" });
      container.listview("refresh");
    };

    // Data
    $.getJSON('/api/component.json', { api_key: profile.api_key }, function(result) {
      components = result;

      order.find('h1').hide();
      // My favourites
      if (type === 'me') {
        order.find('.me').show();
        $.getJSON('/api/order.json', { api_key: profile.api_key, user: profile.id, filter: 'favourite' }, function(result) {
          orders = result;
          return updateDisplay();
        });
      }
      else if (type === 'friends') {
        order.find('.friends').show();

        var fql = 'SELECT name, uid, pic_square FROM user WHERE has_added_app = 1 and uid IN (SELECT uid2 FROM friend WHERE uid1 = me())',
            friends, fcur = 0;
        
        var getFriendsFavourites = function(uid, idx) {
          $.getJSON('/api/order.json', { api_key: profile.api_key, user: uid, filter: 'favourite' }, function(result) {
            friends[idx].orders = result;
            if (++fcur === friends.length) {
              return getTopFriendsFavourites();
            }
          });
        };

        var getTopFriendsFavourites = function() {
          // Set up an array of orders with ref on users
          orders = [];
          for (var i = 0 ; i < friends.length ; ++i) {
            for (var j = 0 ; j < friends[i].orders.length ; ++j) {
              orders.push(friends[i].orders[j]);
              orders[orders.length - 1].user = friends[i];
            }
          }

          // Sort orders by hit
          var sortByHit = function(a, b) {
            if (a.nbVote > b.nbVote) return -1;
            if (a.nbVote < b.nbVote) return 1;
            return 0;
          };
          orders.sort(sortByHit);

          // Display orders
          return updateDisplay();
        };

        // Load FB graph
        $.getJSON('https://graph.facebook.com/fql?access_token=' + profile.access_token + '&q=' + encodeURIComponent(fql), function(graph) {
          friends = graph.data;
          for (var i = 0 ; i < friends.length ; ++i) {
            getFriendsFavourites(friends[i].uid, i);
          }
        });

        // var url_friends =  "https://graph.facebook.com/fql?q=SELECT%20name,%20uid,%20pic_square%20FROM%20user%20WHERE%20has_added_app=1%20and%20uid%20IN%20(SELECT%20uid2%20FROM%20friend%20WHERE%20uid1%20=%20805037276)&access_token="+ accessToken;
        // $.get(url_friends, null, function (data) {
        //   friends_obj = $.parseJSON(data);
        //   for (i = 0; i < 2; i++) {
        //     $("#friends_list").append("<li><a href=''><img id='friend_pic_"+i+"' src='"+friends_obj.data[i].pic_square+"' align='middle'/><h3 id='friend_name_" + i + "'>"+friends_obj.data[i].name+"</h3></a></li>").trigger("create");
        //   }
        //   $("#friends_list").append("<li><a href='#friendsAll'><h3 id='friends_all'> All my friends </h3></a></li>").trigger("create");
        //   $("#friends_list").listview("refresh");
        //   for (i = 0; i < friends_obj.data.length; i++) {
        //     $("#friends_all_page").append("<li><a href=''><h3 id='friend_name_" + i + "'>"+friends_obj.data[i].name+"</h3><img id='friend_pic_"+i+"' src='"+friends_obj.data[i].pic_square+"' /></a></li>").trigger("create");
        //   }
        // });
      }
    });

    $.mobile.loading('show');
    return false;
  };
  $('.favouriteOrders').unbind().click(function() { return favouriteOrdersView('me'); });
  $('.favouriteFriendsOrders').unbind().click(function() { return favouriteOrdersView('friends'); });
});