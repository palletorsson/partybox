$(function() {

var ready = function () {
    $('.track_clicker').click(function(e){
		var id = this.id;
        console.log(id); 

		$.get("/list/"+id+'', function(response) {
			console.log(response);
		  }); 
    });

	 $('.vote_down').click(function(e){
		var id = this.id;
		$.get("/votetrackdown/"+id+'', function(response) {
			console.log(response);
  		}); 
		$.get("/getplaylist/", function(data) {
			var playlist_el = $(".tracklistinsert");
			var list = data.playlist
			playlist_el.html('') 
 
			$.each(list, function(i, track) {


		      playlist_el.append("<div class='track_click radio_cat' id='" + track['pk'] + "'> <span class='glyphicon glyphicon-music'></span>"+ track['title']  + " ( "+ track['author']+ " )"+"<span class='small pull-right'> <span class='icon_hover glyphicon glyphicon-chevron-up vote_up' id='"+track['pk']+"'> </span> | <span class='icon_hover glyphicon glyphicon-chevron-down vote_down' id='"+track['pk']+"' ></span></span>");
              
			});
			ready(); 

  		}); 

	 });

	 $('.vote_up').click(function(e){
		var id = this.id;
		$.get("/votetrackup/"+id+'', function(response) {
			console.log(response);
  		}); 
		$.get("/getplaylist/", function(data) {
			var playlist_el = $(".tracklistinsert");
			var list = data.playlist
			playlist_el.html('') 
 
			$.each(list, function(i, track) {


		      playlist_el.append("<div class='track_click radio_cat' id='" + track['pk'] + "'> <span class='glyphicon glyphicon-music'></span>"+ track['title']  + " ( "+ track['author']+ " )"+"<span class='small pull-right'> <span class='icon_hover glyphicon glyphicon-chevron-up vote_up' id='"+track['pk']+"'> </span> | <span class='icon_hover glyphicon glyphicon-chevron-down vote_down' id='"+list['pk']+"' ></span></span>");
              
			});
			ready(); 

  		}); 

	 });
}
ready(); 

});


