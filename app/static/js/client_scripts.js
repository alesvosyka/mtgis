


function make_user_table_from_JSON(json_user_list) 
{
	var items = [];
    $.each( json_user_list, 
    		function( nick, id ) 
    	   		{
    				items.push( '<input type="checkbox" id='+ id + ' class="user_checkbox">' + nick + '</input><br />' );
    	   		}
    	  );	
   	return items 		
}


function get_user_list()
{
  $.getJSON( "/get_user_list", data);
  return data
}


$('#create_tournament').ready( make_user_table_from_JSON(get_user_list));

