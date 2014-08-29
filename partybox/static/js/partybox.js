$(function() {

$(".post").submit(function(event){

var data = new FormData(this);
console.log(this)
event.preventDefault();
	$.ajax({
		type:"POST",
		url:"/add/",
		data: data,
        
		cache: false,
		processData: false,
		contentType: false,
		success: function(data) {
		    $.getJSON( "/getlists/", function( data ) {
				console.log(data)
		        var stream = $.parseJSON(data.stream);
				var message_list = $(".text_stream");
				var image_list = $(".image_stream");
				var track_list = $(".track_stream");
				// check length		            
				$('#messageModal').modal('hide');	
				$('#myModal').modal('hide');
				$('#audioModal').modal('hide');

				$.each(stream, function(i, obj) {
					if (obj.model == "publication.textpost") {
						$("<div class='media post  pull-left  text_fill'><span class='glyphicon glyphicon-pencil'></span>  " + obj.fields['body'] + "<span class='small pull-right message_date'> | " + obj.fields['created'] + "</span></div>").prependTo( message_list);
					}
					if (obj.model == "publication.track") {
						$('<div class="media post text_fill track_click" id="'+obj.fields['pk']+'" > <span class="glyphicon glyphicon-music"></span> <span class="track_title_author"> '+obj.fields['title']+' <br/> By  '+obj.fields['author']+' </div> <span class="small pull-right"> <span class="glyphicon glyphicon-plus track_clicker icon_hover" id="'+obj.fields['pk']+'" > </span> Add </span>').prependTo(track_list);
					}
					if (obj.model == "publication.imagepost") {
						$('<div class="media post pull-left text_fill"><img class="media-object stream_image" src="/media/'+obj.fields['imgfile']+'" alt="image" class="stream_image"> <div class="lable pull-right">'+obj.fields['created']+'</div></div>').prependTo(image_list);
					}
				});			
			}); 
		}	

	});
this.reset();
});




var sound = "on"; 
var ready = function () {
	console.log("ready")

$( ".showform" ).click(function() {
$( ".fileform" ).toggle();
$('input[type=file]').bootstrapFileInput();
$('.file-inputs').bootstrapFileInput();
});

	$('.mute_song').click(function(e){
		if (sound == "on") {
			sound = "off"
			audio.nowPlaying.mute()
		} else {
			sound = "on"
			audio.nowPlaying.unmute()
		} 		 
	});

	$('.vote_down').click(function(e){
		var id = this.id;
		$.get("/votetrackdown/"+id+'', function(response) {
		$.get("/getplaylist/", function(data) {
			update_playlist(data); 
			setTimeout(function(){ready()}, 500);
		});
  	}); 

	 });

	 $('.vote_up').click(function(e){
		var id = this.id;
		$.get("/votetrackup/"+id+'', function(response) {
		    $.get("/getplaylist/", function(data) {
			update_playlist(data);
				setTimeout(function(){ready()}, 500);
  			});
  		}); 

	 });
}

soundManager.setup({
  url: '/static/swf/',
  flashVersion: 9,
  preferFlash: false, // prefer 100% HTML5 mode, where both supported
   useFlashBlock: false,
debugFlash: true,
 
  onready: function() {
 
  console.log('SM2 ready!');
  },
  ontimeout: function() {
    console.log('SM2 init failed!');
  },
  defaultOptions: {
    // set global default volume for all sound objects
    volume: 33
  }
});

function playAudio(playlistId){
    // Default playlistId to 0 if not supplied
    playlistId = playlistId ? playlistId : 0;
    // If SoundManager object exists, get rid of it...
    if (audio.nowPlaying){
        audio.nowPlaying.destruct();
        // ...and reset array key if end reached
        if(playlistId == audio.playlist.length){
            playlistId = 0;
        }
    }
    // Standard Sound Manager play sound function...

    soundManager.onready(function() {
        audio.nowPlaying = soundManager.createSound({
            id: 'sk4Audio',
            url: audio.playlist[playlistId],
            autoLoad: true,
            autoPlay: true,
            volume: 10,
			whileplaying: function() {
				if (this.position % 23 < 1 ) {
					var w = parseInt((this.position/this.duration)*200);
					var player_bar_el = $("#playbar"); 		  			 
					player_bar_el.width(w+"px");     
				} 
				if (set_total_width = true) {
					 $("#current_song").width(400); 
					 set_total_width = false;
				}
     
  			},
            // ...with a recursive callback when play completes
			  onload: function() {
                 audio.nowPlaying.setVolume(50);
     
			  },
            onfinish: function(){
				// Push first song at the end of the list 
				// Get last playlist and other posts with jquery . update page and play new song
    		$.getJSON( "/getplaylist/", function( data ) {
		            	var current = data.current;
 						var type = data.type;

		           if (type == "List") {
	  				$.getJSON( "/removetrackfromplaylist/"+current, function( data ) {
						$.get("/getplaylist/", function(data) {
							audio.playlist = ["media/"+data.current_track];
							$(".playing_type").html(data.type);
                            $(".current_song").html("<span class='glyphicon glyphicon-music'></span> | Current track: "+data.playlist[0]['title'] + " by " +  data.playlist[0]['author'] )

				        	playAudio(0);
			                update_playlist(data);
						});	
					});
					} else {
						$.get("/getplaylist/", function(data) {
		                	$(".playing_type").html(data.type);
							audio.playlist = ["media/"+data.current_track];
							$(".current_song").html("<span class='glyphicon glyphicon-music'></span> | Current track: "+data.playlist[0]['title'] + " by " +  data.playlist[0]['author'] )

				        	playAudio(0);
			    			update_playlist(data);
						});	

					}
				});
          
				$.getJSON( "/getlists/", function( data ) {
		            var stream = $.parseJSON(data.stream);
                    console.log(stream)
					var list = $(".stream");
					// check length
					$.each(stream, function(i, obj) {
						if (obj.model == "publication.textpost") {
  							$("<div class='media post'><div class='media-body text_fill'>" + obj.fields['body'] + "</div><span class='small pull-right'>" + obj.fields['created'] + "</span></div>").appendTo(list);
						}
						if (obj.model == "publication.track") {
      						$('<ul id="graphic-playlist" class="graphic"><div class="media post"><li><a href="/media/'+obj.fields['docfile']+' class="exclude sm2_link sm2_paused"> '+obj.fields['title']+'</a></li></div></ul>').appendTo(list);
						}
						if (obj.model == "publication.imagepost") {
      						$('<div class="media post"><img src="/media/'+obj.fields['imgfile']+'" alt="image" class="stream_image"></a></div>').appendTo(list);
						}
				});	

			});

				
		          
            }

        })
    });
}

var set_total_width = true; 
var audio = [];
// Array of files you'd like played


$.get("/getplaylist/", function(data) {
	audio.playlist = ["media/"+data.current_track];
	$(".current_song").html("<span class='glyphicon glyphicon-music'></span> | Current track: "+data.playlist[0]['title'] + " by " +  data.playlist[0]['author'] )
		                	$(".playing_type").html(data.type);
    update_playlist(data); 
	playAudio(0);

});

ready(); 


var update_playlist = function (data) {
		var playlist_el = $(".tracklistinsert");
		var list = data.playlist
        var type = data.type
		playlist_el.html('')
		$.each(list, function(i, track) {
		playlist_el.append("<div class='media post text_fill track_click radio_cat' id='" + track['pk'] + "'> <span class='glyphicon glyphicon-music'></span> "+ track['title']  + " ( "+ track['author']+ " )"+"<span class='small pull-right'> <span class='icon_hover glyphicon glyphicon-chevron-up vote_up' id='"+track['pk']+"'> </span> | <span class='icon_hover glyphicon glyphicon-chevron-down vote_down' id='"+track['pk']+"' ></span></span>");  
	   });
	}
    return "ok"; 
});


