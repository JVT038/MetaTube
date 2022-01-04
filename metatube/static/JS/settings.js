$(document).ready(function() {
    socket = io();

    $("#proxy_status").prop('selectedIndex', 0);
    $(".defaultbtn").css('cursor', 'not-allowed');
    $(".defaultbtn").addClass('disabled');
    $(".defaultbtn").attr('disabled', true);
    $("#templatestab").find('tbody').prepend($(".defaulttemplate").parents('tr'))

    if($("#current_hw").val().includes('vaapi')) {
        $("#vaapi_device").parent().removeClass('d-none');
        let vaapi_device = $("#current_hw").val().split(';')[1];
        $("#vaapi_device").val(vaapi_device);
        $("#hardware_acceleration").children('option[value=\'vaapi\']').prop('selected', true);
    } else {
        $("#hardware_acceleration").children('option[value='+$("#current_hw").val()+']').prop('selected', true);
    }

    if($("#spotifycheck").hasAttr('checked')) {
        $("#spotifyrow").removeClass('d-none');
    }

    function addtemplate(data) {
        function setAttributes(element, attributes) {
            Object.keys(attributes).forEach(attr => {
              element.setAttribute(attr, attributes[attr]);
            });
        }
        
        let tr_visible = document.createElement('tr');
        let tr_hidden = document.createElement('tr');
        let td_hidden = document.createElement('td');
        let p_hidden = document.createElement('p');
        let td_name = document.createElement('td');
        let td_type = document.createElement('td');
        let td_extension = document.createElement('td');
        let td_output_folder = document.createElement('td');
        let td_output_name = document.createElement('td');
        let td_buttons = document.createElement('td');
        let defaultbtn = document.createElement('button');
        let editbtn = document.createElement('button');
        let deletebtn = document.createElement('button');
        let expandbtn = document.createElement('button');
        let defaulticon = document.createElement('i');
        let editicon = document.createElement('i');
        let deleteicon = document.createElement('i');
        let expandicon = document.createElement('i');

        tr_visible.id = data["id"];
        tr_hidden.id = "hidden_" + data["id"];
        td_hidden.setAttribute('colspan', '7');

        tr_hidden.classList.add('d-none');
        td_hidden.classList.add('text-dark');
        td_name.classList.add('text-dark', 'td_name');
        td_type.classList.add('text-dark', 'td_td_type');
        td_extension.classList.add('text-dark', 'td_extension');
        td_output_folder.classList.add('text-dark', 'td_output_folder');
        td_output_name.classList.add('text-dark', 'td_output_name');

        td_name.innerText = data["name"];
        td_type.innerText = data["type"];
        td_extension.innerText = data["ext"];
        td_output_folder.innerText = data["output_folder"];
        td_output_name.innerText = data["output_name"];

        defaultbtn.classList.add('btn', 'btn-info', 'setdefaulttemplate', 'mr-1');
        editbtn.classList.add('btn', 'btn-success', 'changetemplatebtn', 'mr-1');
        deletebtn.classList.add('btn', 'btn-danger', 'deltemplatebtn', 'mr-1');
        expandbtn.classList.add('btn', 'btn-primary', 'expandtemplatebtn', 'mr-1');

        setAttributes(defaultbtn, {
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Set as default template'
        });
        setAttributes(editbtn, {
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Edit template'
        });
        setAttributes(deletebtn, {
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Delete template'
        });
        setAttributes(expandbtn, {
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'Show more info'
        });

        defaulticon.classList.add('bi', 'bi-check-lg');
        editicon.classList.add('bi', 'bi-pencil-square');
        deleteicon.classList.add('bi', 'bi-trash-fill');
        expandicon.classList.add('bi', 'bi-caret-down-fill');

        p_hidden.innerHTML = 'Bitrate: ' + data["bitrate"];

        if(data["type"] == 'Video') {
            p_hidden.innerHTML += '<br/>Width: ' + data["resolution"].split(';')[0] + "<br/>Height: " + data["resolution"].split(';')[1];
        }
        if(data['proxy']["status"] == true) {
            p_hidden.innerHTML += '<br/>Proxy status: True <br/>Proxy type: ' + data["proxy"]["type"] + "<br/>Proxy address: " + data["proxy"]["address"] + "<br/>Proxy port: " + data["proxy"]["port"];
            if(data["proxy"]["username"] != '') {
                p_hidden.innerHTML += "<br/>Proxy username: " + data["proxy"]["username"];
            } else {
                p_hidden.innerHTML += "<br/>Proxy username: None";
            }
            if(data["proxy"]["password"] != '') {
                p_hidden.innerHTML += "<br/>Proxy password: " + data["proxy"]["password"];
            } else {
                p_hidden.innerHTML += "<br/>Proxy password: None";
            }
        } else {
            p_hidden.innerHTML += '<br/>Proxy status: False'
        }

        td_hidden.appendChild(p_hidden);
        tr_hidden.appendChild(td_hidden);

        defaultbtn.appendChild(defaulticon);
        editbtn.appendChild(editicon);
        deletebtn.appendChild(deleteicon);
        expandbtn.appendChild(expandicon);
        td_buttons.append(defaultbtn, editbtn, deletebtn, expandbtn);
        tr_visible.append(td_name, td_type, td_extension, td_output_name, td_output_folder, td_buttons);
        $("#addtemplaterow").before(tr_visible, tr_hidden);
    }

    function changedtemplate(data) {

    }
    
    $(document).on('click', ".templatebtn", function() {
        let goal = $(this).attr('goal');
        let id = $("#templatesmodal").hasAttr('template_id') ? $("#templatesmodal").attr('template_id') : "-1";
        let name = $("#template_name").val();
        let output_folder = $("#template_folder").val();
        let output_name = $("#template_outputname").val();
        let output_ext = $("#template_type").val();
        let bitrate = $("#template_bitrate").val() == '' ? 'best' : $("#template_bitrate").val();
        let width = $("#template_resolution").val() == 'best' ? 'best' : $("#template_width").val();
        let height = $("#template_resolution").val() == 'best' ? 'best' : $("#template_height").val();
        let proxy_json = JSON.stringify({
            'status': $("#proxy_status").val(),
            'type': $("#proxy_type").val(),
            'address': $("#proxy_address").val(),
            'username': $("#proxy_username").val(),
            'password': $("#proxy_password").val(),
            'port': $("#proxy_port").val()
        });

        if($("#template_type option:selected").parent().attr('label') == 'Video' && output_ext == 'm4a') {
            output_ext = 'm4a_video';
        } else if(output_ext == 'm4a') {
            output_ext = 'm4a_audio';
        }

        socket.emit('updatetemplate', name, output_folder, output_ext, output_name, id, goal, bitrate, width, height, proxy_json);
    });

    $("#removetemplatemodal, #templatesmodal").on('hidden.bs.modal', function() {
        $(this).removeClass(['d-flex', 'justify-content-center']); 
    });

    $(document).on('click', '.setdefaulttemplate', function() {
        let id = $(this).parents('tr').attr("id");
        socket.emit('setdefaulttemplate', id);
    });

    $(document).on('click', ".deltemplatebtn", function(e) {
        if($(this).hasClass('defaultbtn')) {
            e.preventDefault();
        } else {
            $("#removetemplatemodaltitle").text('Remove modal \''+ $(this).parent().siblings(':first').text() + '\'');
            $("#removetemplatemodal").find('.btn-danger').attr('id', $(this).parent().parent().attr('id'));
            $("#removetemplatemodal").addClass(['d-flex', 'justify-content-center']);
            $("#removetemplatemodal").modal('show');
        }
    });

    $("#deltemplatebtnmodal").on('click', function(){
        let id = $(this).attr('id');
        socket.emit('deletetemplate', id);
        $("#removetemplatemodal").modal('hide');
    });
    $(document).on('click', 'changetemplatebtn', function(e) {
        if($(this).hasClass('defaultbtn')) {
            e.preventDefault();
        } else {
            let id = $(this).parent().parent().attr('id');
            socket.emit('fetchtemplate', id);
            $("#templatesmodal").addClass(['d-flex', 'justify-content-center']);
            $("#templatesmodal").modal("show");
        }
    });
    $("#addtemplatemodalbtn").on('click', function() {
        $("#templatesmodal").children().children().children('.modal-header').children('h5').text('Add template');
        $("#templatesmodal").removeAttr('template_id');
        $("#template_name, #template_folder, #proxy_address, #proxy_username, #proxy_port, #proxy_password").val("");
        $("#template_bitrate").val('');
        $("#template_height, #template_width").val('best');
        $("#changetemplatebtn").attr('id', 'addtemplatebtn');
        $("#addtemplatebtn").text('Add template');
        $("#addtemplatebtn").attr('goal', 'add');
        $("#templatesmodal").addClass(['d-flex', 'justify-content-center']);
        $("#templatesmodal").modal("show");
        $("#advancedtoggle").text('Show advanced');
        $("#advancedrow, .videocol").addClass('d-none');
        $("#proxy_status").val('false').trigger('click');
        $("#proxyrow").children().not(':first').addClass('d-none');
        $("#template_type, #proxy_type").val([]);
    });

    $("#template_type").on('change', function() {
        if($(':selected', $(this)).parent().attr('label') == 'Video') {
            $(".videocol").removeClass('d-none');
        } else {
            $(".videocol").addClass('d-none');
        }
    });

    $("#advancedtoggle").on('click', function() {
        if($("#advancedrow").hasClass('d-none')) {
            $(this).text('Hide advanced');
        } else {
            $(this).text('Show advanced');
        }
        $("#advancedrow").toggleClass('d-none');
    });

    $("#proxy_status").on('change', function() {
        $("#proxyrow").children('div.col:not(:first)').toggleClass('d-none');
    });

    $(document).on('click', '.expandtemplatebtn', function() {
        let id = $(this).parents('tr').attr('id');
        $(this).parents('tr').siblings('#hidden_'+id).toggleClass('d-none');
        
    });

    $(".custom-control-label").on('click', function() {
        $(this).siblings('.metadatainput').trigger('click');
    });

    $(".metadatainput").on('change', function() {
        if($(this).val() == 'spotify') {
            if($(this).is(':checked')) {
                $("#spotifyrow").removeClass('d-none');
            } else {
                $("#spotifyrow").addClass('d-none');
            }
        }
    });

    $("#submitdownloadform").on('click', function() {
        let amount = $("#max_amount").val();
        let ffmpeg_path = $("#ffmpeg_path").val();
        let hardware_transcoding = $("#hardware_acceleration").val();
        let extradata = {};
        if(hardware_transcoding == 'vaapi') {
            hardware_transcoding += ';'+$("#vaapi_device").val();
        };
        let metadata_sources = $('.metadatainput:checked').map(function() {
            return this.value;
        }).get();
        if(metadata_sources.indexOf('spotify') > -1)  {
            if($("#spotifyclientSecret").val() == '' || $("#spotifyclientID").val() == '') {
                $("#downloadsettingslog").find('p').text('Enter the Spotify API credentials!');
                return false;
            } else {
                extradata["spotifyapi"] = {
                    'id': $("#spotifyclientID").val(),
                    'secret': $("#spotifyclientSecret").val()
                };
            }
        }
        socket.emit('updatesettings', ffmpeg_path, amount, hardware_transcoding, metadata_sources, extradata);
    });

    $("#hardware_acceleration").on('change', function() {
        if($(this).val() == 'vaapi') {
            $("#vaapi_device").parent().removeClass('d-none');
        } else {
            $("#vaapi_device").parent().addClass('d-none');
        }
    });

    $("#template_resolution").on('change', function() {
        if($(this).val() != 'best') {
            let width = $(this).val().split(';')[0];
            let height = $(this).val().split(';')[1];
            $("#template_width").val(width);
            $("#template_height").val(height);
            $(".videocol").not($(this).parent()).removeClass('d-none');
        } else {
            $(".videocol").not($(this).parent()).addClass('d-none');
        }
    });

    $("#togglesecret").on('click', function() {
        if($("#spotifyclientSecret").attr('type') == 'password') {
            $("#spotifyclientSecret").attr('type', 'text');
        } else {
            $("#spotifyclientSecret").attr('type', 'password');
        }
    });

    socket.on('downloadsettings', function(msg) {
        $("#downloadsettingslog").find("p").html(msg);
    });

    socket.on('templatesettings', function(msg) {
        $("#templateslog").text(msg.msg);
        if(msg.status == 'delete') {
            $("tr#"+msg.templateid).remove();
            $("tr#hidden_"+msg.templateid).remove();
        } else if(msg.status == 'setdefault') {
            $(".defaulttemplate").prop('disabled', false);
            $('.defaulttemplate').attr({'title': 'Set as default template', 'data-original-title': 'Set as default template'})
            $(".defaulttemplate").removeClass(['defaulttemplate', 'disabled']);

            $("tr#"+msg.templateid).find('.setdefaulttemplate').addClass(['defaulttemplate', 'disabled']);
            $("tr#"+msg.templateid).find('.setdefaulttemplate').removeClass('setdefaulttemplate');
            $("tr#"+msg.templateid).find('.defaulttemplate').attr({'title': 'Template is already the default template', 'data-original-title': 'Template is already the default template'})
            $("tr#"+msg.templateid).find('.defaulttemplate').prop('disabled', true);
            
            $(".defaulttemplate").tooltip('hide');
            $("#templatestab").find('tbody').prepend($(".defaulttemplate").parents('tr'));
        } else if(msg.status == 'newtemplate') {
            $("#templatesmodal").modal('hide');
            addtemplate(msg.data);
        }
    });
    
    socket.on('changetemplate', function(msg) {
        $("p#templatemodallog").text(msg);
    });

    socket.on('template', function(response) {
        let data = JSON.parse(response);
        let name = data["name"];
        let output_name = data["output_name"];
        let bitrate = data["bitrate"];
        let width = data["resolution"].split(';')[0];
        let height = data["resolution"].split(';')[1];
        let resolution = data["resolution"];
        let output_folder = data["output_folder"];
        let ext = data["extension"];
        let type = data["type"];
        let id = data["id"];
        $("#templatesmodal").children().children().children('.modal-header').children('h5').text('Edit template \''+name+'\'');
        $("#templatesmodal").attr('template_id', id);
        $("#template_name").val(name);
        $("#template_folder").val(output_folder);
        $("#template_outputname").val(output_name);
        $("#template_bitrate").val(bitrate);
        if(type == 'Audio') {
            $(".videocol").addClass('d-none');
        } else {
            $(".videocol").removeClass('d-none');
            $("#template_width").val(width);
            $("#template_height").val(height);
            $("#template_resolution").children("option[value='"+resolution+"']").prop('selected', true);
        }
        $("#template_type").children('[label=\''+type+'\']').children('[value=\''+ext+'\']').attr('selected', true);
        $("#addtemplatebtn").attr('id', 'changetemplatebtn');
        $("#changetemplatebtn").text('Change template');
        $("#changetemplatebtn").attr('goal', 'edit');
        if(data["proxy_status"] == true) {
            let proxy_type = data["proxy_type"].toUpperCase();
            $("#advancedtoggle").text('Hide advanced');
            $("#advancedrow").removeClass('d-none');
            $("#proxy_status").val('true').trigger('click')
            $("#proxyrow").children().removeClass('d-none');
            $("#proxy_type option[value='"+proxy_type+"']").prop('selected', true);
            $("#proxy_address").val(data["proxy_address"]);
            $("#proxy_port").val(data["proxy_port"])
            $("#proxy_username").val(data["proxy_username"]);
            $("#proxy_password").val(data["proxy_password"]);
        }
        $("#templatesmodal").addClass(['d-flex', 'justify-content-center']);
        $("#templatesmodal").modal("show");
    });
});