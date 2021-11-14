$(document).ready(function() {
    var csrf_token = "{{ csrf_token() }}";

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
    $(document).on('click', "#addtemplatebtn", function() {
        let name = $("#template_name").val();
        let output_folder = $("#template_folder").val();
        let output_name = $("#template_outputname").val();
        let output_ext = $("#template_type").val();
        let bitrate = $("#template_bitrate").val();
        $.ajax({
            url: Flask.url_for('settings.template'),
            method: 'POST',
            data: {
                name: name,
                output_folder: output_folder,
                output_name: output_name,
                output_ext: output_ext,
                bitrate: bitrate,
                goal: 'add'
            },
            success: function(response) {
                $("#templatemodallog").text(response);
            }, error: function(error) {
                $("#templatemodallog").text("ERROR: " + error.responseText.slice(1, error.responseText.length -1));
            }
        });
    });
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
    })
    $("#deltemplatebtnmodal").on('click', function(){
        let id = $(this).attr('id');
        $.ajax({
            url: Flask.url_for('settings.deltemplate'),
            method: 'POST',
            data: {
                id: id
            },
            success: function(response) {
                $("#templateslog").text(response);
                $("tr#"+id).remove();
                $("#removetemplatemodal").modal('hide');
            }, error: function(error) {
                $("#templateslog").text(error.responseText);
                $("#removetemplatemodal").modal('hide');
            }
        });
    });
    $(".changetemplatebtn").on('click', function(e) {
        if($(this).hasClass('defaultbtn')) {
            e.preventDefault();
        } else {
            let name = $(this).parent().siblings('.td_name').text();
            let output_name = $(this).parent().siblings('.td_output_name').text();
            let bitrate = $(this).parent().siblings('.td_bitrate').text();
            let output_folder = $(this).parent().siblings('.td_output_folder').text();
            let ext = $(this).parent().siblings('.td_extension').text();
            let type = $(this).parent().siblings('.td_type').text();
            let id = $(this).parent().parent().attr('id');
            $("#templatesmodal").children().children().children('.modal-header').children('h5').text('Edit template \''+name+'\'');
            $("#templatesmodal").attr('template_id', id);
            $("#template_name").val(name);
            $("#template_folder").val(output_folder);
            $("#template_outputname").val(output_name);
            if(type == 'Audio') {
                $("#template_bitrate").val(bitrate);
            } else {
                $("#template_bitrate").val("None");
                $("#template_bitrate").parent().addClass('d-none');
            }
            $("#template_type").children('[label=\''+type+'\']').children('[value=\''+ext+'\']').attr('selected', true);
            $("#addtemplatebtn").attr('id', 'changetemplatebtn');
            $("#changetemplatebtn").text('Change template');
            $("#templatesmodal").modal("show");
        }
    });
    $("#addtemplatemodalbtn").on('click', function() {
        $("#templatesmodal").children().children().children('.modal-header').children('h5').text('Add template');
        $("#templatesmodal").removeAttr('template_id');
        $("#template_name").val("");
        $("#template_folder").val("");
        $("#template_type").val([]);
        $("#template_bitrate").removeClass('d-none');
        $("#changetemplatebtn").attr('id', 'addtemplatebtn');
        $("#addtemplatebtn").text('Add template');
        $("#templatesmodal").modal("show");
    });
    $(document).on('click', "#changetemplatebtn", function() {
        console.log('iets');
        let id = $("#templatesmodal").attr('template_id');
        let name = $("#template_name").val();
        let output_folder = $("#template_folder").val();
        let output_name = $("#template_outputname").val();
        let output_ext = $("#template_type").val();
        let bitrate = $("#template_bitrate").val();
        $.ajax({
            url: Flask.url_for('settings.template'),
            method: 'POST',
            data: {
                name: name,
                output_folder: output_folder,
                output_ext: output_ext,
                output_name: output_name,
                bitrate: bitrate,
                id: id,
                goal: 'edit'
            },
            success: function(response) {
                $("#templatemodallog").text(response);
            }, error: function(error) {
                $("#templatemodallog").text("ERROR: " + error.responseText.slice(1, error.responseText.length -1));
            }
        });
    });
    $("#template_type").on('change', function() {
        if($(':selected', $(this)).parent().attr('label') == 'Video') {
            $("#template_bitrate").parent().addClass('d-none');
        } else {
            $("#template_bitrate").parent().removeClass('d-none');
        }
    });
});