$(document).ready(function() {
    // Numeric only control handler
    jQuery.fn.ForceNumericOnly =
    function()
    {
        return this.each(function()
        {
            $(this).keydown(function(e)
            {
                var key = e.charCode || e.keyCode || 0;
                // allow backspace, tab, delete, enter, arrows, numbers and keypad numbers ONLY
                // home, end, period
                return (
                    key == 8 || 
                    key == 9 ||
                    key == 13 ||
                    key == 46 ||
                    key == 110 ||
                    (key >= 35 && key <= 40) ||
                    (key >= 48 && key <= 57) ||
                    (key >= 96 && key <= 105)) ||
                    (key >= 112 && key <= 123);
            });
        });
    };
    $(document).on('focus', '.num_input', function() {
        $(this).ForceNumericOnly()
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

    function insertYTcol(response, segments) {
        var data = response;
        let artist = 'artist' in data ? data.artist : "Unknown";
        let track = 'track' in data ? data.track : "Unknown";
        let album = 'album' in data ? data.album : "Unknown";
        let channel = 'channel' in data ? data.channel : data.uploader;
        let id = data.id;
        let thumbnail = "";
        $.each(data.thumbnails, function(key_thumbnail, value_thumbnail) {
            if(value_thumbnail.height == "480") {
                thumbnail += value_thumbnail.url;
            }
        });
        segments_array = [];
        segment_data = segments;
        $.each(segments, function(key_segments) {
            json_segment = JSON.parse(segments[key_segments]);
            // segments_array.push(JSON.parse(segments[key_segments]))
            if(json_segment.actionType == 'skip' && (key_segments == 0 || key_segments == segments.length - 1)) {
                let skip_segments = [json_segment.segment[0], json_segment.segment[1]];
                segments_array.push(skip_segments);
            }
        });

        let minutes = Math.floor(data.duration / 60);
        let seconds = data.duration % 60;
        if(seconds < 10) {
            seconds = '0' + data.duration % 60;
        }
        
        let length = minutes + ":" + seconds;
        let html = {
            'img': '<img class="img-fluid d-none d-md-block" id="thumbnail_yt" src="'+thumbnail+'" title="Click to watch video" alt="Thumbnail for video '+id+'" onclick="window.open(\''+data.webpage_url+'\', \'_blank\')" style="cursor: pointer" />',
            'text': '<p>Video title: '+data.title+'</br>Channel: '+channel+'<br/>Length: '+length+'</br/>Track name: '+track+'<br/>Artist: '+artist+'<br/>Album: '+album+'</p>',
            'input_start': '<div class="form-row"><label class="align-middle" for="input_start_minutes">Start download at</label><div class="col form-group"><input id="input_start_minutes" class="form-control num_input" type="text" value="00" pattern="[0-9]" title="minutes" /></div>:<div class="col form-group"><input id="input_start_seconds" class="form-control num_input" type="text" value="00" pattern="[0-9]" title="seconds" /></div></div>',
            'input_end': '<div class="form-row"><label class="align-middle" for="input_end_minutes">End download at</label><div class="col form-group"><input id="input_end_minutes" class="form-control num_input" type="text" value="'+minutes+'" pattern="[0-9]" title="minutes" /></div>:<div class="col form-group"><input id="input_end_seconds" class="form-control num_input" type="text" value="'+seconds+'" pattern="[0-9]" title="seconds" /></div></div>'
        }
        let inject = html['img'] + html['text'] + html['input_start'] + html['input_end'];
        return inject;
    }

    function insertMBcol(mbp_data) {
        let ul = $('<ul class="list-unstyled"></ul>');
        $.each(mbp_data, function(key_release, value_release) {
            let release_id = value_release.id;
            let title = value_release.title;
            let artists = value_release['artist-credit'].length > 1 ? "Artists: <br />" : "Artist: ";
            let date = value_release.date;
            let language = value_release["text-representation"]["language"];
            $.each(value_release["artist-credit"], function(key_artist, value_artist) {
                if(typeof(value_artist) == 'object') {
                    // artists_array[key_artist] = [value_artist.name, value_artist.id]
                    let a = '<a href="https://musicbrainz.org/artist/'+value_artist.artist.id+'" target="_blank">'+value_artist.name+'</a><br/>';
                    artists+=a;
                }
            });
            let release_type = value_release["release-group"].type;
            $.ajax({
                url: Flask.url_for('overview.findcover'),
                method: 'GET',
                data: {
                    id: release_id
                },
                success: function(response) {
                    cover = response;
                    let mbp_url = 'https://musicbrainz.org/release/'+release_id;
                    let mbp_image = response.cover == null ? Flask.url_for('static', {"filename": "images/empty_cover.png"}) : response.cover.images[0].thumbnails.small;
                    let img = $('<img src="'+mbp_image+'" class="align-self-center mr-3" alt="Thumbnail for '+release_id+'"/>');
                    let desc = $('<div class="media-body"><h5 class="mt-0 mb-1"><a href="'+mbp_url+'" target="_blank">'+title+'</a></h5><p>'+artists+'Type: '+release_type+'<br/>Date: '+date+'<br/>Language: '+language+'</p></div>')
                    let checkbox = $('<div class="input-group-text"><input type="radio" aria-label="Radio button for selecting an item"></div>')
                    let list = $('<li class="media mbp-item" style="cursor: pointer;" id="'+release_id+'"></li>');
                    list.prepend(img);
                    list.append(desc);
                    list.append(checkbox);
                    ul.append(list);
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
        var amount = $("#amount").val()
        $.ajax({
            url: Flask.url_for('overview.search'),
            method: 'GET',
            data: {
                query: query,
                amount: amount
            },
            success: function(response) {
                $("#query_log").empty();
                info = response;
                let ytcol = insertYTcol(response.yt, response.segments);
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
    $(document).on('mouseenter', '.mbp-item', function() {
        $(this).css('filter', 'brightness(50%)');
        $(this).css('background-colour', '#009999');
    });
    $(document).on('mouseleave', '.mbp-item', function() {
        $(this).css('filter', '');
        $(this).css('background-colour', 'white');
    });
    $(document).on('click', '.mbp-item', function() {
        let checkbox = $(this).children('.input-group-text').children('input');
        checkbox.prop('checked', true);
        $('.mbp-item input[type=\'radio\']').not(checkbox).prop('checked', false);
    });
})