
function save_definition_title() 
{
    var new_text = $("#edit-title-input").val();
    $("#title-text").text(new_text);
    
    render_katex(document.getElementById("title-text"));

    var json_data = {
        'title' : new_text,
        'definition_id': definition_id           
    };

    $.ajax({
        type: "POST",
        url: save_definition_url,

        data: {
             csrfmiddlewaretoken: csrf_token,
             json: JSON.stringify(json_data)
        },

        success: function (response) {
            // save_prop service's response:
            console.log(response);
            display_django_messages();
        },

        error: function (response) {
            console.log(response);
            display_django_messages();
        }
    });
    
}
    
function add_sketch() 
{
    var json_data = {
        'type' : 'sketch',
        'definition_id' : definition_id
    }

    $.ajax({
        type: "POST",
        url: add_def_to_prop_url,

        data: {
             csrfmiddlewaretoken: csrf_token,
             json: JSON.stringify(json_data)
        },

        success: function (response) {
            display_django_messages();            
            var implication_card_list = document.getElementById("implication-chain-card-list");            
            response = `<div class="col">${response}</div>`;
            implication_card_list.innerHTML = response + implication_card_list.innerHTML;   
        },

        error: function (response) {
            console.log(response);
            display_django_messages();
        }
    });
}