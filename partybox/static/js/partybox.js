$(function() {
	
// 1 soundmanager 
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
					 set_total_width = false;
				}

  			},
            // ...with a recursive callback when play completes
			  onload: function() {
                 audio.nowPlaying.setVolume(50);
		 		 this.setPosition(start_at); 

			  },
              onfinish: function(){
                console.log("onfinish")
				// move song next to current 
				var element_next_name = $('.suggested .track_title_author:first').text();
				$(".current_song").html(element_next_name); 
                var element_next = $('.suggested a:first');
				audio.next = element_next.attr("href");
				audio.playlist = [audio.next];
			 	playAudio(0, 2000);			 	
				// remove the played song from playlist 
				$.getJSON( "/removetrack/", function( data ) {
					// get song url from current dom state. 
					var element_next_name = $('.suggested first').html();
					element_next.parent().hide();
				});						
			  }
        })
    });
}

var request_start = true

setTimeout(function() {   
	    audio.playlist = ['/media/250Hz_44100Hz_16bit_05sec.mp3'];
        playAudio(0, 0);
        var request_start = false
        var element_next = $('.suggested a:first');
		audio.next = [element_next.attr("href")];
		element_next.parent().hide();
		var element_next_name = $('.suggested .track_title_author:first').text();
		$(".current_song").html("kickin' it with a test sound"); 							

}, 1000)
var set_total_width = true; 
var audio = [];

// 2 file upload
	$(".filepost").submit(function(event){

	var data = new FormData(this);
	
		event.preventDefault();
			$.ajax({
				type:"POST",
				url:"/add/",
				data: data,      
				cache: false,
				processData: false,
				contentType: false,
				success: function(data) {
				   console.log(data);
				}	
			});

		$('.file-input-name').html('')
		this.reset();
			
	});
});

