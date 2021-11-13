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

    function insertYTcol(response, segments, form) {
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
        if(segments != 'error') {
            segments_array = [];
            segment_data = segments;
            $.each(segments, function(key_segments) {
                json_segment = JSON.parse(segments[key_segments]);
                if(json_segment.actionType == 'skip' && (key_segments == 0 || key_segments == segments.length - 1)) {
                    let skip_segments = [json_segment.segment[0], json_segment.segment[1]];
                    segments_array.push(skip_segments);
                }
            });
        }

        let minutes = Math.floor(data.duration / 60);
        let seconds = data.duration % 60;
        if(seconds < 10) {
            seconds = '0' + data.duration % 60;
        }
        
        let length = minutes + ":" + seconds;
        let html = {
            'img': '<img class="img-fluid d-none d-md-block" id="thumbnail_yt" src="'+thumbnail+'" title="Click to watch video" alt="Thumbnail for video '+id+'" onclick="window.open(\''+data.webpage_url+'\', \'_blank\')" style="cursor: pointer" url="'+data.webpage_url+'" />',
            'text': '<p>Video title: '+data.title+'</br>Channel: '+channel+'<br/>Length: '+length+'</br/>Track name: '+track+'<br/>Artist: '+artist+'<br/>Album: '+album+'</p>',
            'input_start': '<div class="form-row"><label class="align-middle" for="input_start_minutes">Start download at</label><div class="col form-group"><input id="input_start_minutes" class="form-control num_input" type="text" value="00" pattern="[0-9]" title="minutes" /></div>:<div class="col form-group"><input id="input_start_seconds" class="form-control num_input" type="text" value="00" pattern="[0-9]" title="seconds" /></div></div>',
            'input_end': '<div class="form-row"><label class="align-middle" for="input_end_minutes">End download at</label><div class="col form-group"><input id="input_end_minutes" class="form-control num_input" type="text" value="'+minutes+'" pattern="[0-9]" title="minutes" /></div>:<div class="col form-group"><input id="input_end_seconds" class="form-control num_input" type="text" value="'+seconds+'" pattern="[0-9]" title="seconds" /></div></div>'
        }
        let inject = html['img'] + html['text'] + form;
        $("#ytcol").empty();
        return inject;
    }

    function insertAudioCol(mbp_data) {
        let ul = document.createElement('ul');
        ul.classList.add('list-unstyled');
        $.each(mbp_data, function(key_release, value_release) {
            let release_id = value_release.id;
            let title = value_release.title;
            let artists = value_release['artist-credit'].length > 1 ? "Artists: <br />" : "Artist: ";
            let date = value_release.date;
            let language = ""
            if("text-representation" in value_release) {
                if("language" in value_release["text-representation"]) {
                    language =  value_release["text-representation"]["language"]
                } else {
                    language = "Unknown"
                }
            } else {
                language = "Unknown"
            }
            // let language = !"text-representation" in value_release ? "Unknown" : ("language" in value_release["text-represenation"] ? value_release["text-representation"]["language"] : "Unknown");
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
                    html = {
                        'img': '<img src="'+mbp_image+'" class="align-self-center mr-3" alt="Thumbnail for '+release_id+'"/>',
                        'desc': '<div class="media-body"><h5 class="mt-0 mb-1"><a href="'+mbp_url+'" target="_blank">'+title+'</a></h5><p>'+artists+'Type: '+release_type+'<br/>Date: '+date+'<br/>Language: '+language+'</p></div>',
                        'checkbox': '<div class="input-group-text"><input class="audiocol-checkbox" type="radio" aria-label="Radio button for selecting an item"></div>',
                    }
                    let list = '<li class="media mbp-item" style="cursor: pointer" id="'+release_id+'">'+html['img']+html['desc']+html['checkbox']+'</li>';
                    ul.insertAdjacentHTML('afterbegin', list);
                }, 
                error: function(error) {
                    console.log(error)
                }
            })
        });
        $("#audiocol").empty();
        return ul;
    }
    $("#searchsongbtn").on('click', function() {
        let spinner = '<div class="d-flex justify-content-center"><div class="spinner-border text-success" role="status"><span class="sr-only">Loading...</span></div></div>';
        $("#ytcol").empty().append(spinner);
        $("#audiocol").empty().append(spinner);
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
                let ytcol = insertYTcol(response.yt, response.segments, response.downloadform);
                let audiocol = insertAudioCol(response.mbp);
                $("#ytcol").append(ytcol);
                $("#audiocol").append(audiocol);
                $(".modal-footer").removeClass('d-none')
            }, 
            error: function(error) {
                $("#ytcol").empty();
                $("#audiocol").empty();
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
    $(document).on('change', '#template', function() {
        let id = $(this).val();
        $.ajax({
            url: Flask.url_for('overview.fetchtemplate'),
            method: 'GET',
            data: {
                id: id
            },
            success: function(response) {
                data = response;
                $("#extension").val([]);
                $("#extension").children('[label=\''+response.type+'\']').children('[value=\''+response.extension+'\']').prop('selected', true);
                $("#type").val(response.type);
                $("#output_folder").val(response.output_folder);
                $("#outputname").val(response.output_name);
                $("#bitrate").val(response.bitrate);
                if(response.type == 'Video') {
                    $("#bitrate").parent().addClass('d-none');
                } else {
                    $("#bitrate").parent().removeClass('d-none');
                }
            }, 
            error: function(error) {
                $("#ytcol").empty();
                $("#audiocol").empty();
                if(error.status == 400) {
                    $("#query_log").html('<p class="text-center">'+error.responseText+'</p>')
                }
            }
        });
    });
    $("#downloadbtn").on('click', function(e) {
        if($(".audiocol-checkbox:checked").length < 1) {
            e.preventDefault();
            $("#progress_status").removeClass('d-none');
            $("#progress_status").children('p').text('Select a release on the right side before downloading a video');
        } else {
            let url = $("#thumbnail_yt").attr('url');
            let ext = $("#extension").val();
            let output_folder = $("#output_folder").val();
            let type = $("#type").val();
            let output_format = $("#outputname").val();
            let bitrate = $("#bitrate").val();
    
            $.ajax({
                url: Flask.url_for('overview.download'),
                method: 'POST',
                data: {
                    url: url,
                    ext: ext,
                    output_folder: output_folder,
                    type: type,
                    output_format: output_format,
                    bitrate: bitrate
                },
                error: function(error) {
                    console.log(error);
                }
            })
        }
    });

    var socket = io();
    socket.on('overview', function(msg) {
        progress_text = $("#progress_status").children('p');
        if(msg.status == 'downloading') {
            if(msg.total_bytes != 'Unknown') {
                let percentage = (msg.downloaded_bytes / msg.total_bytes) * 100;
                $("#ytdl_progress").parent().removeClass('d-none');
                $("#ytdl_progress").attr('aria-valuenow', percentage+"%");
                $("#ytdl_progress").text(percentage);
                $("#ytdl_progress").css('width', parseInt(percentage)+'%');
            } else {
                if($("#progress_status").hasClass('d-none')) {
                    progress_text.empty();
                    $("#progress_status").removeClass('d-none');
                    progress_text.append('Downloading... <br/>');
                }
            }
        }
        else if(msg.status == 'Finished download') {
            if(msg.total_bytes != 'Unknown') {
                $("#ytdl_progress").attr('aria-valuenow', 100);
                $("#ytdl_progress").text("100%");
                $("#ytdl_progress").css('width', '100%');
            } else {
                progress_text.append('Finished downloading!<br/>');
            }
        } else if(msg.status == 'processing') {
            progress_text.append('Processing and converting file to desired format... <br/>');
        } else if(msg.status == 'finished_ffmpeg') {
            progress_text.append('Finished converting!<br/>');
            let release_id = $(".audiocol-checkbox:checked").parent().parent().attr('id');
            let filepath = msg.filepath;
            socket.emit('merge', {
                'release_id': release_id,
                'filepath': filepath
            });
        }
    });
})