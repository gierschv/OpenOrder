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
  $scope.editComponentProcess = function() {
    var stepId = $('.ng-components ul.nav li.active').attr('step-id');

    if ($scope.componentName === undefined || $scope.componentPrice === undefined || $scope.componentStock === undefined) {
      return false;
    }
    
    var updateView = function() {
      $('#componentModal').modal('hide');
      loadSteps(function() {
        $('.ng-components ul.nav li[step-id="1"] a').tab('show');
      });
    };

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
  }

  $scope.editComponent = function(stepIdx, componentIdx, componentId) {
    $scope.componentEditing = componentId;
    $scope.componentName = $scope.steps[stepIdx].components[componentIdx].name;
    $scope.componentPrice = $scope.steps[stepIdx].components[componentIdx].price;
    $scope.componentStock = $scope.steps[stepIdx].components[componentIdx].stock;
    $('#componentModal').modal('show');
  };
}

function OrdersCtrl($location, $rootScope) {
  if ($rootScope['profile'] === undefined) {
    return $location.path('/auth');
  }

  $('.navbar li.active').removeClass('active');
  $('.navbar li.nav-orders').addClass('active');
}