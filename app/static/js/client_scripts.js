

var load_page = function(html_string)
{
  var newDoc = document.open("text/html", "replace");
  newDoc.write(html_string);
  newDoc.close();
}
/*
var make_post = function()
{
    var url = $("#savebyround").attr('data-url_for_post')
    var form = $("#form_generator_by_round").serialize()
    $.post(url, form, function(data, status) {load_page(data)})
}

var save_by_round_button = function() 
{ 
 $("#savebyround").click(make_post)
}


*/

function post_by_button (button_id, url, form_id)
{
  console.log(button_id + " " + url )
  $(button_id).click(function(){$.post(url,$(form_id).serialize(), function(data){load_page(data)} )})
}


$(document).ready(function(){ post_by_button( "#save_by_round", $("#save_by_round").attr('data-url_for_post'), "#form_generator_by_round" )});
$(document).ready(function(){ post_by_button( "#delete_round_by_round", $("#delete_round_by_round").attr('data-url_for_post'), "#form_generator_by_round" )});

