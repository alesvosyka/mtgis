

var get_user_list = function(){
  $.getJSON( "/get_user_list", function( data ) {
    var items = [];
    $.each( data, function( nick, id ) {
      items.push( '<input type="checkbox" id='+ id + ' class="user_checkbox">' + nick + '</input><br />' );
    });
 
  $('#user_list').html(items.join(""));
  });
}


$('#create_tournament').ready(get_user_list);

