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

function LogoutCtrl() {
  $('.navbar').hide();
}

function HomeCtrl($location, $rootScope) {
  if ($rootScope['profile'] === undefined) {
    return $location.path('/auth');
  }

  $('.navbar').show();
  $('.navbar li.active').removeClass('active'); 
  $('.navbar li.nav-home').addClass('active');
}

function ComponentsCtrl($location, $rootScope, $scope, $timeout, Step, Component) {
  // Init & UI
  if ($rootScope['profile'] === undefined) {
    return $location.path('/auth');
  }
  $('.navbar li.active').removeClass('active');
  $('.navbar li.nav-components').addClass('active');

  // Steps
  var loadSteps = function(callback) {
    $scope.steps = Step.query({ api_key: $rootScope['profile']['api_key'] }, function() {
      if (callback !== undefined) {
        $timeout(callback);
      }
    });
  };

  loadSteps();

  // - Add new step
  $scope.addStep = function() {
    if ($scope.newStepName === undefined || $scope.newStepIndex === undefined || $scope.newStepType === undefined) {
      return false;
    }

    // TODO Check result
    Step.save({ api_key: $rootScope['profile']['api_key'],
                name: $scope.newStepName,
                number: $scope.newStepIndex,
                type: $scope.newStepType });

    $('#stepModal').modal('hide');
    return loadSteps();
  };

  // - Remove a step
  $scope.removeStep = function(id) {
    Step.remove({ api_key: $rootScope['profile']['api_key'], id: id });
    return loadSteps();
  };

  // Components
  var stepId;
  var updateView = function() {
      $('#componentModal').modal('hide');
      loadSteps(function() {
        $('.ng-components ul.nav li[step-id="' + stepId + '"] a').tab('show');
      });
    };

  $scope.editComponentProcess = function() {
    stepId = $('.ng-components ul.nav li.active').attr('step-id');

    if ($scope.componentName === undefined || $scope.componentPrice === undefined || $scope.componentStock === undefined) {
      return false;
    }

    // TODO Check result
    Component.save({ api_key: $rootScope['profile']['api_key'],
                     id: $scope.componentEditing,
                     step: stepId,
                     name: $scope.componentName,
                     price: $scope.componentPrice,
                     stock: $scope.componentStock }, updateView);
  };

  $scope.addComponent = function() {
    $scope.componentEditing = null;
    $scope.componentName = '';
    $scope.componentPrice = '';
    $scope.componentStock = '';
    $('#componentModal').modal('show');
  };

  $scope.editComponent = function(stepIdx, componentIdx, componentId) {
    $scope.componentEditing = componentId;
    $scope.componentName = $scope.steps[stepIdx].components[componentIdx].name;
    $scope.componentPrice = $scope.steps[stepIdx].components[componentIdx].price;
    $scope.componentStock = $scope.steps[stepIdx].components[componentIdx].stock;
    $('#componentModal').modal('show');
  };

  $scope.removeComponent = function(componentId) {
    stepId = $('.ng-components ul.nav li.active').attr('step-id');
    Component.remove({ id: componentId }, updateView);
  };
}

function OrdersCtrl($location, $rootScope, $scope, $http, Component, Order) {
  if ($rootScope['profile'] === undefined) {
    return $location.path('/auth');
  }
  $('.navbar li.active').removeClass('active');
  $('.navbar li.nav-orders').addClass('active');

  $scope.updateGraph = function(uid) {
    $scope.graphUsers[uid] = null;
    $http({ method: 'GET', url: 'https://graph.facebook.com/' + uid }).success(function(graph) {
      $scope.graphUsers[uid] = graph;
    });
  };

  $scope.orderDetails = function(id) {
    $scope.detailedOrder = Order.get({ api_key: $rootScope['profile']['api_key'], id: id }, function() {
      if ($scope.detailedOrder.user != null && $scope.graphUsers[$scope.detailedOrder.user] === undefined) {
        $scope.updateGraph($scope.detailedOrder.user);
      }

      $scope.detailedOrderPrice = 0;
      for (var i = 0 ; i < $scope.detailedOrder.components.length ; ++i) {
        $scope.detailedOrderPrice += $scope.getComponentById($scope.detailedOrder.components[i]).price;
      }

      $('#orderModal').modal('show');
    });
  };

  $scope.markSelled = function(id) {
    $('#orderModal').modal('hide');
    Order.sell({ api_key: $rootScope['profile']['api_key'], id: id }, function() {
      $scope.orders = Order.query({ api_key: $rootScope['profile']['api_key'], filter: 'unsold' }, $scope.updateOrdersView);
    });
  };


  $scope.components = Component.query({ api_key: $rootScope['profile']['api_key'] });
  $scope.getComponentById = function(id) {
    for (var i = 0 ; i < $scope.components.length ; ++i) {
      if ($scope.components[i].id === id) {
        return $scope.components[i];
      }
    }
    return null;
  };

  $scope.updateOrdersView = function() {
    for (var i = 0 ; i < $scope.orders.length ; ++i) {
      $scope.orders[i].dateCreated = new Date($scope.orders[i].dateCreated * 1000);
      if ($scope.orders[i].user != null && $scope.graphUsers[$scope.orders[i].user] === undefined) {
        $scope.updateGraph($scope.orders[i].user);
      }
    }
  };

  $scope.graphUsers = {};
  $scope.orders = Order.query({ api_key: $rootScope['profile']['api_key'], filter: 'unsold' }, $scope.updateOrdersView);
}
