var myApp = angular.module('myApp', []); 

myApp.controller('MyController', ['$scope', '$http',  function($scope, $http)  {

  $http.get('/getplaylist/').success(function(data) {
    $scope.tracks = data.playlist;
  });

  $http.get('/posts/').success(function(data) {
    $scope.posts = data;
  });

  $http.get('/files/').success(function(data) {
    $scope.files = data;
  });

  $http.get('/images/').success(function(data) {
    $scope.images = data;
  });

  $http.get('/tracks/').success(function(data) {
    $scope.songs = data;  
  });


  $scope.trackClicked = function() {
  	$http.get('/list/'+this.item.pk+'/').success(function(data_1) {
	  $scope.getLastData()
  	});
  }


  $scope.getLastData = function() {
	$http.get('/getplaylist/').success(function(data) {
		var $playlist = $(".playlist");
        var $playlist2 = $(".playlist2");
		var playlist_el = $(".tracklistinsert");
	    var trackslist = data.playlist,
					type = data.type,
		        	track_html = '';
				$.each(trackslist, function(i, track) {
					track_html = track_html  + ("<div class='media post text_fill track_click radio_cat' id='" + track.pk + "'> <span class='glyphicon glyphicon-music'></span>"+ track['title']  + " ( "+ track.author+ " )"+"<span class='small pull-right'> <span class='icon_hover glyphicon glyphicon-chevron-up vote_up' id='"+track['pk']+"'> </span> </span></div>");  
			   });
				$playlist.html('');
	            $playlist2.html('');
	            playlist_el.html('');

				$playlist2.html(track_html);
  				$scope.votes(); 
	});
  }

  $scope.votes = function() {
	
	$('.vote_down').click(function(e){
		var id = this.id;
		$.get("/votetrackdown/"+id+'', function(response) {
		 $scope.getLastData();
  	}); 

	 });

	 $('.vote_up').click(function(e){
		var id = this.id;
		$.get("/votetrackup/"+id+'', function(response) {
		     $scope.getLastData();
  		}); 

 });

  	}


}]);
