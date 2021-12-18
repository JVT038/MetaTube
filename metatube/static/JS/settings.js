$(document).ready(function() {
    socket = io();

    $("#proxy_status").prop('selectedIndex', 0);
    $(".defaultbtn").css('cursor', 'not-allowed');
    $(".defaultbtn").addClass('disabled');
    $(".defaultbtn").attr('disabled', true);

    if($("#current_hw").val().includes('vaapi')) {
        $("#vaapi_device").parent().removeClass('d-none');
        let vaapi_device = $("#current_hw").val().split(';')[1];
        $("#vaapi_device").val(vaapi_device);
        $("#hardware_acceleration").children('option[value=\'vaapi\']').prop('selected', true);
    } else {
        $("#hardware_acceleration").children('option[value='+$("#current_hw").val()+']').prop('selected', true);
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

    $(".deltemplatebtn").on('click', function(e) {
        if($(this).hasClass('defaultbtn')) {
            e.preventDefault();
        } else {
            $("#removetemplatemodaltitle").text('Remove modal \''+ $(this).parent().siblings(':first').text() + '\'');
            $("#removetemplatemodal").find('.btn-danger').attr('id', $(this).parent().parent().attr('id'));
            $("#removetemplatemodal").modal('show');
        }
    });
    $("#deltemplatebtnmodal").on('click', function(){
        let id = $(this).attr('id');
        socket.emit('deletetemplate', id);
        $("tr#"+id).remove();
        $("#removetemplatemodal").modal('hide');
    });
    $(".changetemplatebtn").on('click', function(e) {
        if($(this).hasClass('defaultbtn')) {
            e.preventDefault();
        } else {
            let id = $(this).parent().parent().attr('id');
            socket.emit('fetchtemplate', id);
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
    $(".expandtemplatebtn").on('click', function() {
        let id = $(this).parents('tr').attr('id');
        $(this).parents('tr').siblings('#proxy_'+id).toggleClass('d-none');
        
    });

    $("#submitdownloadform").on('click', function() {
        let amount = $("#max_amount").val();
        let ffmpeg_path = $("#ffmpeg_path").val();
        let hardware_transcoding = $("#hardware_acceleration").val();
        if(hardware_transcoding == 'vaapi') {
            hardware_transcoding += ';'+$("#vaapi_device").val();
        }
        socket.emit('updatesettings', ffmpeg_path, amount, hardware_transcoding);
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

    socket.on('downloadsettings', function(msg) {
        $("#downloadsettingslog").find("p").html(msg);
    });

    socket.on('templatesettings', function(msg) {
        $("#templateslog").text(msg);
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
        if(data["proxy_status"] == 'True') {
            let proxy_type = data["proxy_type"];
            let proxy_address = data["proxy-address"];
            let proxy_port = data["proxy_port"];
            let proxy_username = data["proxy_username"];
            let proxy_password = data["proxy_password"];
            $("#advancedtoggle").text('Hide advanced');
            $("#advancedrow").removeClass('d-none');
            $("#proxy_status").val('true').trigger('click')
            $("#advancedrow").children('.d-none').removeClass('d-none');
            $("#proxy_type option[value='"+proxy_type+"']").attr('selected', 'selected');
            $("#proxy_address").val(proxy_address);
            $("#proxy_port").val(proxy_port)
            $("#proxy_username").val(proxy_username);
            $("#proxy_password").val(proxy_password);
        }
        $("#templatesmodal").modal("show");
    });
});