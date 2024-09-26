
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

function remove_prop(prop_id)
{
    var json_data = {
        'definition_id': definition_id,
        'prop_id': prop_id,
    }
    
    $.ajax({
        type: "POST",
        url: remove_prop_from_def_url,
        data: {
            csrfmiddlewaretoken: csrf_token,
            json: JSON.stringify(json_data)
        },
        success: function (response)
        {
            display_django_messages();
            var prop = document.getElementById(`prop-id-${prop_id}`);
            var col = prop.parentNode;            
            col.parentNode.removeChild(col);
        },
        error: function (response)
        {
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
        url: add_sketch_to_def_url,

        data: {
             csrfmiddlewaretoken: csrf_token,
             json: JSON.stringify(json_data)
        },

        success: function (response) {
            display_django_messages();            
            var json_data = response;
            var implication_card_list = document.getElementById("implication-chain-card-list");
            var prop_id = json_data['prop_id'];
            var card_content = json_data['card_content'];
            var card_content = `<div class="col">${card_content}</div>`;
            implication_card_list.innerHTML += card_content;
        },

        error: function (response) {
            console.log(response);
            display_django_messages();
        }
    });
}