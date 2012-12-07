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

function ComponentsCtrl($location, $rootScope, $scope, Step) {
  // Init & UI
  if ($rootScope['profile'] === undefined) {
    return $location.path('/auth');
  }
  $('.navbar li.active').removeClass('active');
  $('.navbar li.nav-components').addClass('active');

  // Steps
  $scope.steps = Step.query();

  // - Add new step
  $scope.addStep = function() {
    if ($scope.newStepName === undefined || $scope.newStepIndex === undefined || $scope.newStepType === undefined) {
      return false;
    }

    // TODO Check result
    Step.save({ name: $scope.newStepName, number: $scope.newStepIndex, type: $scope.newStepType });
    $('#stepModal').modal('hide');
    $scope.steps = Step.query();
  };

  // - Remove a step
  $scope.removeStep = function(id) {
    Step.remove({ id: id });
    $scope.steps = Step.query();
  };
}

function OrdersCtrl($location, $rootScope) {
  if ($rootScope['profile'] === undefined) {
    return $location.path('/auth');
  }

  $('.navbar li.active').removeClass('active');
  $('.navbar li.nav-orders').addClass('active');
}