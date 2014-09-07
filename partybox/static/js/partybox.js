$(function() {

$(".post").submit(function(event){

var data = new FormData(this);
if (data.body != '') {

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
                if (data.type == "all") {
					message_list.html('')
				}
				$.each(stream, function(i, obj) {
					  console.log(obj.model)
					if (obj.model == "publication.textpost") {
						$("<div class='media post  pull-left  text_fill'><span class='glyphicon glyphicon-pencil'></span> - " + obj.fields['body'] + "<span class='small pull-right message_date'> | " + obj.fields['created'] + "</span></div>").prependTo(message_list);
					} else if (obj.model == "publication.track") {
						$('<div class="text_fill media"> <span class="glyphicon glyphicon-music"></span> <span class="track_title_author"> '+obj.fields['title']+' uploaded </div>').prependTo(message_list);


					} else if (obj.model == "publication.imagepost") {
						$('<div class="media post pull-left text_fill"><img class="media-object stream_image" src="/media/'+obj.fields['imgfile']+'" alt="image" class="stream_image"> <div class="lable pull-right">'+obj.fields['created']+'</div></div>').prependTo(message_list);
					} else if(obj.model == "publication.docpost") {
						$('<div class="text_fill media"><span class="glyphicon glyphicon-file"></span> - <a href="/media/'+obj.fields['docfile']+'" alt="doc"> '+obj.fields['docfile']+'</a>  uploaded</div>').prependTo(message_list);
					} else {
					  console.log(obj.model )
					}
				});			
			}); 
		}	

	});
	$('.file-input-name').html('')
	this.reset();
	}
});


var sound = "on"; 

var ready = function () {

$('input[type=file]').bootstrapFileInput();
$('.file-inputs').bootstrapFileInput();


$( ".showform" ).click(function() {
	$( ".fileform" ).toggle();
});

$().click(function(e){
    console.log(e)
});


$('.mute_song').click(function(e){
    console.log("maju")
	if (sound == "on") {
		sound = "off"
		audio.nowPlaying.mute()
     $('.muteicon').addClass("glyphicon-volume-off").removeClass("glyphicon-volume-up");

	} else {
		sound = "on"
		audio.nowPlaying.unmute()

     $('.muteicon').addClass("glyphicon-volume-up").removeClass("glyphicon-volume-off");
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

function playAudio(playlistId, start_at){
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
				if (this.position % 13 < 1 ) {
					var w = parseInt((this.position/this.duration)*200);
					var player_bar_el = $("#playbar"); 		  			 
					player_bar_el.width(w+"px");  			                       
				} 
				if (set_total_width = true) {
					 //$("#current_song").width(400); 
					 set_total_width = false;
				}
     
  			},
            // ...with a recursive callback when play completes
			  onload: function() {
                 audio.nowPlaying.setVolume(50);
		 		 this.setPosition(start_at); 
                 
     
			  },
            onfinish: function(){
				// Push first song at the end of the list 
				// Get last playlist and other posts with jquery . update page and play new song
    			$.getJSON( "/getplaylist/", function( data ) {
		            	var current = data.current;
 						var type = data.type;
						var remove = data.pk
		                $(".playing_type").html(data.type);
						audio.playlist = ["media/"+data.current_track];
						$(".current_song").html("<span class='glyphicon glyphicon-music'></span> | Current track: "+data.playlist[0]['title'] )
				       
						var start_at = data.start_playing_at

        				console.log(start_at)
 						playAudio(0, start_at);
			    		update_playlist(data);
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

$.get("/getplaylist/", function(data) {
		audio.playlist = ["media/"+data.current_track];
		$(".current_song").html("<span class='glyphicon glyphicon-music'></span> Current track: "+data.playlist[0]['title'] )
				            	$(".playing_type").html(data.type);
		update_playlist(data); 
		var start_at = data.start_playing_at

		playAudio(0, start_at);
        var request_start = false
	});

var set_total_width = true; 
var audio = [];

ready(); 

var update_playlist = function (data) {
		var playlist_el = $(".tracklistinsert");
		var list = data.playlist
        var type = data.type
        var clean = $(".playlist");
        var clean2 = $(".playlist2");
        clean.html('')
        clean2.html('')
		playlist_el.html('')
		$.each(list, function(i, track) {
        if (i > 1) {
		playlist_el.append("<div class='track_click track_fill' id='" + track['pk'] + "'> <span class='glyphicon glyphicon-music'></span> "+ track['title']  + " ( "+ track['author']+ " )"+"<span class='small pull-right'> <span class='icon_hover glyphicon glyphicon-chevron-up vote_up' id='"+track['pk']+"'> </span> </span>");  
}
	   });
	}
    return "ok"; 
});




var request_start = true

