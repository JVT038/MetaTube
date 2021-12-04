$(document).ready(function() {
    socket = io();

    $("#hardware_acceleration").children('option[value='+$("#current_hw").val()+']').prop('selected', true);
    $("#proxy_status").prop('selectedIndex', 0);
    $(".defaultbtn").css('cursor', 'not-allowed');
    $(".defaultbtn").addClass('disabled');
    $(".defaultbtn").attr('disabled', true);
    $(".deltemplatebtn").on('click', function(e) {
        if($(this).hasClass('defaultbtn')) {
            e.preventDefault();
        } else {
            $("#removetemplatemodaltitle").text('Remove modal \''+ $(this).parent().siblings(':first').text() + '\'');
            $("#removetemplatemodal").children().children().children('.modal-footer').children('.btn-danger').attr('id', $(this).parent().parent().attr('id'));
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
        $("#template_name").val("");
        $("#template_folder").val("");
        $("#template_type").val([]);
        $("#template_bitrate").val('192');
        $("#template_height").val('1080');
        $("#template_width").val('1920');
        $("#changetemplatebtn").attr('id', 'addtemplatebtn');
        $("#addtemplatebtn").text('Add template');
        $("#addtemplatebtn").attr('goal', 'add');
        $("#templatesmodal").modal("show");
        $("#advancedtoggle").text('Show advanced');
        $("#advancedrow").addClass('d-none');
        $("#proxy_status").val('false').trigger('click');
        $("#proxyrow").children().not(':first').addClass('d-none');
        $("#proxy_type").val([]);
        $("#proxy_address").val("");
        $("#proxy_port").val("");
        $("#proxy_username").val("");
        $("#proxy_password").val("");
    });
    $(document).on('click', ".templatebtn", function() {
        let goal = $(this).attr('goal');
        let id = $("#templatesmodal").hasAttr('template_id') ? $("#templatesmodal").attr('template_id') : "-1";
        let name = $("#template_name").val();
        let output_folder = $("#template_folder").val();
        let output_name = $("#template_outputname").val();
        let output_ext = $("#template_type").val();
        let bitrate = $("#template_bitrate").val();
        let width = $("#template_width").val();
        let height = $("#template_height").val();
        // let resolution = $("#template_resolution").parent().hasClass('d-none') ? "None" : $("#template_resolution").val();
        let proxy_json = JSON.stringify({
            'status': $("#proxy_status").val(),
            'type': $("#proxy_type").val(),
            'address': $("#proxy_address").val(),
            'username': $("#proxy_username").val(),
            'password': $("#proxy_password").val(),
            'port': $("#proxy_port").val()
        });

        socket.emit('updatetemplate', name, output_folder, output_ext, output_name, id, goal, bitrate, width, height, proxy_json);
    });
    $("#template_type").on('change', function() {
        if($(':selected', $(this)).parent().attr('label') == 'Video') {
            $("#bitratecol").siblings().removeClass('d-none');
        } else {
            $("#bitratecol").siblings().addClass('d-none');
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
        socket.emit('updatesettings', ffmpeg_path, amount, hardware_transcoding);
    });

    $("#template_resolution").on('change', function() {
        let width = $(this).val().split(';')[0];
        let height = $(this).val().split(';')[1];
        $("#template_width").val(width);
        $("#template_height").val(height);
    });

    socket.on('downloadsettings', function(msg) {
        $("#downloadsettingslog").find("p").text(msg);
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
        if(type == 'Audio') {
            $("#template_bitrate").val(bitrate);
            $("#template_resolution").parent().addClass('d-none');
            $("#template_bitrate").parent().removeClass('d-none');
        } else {
            $("#outputrow").children().removeClass('d-none');
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