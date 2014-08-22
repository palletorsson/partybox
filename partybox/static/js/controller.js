var myApp = angular.module('myApp', []); 

myApp.controller('MyController', ['$scope', '$http',  function($scope, $http)  {
  $http.get('/getplaylist/').success(function(data) {

    $scope.tracks = data.playlist;
  });

  $http.get('/messages/').success(function(data) {
    $scope.messages = data;
    console.log($scope.messages)   
  });

  $http.get('/tracks/').success(function(data) {
    $scope.songs = data;
    console.log($scope.songs)   
  });
}]);
