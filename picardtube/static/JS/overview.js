$(document).ready(function() {
    // embed CSRF token in Ajax requests
    var csrftoken = $('meta[name=csrf-token]').attr('content')
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $(document).on('change', '#query_type', function() {
        console.log('iets')
        if($(this).val() == 'url') {
            $("#query").attr('placeholder', 'Enter URL to download')
            $("#supportedsitesanchor").show();
        } else if ($(this).val() == 'mbq') {
            $("#query").attr('placeholder', 'Enter MusicBrainz ID to download')
            $("#supportedsitesanchor").hide();
        }
    });
    $("#queryform").on('submit', function(e) {
        e.preventDefault();
        $("#searchsongbtn").trigger('click');
    });
    $("#searchsongbtn").on('click', function() {
        let validator = $("#queryform").validate()
        // if(validator.element($(this))) {
            var query = $("#query").val()
            $.ajax({
                url: Flask.url_for('search'),
                method: 'GET',
                data: {
                    query: query
                },
                success: function(response) {
                    $("#ytcol").empty();
                    var data = response.info;
                    console.log(response);
                    data = response.info;
                    let id = data.id;
                    let thumbnail = data.thumbnails[data.thumbnails.length - 1].url;
                    let minutes = Math.floor(data.duration / 60);
                    let seconds = data.duration % 60;
                    if(seconds < 10) {
                        seconds = '0' + data.duration % 60;
                    }
                    
                    let length = minutes + ":" + seconds;
                    let html = {
                        'img': '<img class="img-fluid" id="thumbnail_yt" src="'+thumbnail+'" title="Click to watch video" alt="Thumbnail for video '+id+'" onclick="window.open(\''+data.webpage_url+'\', \'_blank\')" style="cursor: pointer" />',
                        'text': '<p>Title: '+data.title+'</br>Length: '+length+'</p>',
                        'input_start': '<div class="form-inline">Start: <input class="form-control" type="text" value="0:00" pattern="[0-9\:]" title="minutes:seconds" />',
                        'input_end': '<div class="form-inline">End: <input class="form-control" type="text" value="'+length+'" pattern="[0-9\:]" title="minutes:seconds" />'
                    }
                    let inject = html['img'] + html['text'] + html['input_start'] + html['input_end'];
                    $("#ytcol").append(inject);
                    $("#query_log").html(response);
                }, 
                error: function(error) {
                    console.log(error.error)
                    if(error.status == 500 && error.error == 'empty') {
                        $("#query_log").html('<p class="text-center">Enter an URL!</p>')
                    }
                }
            })
        // }
    });
})