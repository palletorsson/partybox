$(function() {
	

//$(".progress").hide()
// 2 file upload
	$(".filepost").submit(function(event){

	var data = new FormData(this);
	
		event.preventDefault();
			$.ajax({
				xhr: function()
                 {
                 var xhr = new window.XMLHttpRequest();

                 xhr.upload.addEventListener("progress", function(evt){
					 $(".progress").show()
					 if (evt.lengthComputable) {
						 var percentComplete = evt.loaded / evt.total;
						 percentComplete=parseInt(percentComplete*100);
						 console.log(percentComplete);
                         $(".progress-bar").width(percentComplete + "% ");
                         $(".procent").html(" " + percentComplete + "% ")
						 if(percentComplete === 100) {
							$(".progress").hide()
						 }

					 }
					 }, false);

                 return xhr;
                 },
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

