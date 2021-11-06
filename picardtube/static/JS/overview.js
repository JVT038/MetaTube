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
            'img': '<img class="img-fluid d-none d-md-block" id="thumbnail_yt" src="'+thumbnail+'" title="Click to watch video" alt="Thumbnail for video '+id+'" onclick="window.open(\''+data.webpage_url+'\', \'_blank\')" style="cursor: pointer" />',
            'text': '<p>Video title: '+data.title+'</br>Channel: '+channel+'<br/>Length: '+length+'</br/>Track name: '+track+'<br/>Artist: '+artist+'<br/>Album: '+album+'</p>',
            'input_start': '<div class="row">Start: <div class="form-inline float-right"><input class="form-control float-right" type="text" value="0:00" pattern="[0-9\:]" title="minutes:seconds" /></div></div>',
            'input_end': '<div class="row">End: <div class="form-inline float-right"><input class="form-control" type="text" value="'+length+'" pattern="[0-9\:]" title="minutes:seconds" /></div></div>'
        }
        let inject = html['img'] + html['text'] + html['input_start'] + html['input_end'];
        return inject;
    }

    function insertMBcol(mbp_data) {
        let ul = $('<ul class="list-unstyled"></ul>');
        
        $.each(mbp_data, function(key_release, value_release) {
            let release_id = value_release.id;
            let title = value_release.title;
            let artists = "Artist: ";
            if(value_release["artist-credit"].length > 1) {
                artists = "Artists: <br/>";
            }
            $.each(value_release["artist-credit"], function(key_artist, value_artist) {
                if(typeof(value_artist) == 'object') {
                    // artists_array[key_artist] = [value_artist.name, value_artist.id]
                    let a = '<a href="https://musicbrainz.org/artist/'+value_artist.artist.id+'" target="_blank">'+value_artist.name+'</a><br/>';
                    artists+=a;
                }
            });
            let release_type = value_release["release-group"].type;
            $.ajax({
                url: Flask.url_for('findcover'),
                method: 'GET',
                data: {
                    id: release_id
                },
                success: function(response) {
                    if(response.cover != null) {
                        cover = response;
                        let mbp_url = response.cover.release;
                        let mbp_image = response.cover.images[0].thumbnails.small;
                        let img = $('<img src="'+mbp_image+'" style="cursor: pointer" onclick="window.open(\''+mbp_url+'\', \'_blank\')" class="align-self-center mr-3" alt="Thumbnail for '+release_id+'" title="Click to view on Musicbrainz.org" />');
                        let desc = $('<div class="media-body"><h5 class="mt-0 mb-1">'+title+'</h5><p>'+artists+'Type: '+release_type+'</p></div>')
                        let list = $('<li class="media" id="'+release_id+'"></li>');
                        list.prepend(img);
                        list.append(desc);
                        ul.prepend(list);
                    }
                }, 
                error: function(error) {
                    console.log(error)
                }
            })
        });
        return ul;
    }

    $("#searchsongbtn").on('click', function() {
        let spinner = '<div class="d-flex justify-content-center"><div class="spinner-border text-success" role="status"><span class="sr-only">Loading...</span></div></div>';
        $("#ytcol").empty().append(spinner);
        $("#mbpcol").empty().append(spinner);
        var query = $("#query").val()
        $.ajax({
            url: Flask.url_for('search'),
            method: 'GET',
            data: {
                query: query
            },
            success: function(response) {
                $("#query_log").empty();
                info = response;
                let ytcol = insertYTcol(response.yt);
                let mbpcol = insertMBcol(response.mbp);
                $("#ytcol").empty().append(ytcol);
                $("#mbpcol").empty().append(mbpcol);
                $(".modal-footer").removeClass('d-none')
            }, 
            error: function(error) {
                $("#ytcol").empty();
                $("#mbpcol").empty();
                if(error.status == 400) {
                    $("#query_log").html('<p class="text-center">'+error.responseText+'</p>')
                }
            }
        })
    });
})