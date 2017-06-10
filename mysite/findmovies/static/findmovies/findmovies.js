$(".dropdown-menu li a").click(function(e){
  e.preventDefault();
  $(this).parents(".dropup").find('.btn').html($(this).text() + ' <span class="caret"></span>');
  $(this).parents(".dropup").find('.btn').val($(this).data('value'));
});



$("button#search_movies").click(function(){
    
  $('#pleaseWaitDialog').modal('show');
    
  var query = $(".form-control").val();
  var page = 1;
  console.log(query);
    
  var url = '/findmovies/search_movies/?' + 'query=' + query + '&page=' + page;
  $.ajax({
      type: 'GET',
      url: url,
      success: function(json_str) {
          var responses = JSON.parse(json_str);
          var results = responses['results'];
          
          $("div#search_movies_panel").empty();
          for (i = 0; i < results.length; i++) { 
              console.log(results[i]['poster_path']);
              if (results[i]['poster_path'] != null) {
                  var new_tag = '<a href="#" class="thumbnail" style="display: inline-block; vertical-a  lign: middle;"><input type="text" id="movie_id" style="display:none;" value="' + results[i]['id'] + '" /><input type="text" id="movie_poster" style="display:none;" value="https://image.tmdb.org/t/p/w300_and_h450_bestv2' + results[i]['poster_path'] + '" /><img src="https://image.tmdb.org/t/p/w300_and_h450_bestv2' + results[i]['poster_path'] + '" alt="" style="width: 160px; height: 180px;"></a>'
                  $("div#search_movies_panel").append(new_tag);
              }
          }
          
          $('#pleaseWaitDialog').modal('hide');
      },
  });
    
});



$("#search_movies_panel").on("click", ".thumbnail", function(e){
  e.preventDefault();
  var movie_id = $(this).children("#movie_id").attr('value');
  var movie_poster = $(this).children("#movie_poster").attr('value');
  $(".choose-ref").children("#ref_movie_id").attr('value', movie_id);
  $(".choose-ref").children("#ref_movie_poster").attr('value', movie_poster);
  console.log($(".choose-ref").children("#ref_movie_id").attr('value'));
  console.log($(".choose-ref").children("#ref_movie_poster").attr('value'));
});



$("button#load_ref_movie").click(function(){
    
  $('#pleaseWaitDialog').modal('show');
  
  var movie_id = $(this).prevAll().eq(1).attr('value');
  var movie_poster = $(this).prevAll().eq(0).attr('value');
    
  var url = '/findmovies/get_reference_movie_imdb_id?' + 'movie_id=' + movie_id;
  $.ajax({
      type: 'GET',
      url: url,
      success: function(json_str) {
          console.log(json_str);
          //var list = JSON.parse(json_str);
          
          if (json_str != -1) {
              var new_tag = '<div class="item" style="overflow: hidden;"><input type="text" id="movie_imdb_id" style="display:none;" value="' + JSON.parse(json_str) + '" /><img data-src="holder.js/1140x500/auto/#777:#555/text:First slide" alt="First slide [1140x500]" src="' + movie_poster + '" data-holder-rendered="true" width="190" height="285" align="middle" hspace="120"></div>'
          
              $(".panel-body#ref_panel").append(new_tag);
              
              $('button#similarity_search').removeAttr('disabled');
              //$(this).hide();
              $("button#load_ref_movie").hide();
              $("button#unload_ref_movie").show();
              
          } else {
              //alert("Not enough avaiable information of this movie for analysis!");
              BootstrapDialog.alert({
                  title: 'ERROR',
                  message: 'Not enough avaiable information we can find for this movie!',
                  type: BootstrapDialog.TYPE_DANGER, // <-- Default value is BootstrapDialog.TYPE_PRIMARY
                  closable: true, // <-- Default value is false
                  draggable: true, // <-- Default value is false
                  buttonLabel: 'OK', // <-- Default value is 'OK',
                  callback: function(result) {
                      // result will be true if button was click, while it will be false if users close the dialog directly.
                      //alert('Result is: ' + result);
                  }
              });
          }
          
          $('#pleaseWaitDialog').modal('hide');
      },
  });

});



$("button#unload_ref_movie").click(function(){
  $(".panel-body#ref_panel").children(".item").remove();
  
  $('button#similarity_search').attr('disabled','disabled');
  $(this).hide();
  $("button#load_ref_movie").show();
});



$("ul.dropdown-menu li > a").click(function(e){
    //$('button#dropdownManu1').text(this.innerHTML);
    $("input#dropdown_menu_selected").attr('value', this.innerHTML);
});



$('button#similarity_search').click(function(){

    $('#pleaseWaitDialog').modal('show');
    
    var ref_imdb_id = $("div#ref_panel input#movie_imdb_id").attr('value');
    var movie_pool = $("input#dropdown_menu_selected").attr('value');
    
    
    if (movie_pool == null) {
        BootstrapDialog.alert({
            title: 'ERROR',
            message: 'Please select a type of movies!',
            type: BootstrapDialog.TYPE_DANGER, // <-- Default value is BootstrapDialog.TYPE_PRIMARY
            closable: true, // <-- Default value is false
            draggable: true, // <-- Default value is false
            buttonLabel: 'OK', // <-- Default value is 'OK',
            callback: function(result) {
                // result will be true if button was click, while it will be false if users close the dialog directly.
                //alert('Result is: ' + result);
            }
        });
    }
     
    
    var movie_pool_map = { 'Upcoming movies'   : 'upcoming_movies',
                           'Popular movies'    : 'popular_movies',
                           'Top rated movies'  : 'top_rated_movies',
                           'Now playing movies': 'now_playing_movies' };
    movie_pool = movie_pool_map[movie_pool];
    
    
    var url = '/findmovies/search_similar_movies?'
              + 'ref_imdb_id=' + ref_imdb_id + '&'
              + 'movies_pool=' + movie_pool;
    $.ajax({
        type: 'GET',
        url: url,
        success: function(json_str) {
            var results = JSON.parse(json_str);
            
            $("div#rec_panel").empty();
            
            var tag_container = `
<div id="carousel-example-generic" class="carousel slide" data-ride="carousel">
  <!-- Indicators -->
  <ol class="carousel-indicators"></ol>
  <!-- Wrapper for slides -->
  <div class="carousel-inner" role="listbox"></div>
  <!-- Controls -->
  <a class="left carousel-control" href="#carousel-example-generic" role="button" data-slide="prev">
    <span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>
    <span class="sr-only">Previous</span>
  </a>
  <a class="right carousel-control" href="#carousel-example-generic" role="button" data-slide="next">
    <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
    <span class="sr-only">Next</span>
  </a>
</div>
`
            tag_container = $(tag_container);
            for(var i=0; i < results.length; i++) {
                tag_container.children("ol.carousel-indicators").append($('<li data-target="#carousel-example-generic" data-slide-to="' + i + '" class=""></li>'));
                tag_container.children("div.carousel-inner").append($('<div class="item"><img data-src="holder.js/1140x500/auto/#777:#555/text:First slide" alt="First slide [1140x500]" src="https://image.tmdb.org/t/p/w300_and_h450_bestv2' + results[i]['poster_path'] + '" data-holder-rendered="true" width="190" height="190" align="middle" hspace="120"></div>'));
            }
            $("div#rec_panel").append(tag_container);
            $('div#rec_panel .item').first().addClass('active');
            $('div#rec_panel .carousel-indicators > li').first().addClass('active');
            $('div#rec_panel #carousel-example-generic').carousel();  
            
            $('#pleaseWaitDialog').modal('hide');
        },
    });
    
    
});