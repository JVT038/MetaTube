$(document).ready(function() {
    var csrf_token = "{{ csrf_token() }}";

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
    // form = $("#downloadsform").clone()
    // $("#downloadsform").on('submit', function(e) {
    //     e.preventDefault();
    // });
    $("#testffmpeg").on('click', function() {
        $.ajax({
            url: Flask.url_for('settings.testffmpeg'),
            method: 'GET',
            success: function(response) {
                $("#downloadsettingslog").html('<p class="text-center">'+response+'</p>')
            }
        });
    });
});