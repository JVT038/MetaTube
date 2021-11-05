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
    // Option to change the query type - disabled at the moment
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
    // If the user presses Enter or submits the form in some other way, it'll trigger the 'find' button
    $("#queryform").on('submit', function(e) {
        e.preventDefault();
        $("#searchsongbtn").trigger('click');
    });

    function insertYTcol(response) {
        $("#ytcol").empty();
        var data = response;
        let artist = 'artist' in data ? data.artist : "Unknown";
        let track = 'track' in data ? data.track : "Unknown";
        let album = 'album' in data ? data.album : "Unknown";
        let channel = 'channel' in data ? data.channel : data.uploader;
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
            'text': '<p>Video title: '+data.title+'</br>Channel: '+channel+'<br/>Length: '+length+'</br/>Track name: '+track+'<br/>Artist: '+artist+'<br/>Album: '+album+'</p>',
            'input_start': '<div class="row">Start: <div class="form-inline float-right"><input class="form-control float-right" type="text" value="0:00" pattern="[0-9\:]" title="minutes:seconds" /></div></div>',
            'input_end': '<div class="row">End: <div class="form-inline float-right"><input class="form-control" type="text" value="'+length+'" pattern="[0-9\:]" title="minutes:seconds" /></div></div>'
        }
        let inject = html['img'] + html['text'] + html['input_start'] + html['input_end'];
        $("#ytcol").append(inject);
        $("#query_log").html(response);
    }

    function insertMBcol(response) {
        console.log(response);
        $.each(response, function(value, key) {
            let release_id = key.id;
            let title = key.title;
            let artists = key["artist-credit"];
            console.log(artists)
            $.ajax({
                url: Flask.url_for('findcover'),
                method: 'GET',
                data: {
                    id: release_id
                },
                success: function(response) {
                    console.log(response);
                    console.log('iets');
                }, 
                error: function(error) {
                    console.log(error.error)
                    if(error.status == 500 && error.error == 'empty') {
                        $("#query_log").html('<p class="text-center">Enter an URL!</p>')
                    }
                }
            })
        });
    }

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
                    info = response;
                    insertYTcol(response.yt);
                    insertMBcol(response.mbp);
                    $(".modal-footer").removeClass('d-none')
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