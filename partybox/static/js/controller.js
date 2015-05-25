
var myApp = angular.module('myApp', []); 

myApp.controller('MyController', ['$scope', '$http', 'fileUpload',  function($scope, $http, fileUpload)  {

  // 1 Interact with django API
  // get last function posts
  $scope.getLastStream = function() {
	  $http.get('/posts/').success(function(data) {
		$scope.posts = data;
			angular.forEach($scope.posts ,function(value, index){
				if (value.model == 'publication.docpost') {
					var splited = value.fields.docfile.split( '/' );
					value.title = splited[4];
				}
			})
	  });
  }
  
  $scope.getLastStream(); 

  // get the playlist form tracks 	
  $http.get('/getplaylist/').success(function(data) {
    $scope.tracks = data.playlist; 
    $scope.lasttrack = data.current_all; 
  });

  // get track list
  $http.get('/tracks/').success(function(data) {
    $scope.songs = data;  
  });
  
  // get file list
  $http.get('/files/').success(function(data) {
    $scope.files = data;
    angular.forEach($scope.files ,function(value, index){
			var splited = value.fields.docfile.split( '/' );
			value.title = splited[4];
		})

  });
  
  // get image list 
  $http.get('/images/').success(function(data) {
    $scope.images = data;
  });


  // 2 Dom functions
  // toggle fileform
  $scope.toggleFileField = function() {
	  $( ".fileform" ).toggle();
  }
  $scope.showAll = function() {
	  console.log("fuck");
  }

  // iframe for images	  	
  $scope.iframeimage= function(e, i) {
    var target = $('.iframetarget'); 
    console.log(e.target)
    var value = e.target.src
	target.attr('src', value);	
  }

  // 3 playlist functions
  // add track to playlist suggestions 
  $scope.trackClicked = function() {
	$http.get('/list/'+this.item.pk+'/').success(function(data_1) {
	  $scope.getLastPlaylist()
  	});
  }

  // after adding to playlist suggestions update tracks
  $scope.getLastPlaylist = function() {
	$http.get('/getplaylist/')
		.success(function(data) {
		 $scope.tracks = data.playlist;
	});
  }

  // vote for track in playlist suggestions 
  $scope.voteUpClicked = function(id) {
	    // disable voting for 3 sec. 
	    var stop_voting = $(".voting")
	    console.log(stop_voting)
	    stop_voting.attr('disabled','disabled');
	    setTimeout(function() {
			 stop_voting.removeAttr('disabled');
		}, 30000);
	    
		$http.get("/votetrackup/"+id+"/")
			.success(function(data) {
				$scope.getLastPlaylist();
  		}); 
  }
  // 4 fileupload
  // file upload och form submit
  $scope.uploadFile = function(body){
	var file = $scope.myFile;
	var csrfmiddlewaretoken = $("[name='csrfmiddlewaretoken']").val();

	console.log('file is ' + JSON.stringify(file), body, csrfmiddlewaretoken);  
		  
	if (JSON.stringify(file) == undefined)  {
		file = '';
		var has_file = false;
	} else {
		var has_file = true;
	} 
	
	if (body == undefined)  {
		body = ''
		var has_body = false;
	} else {
		var has_body = true;	
	}
		
	var uploadUrl = "/add/";
	// only upload or submit if form has content
	
	if (has_body || has_file) {
		fileUpload.uploadFileToUrl(file, body, csrfmiddlewaretoken, uploadUrl);	
		
	}	
	$('#id_body').val(''); 
	// this is the wrong way to do this but I havent figured out how the service can know about the scope
	setTimeout(function() {
		$scope.getLastStream(); 
	}, 1000);

  };
  // 5 refresh dom
  // upload file from refresh
  $scope.updateDom = function(){
    setTimeout(function() {
		$scope.pageRefresh();
    }, 7000)
   };

  // Function to replicate setInterval using $timeout service.
  $scope.intervalFunction = function(){
    setTimeout(function() {
		$scope.pageRefresh();
    }, 20000)
  };
  
  $scope.pageRefresh = function(){
      $scope.getLastStream(); 
      $scope.getLastPlaylist();
      $scope.intervalFunction(); 
  };
  
  // Kick off the interval
  $scope.intervalFunction();

}]);

// fileupload directive
myApp.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
		         scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);

//fileupload service
myApp.service('fileUpload', ['$http', function ($http) {
    this.uploadFileToUrl = function(file, body, csrfmiddlewaretoken, uploadUrl){
        var fd = new FormData();
        
        fd.append('body', body);
		fd.append('file', file);        
        fd.append('csrfmiddlewaretoken', csrfmiddlewaretoken);

        $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        })
        .success(function(){
			
        })
        .error(function(){
        });
    }
}]);


