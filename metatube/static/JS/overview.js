var socket = io();
$(document).ready(function() {
    // Option to change the query type - disabled at the moment
    // $(document).on('change', '#query_type', function() {
    //     if($(this).val() == 'url') {
    //         $("#query").attr('placeholder', 'Enter URL to download')
    //         $("#supportedsitesanchor").show();
    //     } else if ($(this).val() == 'mbq') {
    //         $("#query").attr('placeholder', 'Enter MusicBrainz ID to download')
    //         $("#supportedsitesanchor").hide();
    //     }
    // });
    // If the user presses Enter or submits the form in some other way, it'll trigger the 'find' button
    $("#queryform").on('submit', function(e) {
        e.preventDefault();
        $("#searchsongbtn").trigger('click');
    });

    function insertYTcol(response, form) {
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

        let minutes = Math.floor(data.duration / 60);
        let seconds = data.duration % 60;
        if(seconds < 10) {
            seconds = '0' + data.duration % 60;
        }
        
        let length = minutes + ":" + seconds;
        let html = {
            'img': '<img class="img-fluid d-none d-md-block" id="thumbnail_yt" src="'+thumbnail+'" title="Click to watch video" alt="Thumbnail for video '+id+'" onclick="window.open(\''+data.webpage_url+'\', \'_blank\')" style="cursor: pointer" url="'+data.webpage_url+'" />',
            'text': '<p>Video title: '+data.title+'</br>Channel: '+channel+'<br/>Length: '+length+'</br/>Track name: '+track+'<br/>Artist: '+artist+'<br/>Album: '+album+'</p>'
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
            $.each(value_release["artist-credit"], function(key_artist, value_artist) {
                if(typeof(value_artist) == 'object') {
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
                    ul.insertAdjacentHTML('beforeend', list);
                }, 
                error: function(error) {
                    console.log(error)
                }
            })
        });
        $("#audiocol").empty();
        console.log(ul);
        return ul;
    }
    $("#searchsongbtn").on('click', function() {
        let spinner = '<div class="d-flex justify-content-center"><div class="spinner-border text-success" role="status"><span class="sr-only">Loading...</span></div></div>';
        $("#ytcol").empty().append(spinner);
        $("#audiocol").empty().append(spinner);
        // YouTube socket
        let query = $("#query").val();
        socket.emit('ytdl_search', query);
    });

    socket.on('ytdl_response', (video, downloadform) => {
        let ytcol = insertYTcol(video, downloadform);
        $("#ytcol").append(ytcol);
        friconix_update();
        $(".modal-footer").removeClass('d-none')
    });
    socket.on('mbp_response', (mbp) => {
        let audiocol = insertAudioCol(mbp);
        $("#audiocol").append(audiocol);
        $(".modal-footer").removeClass('d-none')
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
                if(response.proxy_status == true) {
                    $("#proxy_type").val(response.proxy_type).change();
                    $("#proxy_address").val(response.proxy_address);
                    $("#proxy_port").val(response.proxy_port);
                    $("#proxy_username").val(response.proxy_username);
                    $("#proxy_password").val(response.proxy_password);
                    $("#proxy_row").removeClass('d-none');
                }
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
            var skipfragments = [];
            if(!$("#segments_check").is(':checked')) {
                $.each($('.timestamp_input'), function(key, value) {
                    if(value.id.slice(0, 12) == 'segmentstart') {
                        let id = value.id.slice(13);
                        skipfragments[id] = {'start': value.value}
                    } else if(value.id.slice(0, 10) == 'segmentend') {
                        let id = value.id.slice(11);
                        skipfragments[id].end = value.value;
                    }
                });
                skipfragments = JSON.stringify($.grep(skipfragments,function(n){ return n == 0 || n }));
            }
            let proxy_data = JSON.stringify({
                'proxy_status': $("#proxy_type").val(),
                'proxy_address': $("#proxy_address").val(),
                'proxy_port': $("#proxy_port").val(),
                'proxy_username': $("#proxy_username").val(),
                'proxy_password': $("#proxy_password").val()
            })
            $("#progress_status").siblings('p').empty();
            socket.emit('ytdl_download', 
                url, ext, output_folder, type, output_format, bitrate, skipfragments, proxy_data
            );
            // socket.emit('ytdl_download', {
            //     url: url,
            //     ext: ext,
            //     output_folder: output_folder,
            //     type: type,
            //     output_format: output_format,
            //     bitrate: bitrate,
            //     segments: skipfragments,
            //     proxy_data: proxy_data
            // });
            // $.ajax({
            //     url: Flask.url_for('overview.download'),
            //     method: 'POST',
            //     data: {
            //         url: url,
            //         ext: ext,
            //         output_folder: output_folder,
            //         type: type,
            //         output_format: output_format,
            //         bitrate: bitrate,
            //         segments: skipfragments
            //     },
            //     error: function(error) {
            //         $("#progress_status").removeClass('d-none');
            //         $("#progress_status").children('p').text(error.responseText.slice(1, error.responseText.length - 1));
                    
            //     }
            // })
        }
    });
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
            var filepath = msg.filepath;
            var length = info.yt.duration;
            let release_id = $(".audiocol-checkbox:checked").parent().parent().attr('id');
            
        }
    });
    $(document).on('click', ".removesegment", function() {
        $(this).parents('.form-row').remove();
    });
    $(document).on('click', "#addsegment", function() {
        let id = $(this).parents('.form-row').siblings('.timestamp_row').length > 0 ? parseInt($(this).parents('.form-row').siblings('.timestamp_row:last').attr('id').slice(4)) + 1 : parseInt($(this).parents('.form-row').attr('id').slice(4)) + 1;

        let row = document.createElement('div');
        let startcol = document.createElement('div');
        let endcol = document.createElement('div');
        let startinput = document.createElement('input');
        let endinput = document.createElement('input');
        let input_group = document.createElement('div');
        let input_group_append = document.createElement('div');
        let removebtn = document.createElement('button');
        let removeicon = document.createElement('i');

        row.classList.add('form-row', 'timestamp_row');
        row.id = 'row_'+id;

        startcol.classList.add('col');
        endcol.classList.add('col');

        input_group.classList.add('input-group');
        input_group_append.classList.add('input-group-append');

        removebtn.classList.add('btn', 'btn-danger', 'bg-danger', 'input-group-text', 'removesegment');
        removeicon.classList.add('fi-xwsuxl-minus-solid');
        removeicon.setAttribute('style', 'color: white');

        startinput.classList.add('form-control', 'timestamp_input');
        startinput.id = 'segmentstart_'+id;
        startinput.type = 'text';

        endinput.classList.add('form-control', 'timestamp_input');
        endinput.id = 'segmentend_'+id;
        endinput.type = 'text';

        removebtn.appendChild(removeicon);
        input_group_append.appendChild(removebtn);
        input_group.appendChild(endinput);
        input_group.appendChild(input_group_append);        

        startcol.appendChild(startinput);
        endcol.appendChild(input_group);
        row.appendChild(startcol);
        row.appendChild(endcol);

        $(".timestamp_row:last").after(row);
        friconix_update();
    });
    $(document).on('focus', '.timestamp_input', function() {
        $(this).ForceNumericOnly();
    });
    $(document).on('click', '#segments_check', function() {
        
        $(".timestamp_row").toggleClass('d-none');
        $(".timestamp_caption").parents('.form-row').toggleClass('d-none');
    });
    $(document).on('click', 'label[for=\'#segments_check\']', function() {
        $(".timestamp_row").toggleClass('d-none');
        $(".timestamp_caption").parents('.form-row').toggleClass('d-none');
        $(this).siblings('input').click();
    })
    $(document).on('change', '#extension', function() {
        if($("#extension option:selected").parent().attr('label') == 'Video') {
            $("#bitrate").parent().addClass('d-none');
        } else if($("#extension option:selected").parent().attr('label') == 'Audio') {
            $("#bitrate").parent().removeClass('d-none');
            $("#bitrate").val("192");
        }
    });
})