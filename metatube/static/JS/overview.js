var socket = io();
$(document).ready(function() {
    $("#metadataview").find('input').attr('autocomplete', 'off');
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
                    let mbp_image = "";
                    if("cover" in response && response.cover != "None") {
                        // "cover" in response ? response.cover.images[0].thumbnails.small : Flask.url_for('static', {"filename": "images/empty_cover.png"});
                        mbp_image = response.cover.images[0].thumbnails.small;
                    } else {
                        mbp_image = Flask.url_for('static', {"filename": "images/empty_cover.png"});
                    }
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
            });
        });
        $("#audiocol").empty();
        return ul;
    }

    function addperson() {
        let addbutton = $(".addperson");
        let id = addbutton.parents('.personrow').siblings('.personrow').length > 0 ? parseInt(addbutton.parents('.personrow').siblings('.personrow:last').attr('id').slice(addbutton.parents('.personrow').attr('id').length - 1)) + 1 : parseInt(addbutton.parents('.personrow').attr('id').slice(addbutton.parents('.personrow').attr('id').length - 1)) + 1;
        let row = document.createElement('div');
        let col_name = document.createElement('div');
        let col_type = document.createElement('div');
        let input_group = document.createElement('div');
        let input_group_append = document.createElement('div');
        let input_name = document.createElement('input');
        let input_type = document.createElement('input');
        let button = document.createElement('button');
        let icon = document.createElement('i');

        row.classList.add('form-row', 'personrow');
        row.id = 'personrow' + id;

        col_name.classList.add('col');
        col_type.classList.add('col');

        input_name.classList.add('form-control', 'artist-relations');
        input_name.id = 'artist_relations_name' + id;
        
        input_type.classList.add('form-control', 'artist-relations');
        input_type.id = 'artist_relations_type' + id;

        input_group.classList.add('input-group');
        input_group_append.classList.add('input-group-append');
        
        button.classList.add('btn', 'btn-danger', 'bg-danger', 'removeperson');
        button.type = 'button';
        
        icon.classList.add('fi-xwsuxl-minus-solid');
        icon.setAttribute('style', 'color: white');

        button.appendChild(icon);
        input_group_append.appendChild(button);
        input_group.appendChild(input_type);
        input_group.appendChild(input_group_append);
        col_type.appendChild(input_group);
        col_name.appendChild(input_name);
        row.appendChild(col_name);
        row.appendChild(col_type);
        $('.personrow:last').after(row);

        friconix_update();
        return $('.personrow:last');
    }

    $("#queryform").on('submit', function(e) {
        e.preventDefault();
        $("#searchsongbtn").trigger('click');
    });
    
    $("#searchsongbtn").on('click', function() {
        let spinner = '<div class="d-flex justify-content-center"><div class="spinner-border text-success" role="status"><span class="sr-only">Loading...</span></div></div>';
        $("#ytcol").empty().append(spinner);
        $("#audiocol").empty().append(spinner);
        // Reset the modal
        $(".modal-footer").addClass('d-none');
        $(".removeperson").parents('.personrow').remove();
        $("#metadataview").find('input').val('');
        // YouTube socket
        let query = $("#query").val();
        socket.emit('ytdl_search', query);
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
        socket.emit('fetchtemplate', id)
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
    $(document).on('click', "#editmetadata", function() {
        $("#defaultview").toggleClass('d-none');
        $("#metadataview").toggleClass('d-none');
        $("#queryform").toggleClass('d-none');
        $(this).attr('id', 'savemetadata');
        $(this).text('Save metadata')
    });
    $(document).on('click', '#savemetadata', function() {
        $("#defaultview").toggleClass('d-none');
        $("#metadataview").toggleClass('d-none');
        $("#queryform").toggleClass('d-none');
        $(this).attr('id', 'editmetadata');
        $(this).text('Edit metadata')
    });
    $(document).on('click', '.addperson', function() {
        addperson(this);
    });
    $(document).on('click', '.removeperson', function() {
        $(this).parents('.personrow').remove();
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
            });
            $("#progress_status").siblings('p').empty();
            socket.emit('ytdl_download', 
                url, ext, output_folder, type, output_format, bitrate, skipfragments, proxy_data
            );
        }
    });
    $("#fetchmbpreleasebtn").on('click', function(){
        let release_id = $("#mbp_releaseid").val();
        if(release_id.length > 0) {
            $(".removeperson").parents('.personrow').remove();
            socket.emit('fetchmbprelease', release_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").after('<p>Enter a Musicbrainz ID!</p>')
        }
    });

    $("#proxy_type").on('change', function() {
        if($(this).val() == 'None') {
            $("#proxy_row").toggleClass('d-none');
        } else {
            $("#proxy_row").toggleClass('d-none');
        }
    });

    $("#fetchmbpalbumbtn").on('click', function(){
        let album_id = $("#md_albumid").val();
        if(album_id.length > 0) {
            socket.emit('fetchmbpalbum', album_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").after('<p>Enter a Musicbrainz ID!</p>')
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
            let release_id = $(".audiocol-checkbox:checked").parent().parent().attr('id');
            socket.emit('mergedata', filepath, release_id)
        }
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
    socket.on('template', (response) => {
        data = response;
        response = JSON.parse(response);
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
        } else {
            $("#proxy_type").val('None');
            $("#proxy_address").val("");
            $("#proxy_port").val("");
            $("#proxy_username").val("");
            $("#proxy_password").val("");
            $("#proxy_row").addClass('d-none');
        }
        if(response.type == 'Video') {
            $("#bitrate").parent().addClass('d-none');
        } else {
            $("#bitrate").parent().removeClass('d-none');
        }
    });
    socket.on('foundmbprelease', (data) => {
        let mbp = JSON.parse(data);
        let title = mbp["release"].title;
        let tags = "";
        let artists = "";
    
        let album = mbp["release"]["release-group"]["title"];
        let album_releasedate = mbp["release"]["release-group"]["date"];
        let album_id = mbp["release"]["release-group"]["id"];
        
        $.each(mbp["release"]["artist-credit"], function(key, value) {
            if(typeof(value) != 'string') {
                artists += value.artist.name.trim() + "; ";
            }
        });
        $.each(mbp["release"]["release-group"]["tag-list"], function(key, value){
            tags += value.name.trim() + "; ";
        });
        tags = tags.trim().slice(0, tags.trim().length - 1);
        artists = artists.trim().slice(0, artists.trim().length -1);
        $("#md_title").val(title);
        $("#md_artists").val(artists);
        $("#md_album").val(album);
        $("#md_album_releasedate").val(album_releasedate);
        $("#md_albumid").val(album_id);
    
        if("artist-relation-list" in mbp["release"] && mbp["release"]["artist-relation-list"].length > 0) {
            $.each(mbp["release"]["artist-relation-list"], function(key, value) {
                let name = value.artist.name;
                let type = value.type;
                if($(".personrow").length > 1 || ($("#artist_relations_name0").val() != "" || $("#artist_relations_type0").val() != "")) {
                    var row = addperson($(".addperson"));
                    var rowid = row.attr('id').slice(row.attr('id').length - 1);
                } else {
                    var rowid = "0";
                }
                
                $("#artist_relations_name"+rowid).val(name);
                $("#artist_relations_type"+rowid).val(type);
            });
        }
    });
    socket.on('foundmbpalbum', (data) => {
        let mbp = JSON.parse(data);
        let artists = "";
        let tracknr = "";
        let release_cover = mbp["release_cover"]["images"][0]["thumbnails"]["small"];
        let release_date = mbp["release_group"]["release-group-list"][0]["first-release-date"];
        $.each(mbp["release_group"]["release-group-list"][0]["artist-credit"], function(key, value) {
            if(typeof(value) != 'string') {
                artists += value.artist.name.trim() + "; ";
            }
        });
        $.each(mbp["release_group"]["release-group-list"][0]["release-list"], function(key, value) {
            if(value.title == mbp["release_group"]["release-group-list"][0].title) {
                tracknr = key + 1;
            }
        });
        artists = artists.trim().slice(0, artists.trim().length -1);
        $("#md_cover").val(release_cover);
        $("#md_album_releasedate").val(release_date);
        $("#md_album_artists").val(artists);
        $("#md_album_tracknr").val(tracknr);
        console.log(mbp);
    });
})