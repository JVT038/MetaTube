var socket = io();
$(document).ready(function() {
    $("#metadataview").find('input').attr('autocomplete', 'off');
    
    // If the user presses Enter or submits the form in some other way, it'll trigger the 'find' button
    async function insertYTcol(response, form) {
        let data = response;
        let artist = 'artist' in data ? data.artist : "Unknown";
        let track = 'track' in data ? data.track : "Unknown";
        let album = 'album' in data ? data.album : "Unknown";
        let channel = 'channel' in data ? data.channel : data.uploader;
        let id = data.id;
        let thumbnail = "";
        $.each(data.thumbnails, function(key_thumbnail, value_thumbnail) {
            if(value_thumbnail.preference == -5) {
                
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
            'img': '<img class="img-fluid d-none d-md-block" id="thumbnail_yt" ytid="'+data.id+'" src="'+thumbnail+'" title="Click to watch video" alt="Thumbnail for video '+id+'" onclick="window.open(\''+data.webpage_url+'\', \'_blank\')" style="cursor: pointer" url="'+data.webpage_url+'" />',
            'text': '<p>Video title: '+data.title+'</br>Channel: '+channel+'<br/>Length: '+length+'</br/>Track name: '+track+'<br/>Artist: '+artist+'<br/>Album: '+album+'</p>'
        }
        let inject = html['img'] + html['text'] + form;
        $("#ytcol").empty();
        return inject;
        
    }

    async function insertAudioCol(mbp_data) {
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

    function additem(data) {
        let itemdata = data.data;
        let tr = document.createElement('tr');
        let td_name = document.createElement('td');
        let td_artist = document.createElement('td');
        let td_album = document.createElement('td');
        let td_date = document.createElement('td');
        let td_actions = document.createElement('td');
        let editbtn = document.createElement('button');
        let deletebtn = document.createElement('button');
        let downloadbtn = document.createElement('button');
        let viewbtn = document.createElement('button');
        let i_edit = document.createElement('i');
        let i_delete = document.createElement('i');
        let i_view = document.createElement('i');
        let i_download = document.createElement('i');
        
        td_name.innerText = itemdata["name"]
        td_artist.innerText = itemdata["artist"].replace('/', ';')
        td_album.innerText = itemdata["album"]
        td_date.innerText = itemdata["date"]
        
        editbtn.classList.add('btn', 'btn-success', 'edititembtn', 'mr-1');
        viewbtn.classList.add('btn', 'btn-info', 'mr-1');
        downloadbtn.classList.add('btn', 'btn-primary', 'downloaditembtn', 'mr-1');
        deletebtn.classList.add('btn', 'btn-danger', 'deleteitembtn');
        
        i_edit.classList.add('fi-xnsuxl-edit-solid');
        i_delete.classList.add('fi-xnsuxl-trash-bin');
        i_view.classList.add('fi-xwsuxl-youtube');
        i_download.classList.add('fi-xwsrxl-sign-in-solid');
        
        tr.id = itemdata["id"];

        editbtn.setAttribute('data-toggle', 'tooltip');
        editbtn.setAttribute('data-placement', 'top');
        editbtn.setAttribute('title', 'Edit item');

        deletebtn.setAttribute('data-toggle', 'tooltip');
        deletebtn.setAttribute('data-placement', 'top');
        deletebtn.setAttribute('title', 'Delete item');

        viewbtn.setAttribute('data-toggle', 'tooltip');
        viewbtn.setAttribute('data-placement', 'top');
        viewbtn.setAttribute('title', 'View YouTube video');
        viewbtn.setAttribute('onclick', 'window.open(\'https://youtu.be/'+itemdata["ytid"]+'\', target=\'__blank\')');
        
        downloadbtn.setAttribute('data-toggle', 'tooltip');
        downloadbtn.setAttribute('data-placement', 'top');
        downloadbtn.setAttribute('title', 'Download item');

        i_view.setAttribute('style', 'color: red');

        deletebtn.appendChild(i_delete);
        editbtn.appendChild(i_edit);
        viewbtn.appendChild(i_view);
        downloadbtn.appendChild(i_download);

        td_actions.appendChild(editbtn);
        td_actions.appendChild(downloadbtn);
        td_actions.appendChild(viewbtn);
        td_actions.appendChild(deletebtn);

        tr.append(td_name, td_artist, td_album, td_date, td_actions);
        $("#recordstable").children("tbody").append(tr);
        friconix_update();
    }

    function downloadURI(uri, name) {
        var link = document.createElement("a");
        link.download = name;
        link.href = uri;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        delete link;
    }

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
            $("#type").val('Video');
            $("#videorow").removeClass('d-none');
        } else if($("#extension option:selected").parent().attr('label') == 'Audio') {
            $("#videorow").addClass('d-none');
            $("#type").val('Audio');
        }
    });

    $(document).on('change', '#resolution', function() {
        $("#width").val($(this).val().split(';')[0]);
        $("#height").val($(this).val().split(';')[1]);
    });
    
    $(document).on('click', "#editmetadata", function() {
        $("#defaultview, #metadataview, #queryform, #downloadbtn").toggleClass('d-none');
        $(this).attr('id', 'savemetadata');
        $(this).text('Save metadata')
    });
    
    $(document).on('click', '#savemetadata', function() {
        $("#defaultview, #metadataview, #queryform, #downloadbtn").toggleClass('d-none');
        $(this).attr('id', 'editmetadata');
        $(this).text('Edit metadata')
    });

    $(document).on('click', '.addperson', addperson);

    $(document).on('click', '.removeperson', function() {
        $(this).parents('.personrow').remove();
    });

    $(document).on('change', '#proxy_type', function() {
        $("#proxy_row").toggleClass('d-none');
    });

    
    $(document).on('click', ".deleteitembtn", function() {
        $("#removeitemmodal").find('.btn-danger').attr('id', $(this).parent().parent().attr('id'));
        $("#removeitemmodaltitle").text('Delete ' + $(this).parents('tr').children(':first').text())
        $("#removeitemmodal").modal('show');
    });

    $(document).on('click', '.edititembtn', function() {

    });

    $(document).on('click', '.downloaditembtn', function() {
        let id = $(this).parents('tr').attr('id');
        socket.emit('downloaditem', id)
    });

    $("#delitembtnmodal").on('click', function() {
        let id = $(this).attr('id');
        $("tr#"+id).remove();
        $("#removeitemmodal").modal('hide');
        socket.emit('deleteitem', id);
    });

    $("#queryform").on('submit', function(e) {
        e.preventDefault();
        $("#searchsongbtn").trigger('click');
    });
    
    $("#searchsongbtn").on('click', function() {
        // Send request to the server
        let query = $("#query").val();
        socket.emit('ytdl_search', query);
        let spinner = '<div class="d-flex justify-content-center"><div class="spinner-border text-success" role="status"><span class="sr-only">Loading...</span></div></div>';
        $("#searchlog, #progresstext").empty();
        $("#defaultview").removeClass('d-none');
        $("#ytcol, #audiocol").empty().append(spinner);
        // Reset the modal
        $("#progress").attr('aria-valuenow', "0").css('width', '0');
        $("#searchvideomodalfooter, #metadataview, #progressview").addClass('d-none');
        $(".removeperson").parents('.personrow').remove();
        $("#metadataview").find('input').val('');
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
            let width = $("#width").val();
            let height = $("#height").val();
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
            }
            skipfragments = JSON.stringify($.grep(skipfragments,function(n){ return n == 0 || n }));
            let proxy_data = JSON.stringify({
                'proxy_status': $("#proxy_type").val(),
                'proxy_address': $("#proxy_address").val(),
                'proxy_port': $("#proxy_port").val(),
                'proxy_username': $("#proxy_username").val(),
                'proxy_password': $("#proxy_password").val()
            });
            $("#progress_status").siblings('p').empty();
            socket.emit('ytdl_download', 
                url, ext, output_folder, type, output_format, bitrate,skipfragments, proxy_data, width, height
            );
            $("#editmetadata, #downloadbtn, #defaultview").addClass('d-none');
            $("#progressview").removeClass('d-none');
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

    $("#fetchmbpalbumbtn").on('click', function(){
        let album_id = $("#md_albumid").val();
        if(album_id.length > 0) {
            socket.emit('fetchmbpalbum', album_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").after('<p>Enter a Musicbrainz ID!</p>')
        }
    });

    $("#addvideo").on('click', function() {
        if($("#progress").text() == '100%') {
            $("#defaultview, #downloadbtn, #editmetadata").removeClass('d-none');
            $("#progressview, #downloadfilebtn").addClass('d-none');
            $("#progresstext, #progress").text('');
            $("#progress").attr({
                'aria-valuenow': '0',
                'aria-valuemin': '0',
                'style': ''
            });
        }

        $("#downloadmodal").modal('toggle');
    });

    $("#downloadfilebtn").on('click', function() {
        socket.emit('downloaditem', $(this).attr('filepath'));
    });

    socket.on('downloadprogress', function(msg) {
        var progress_text = $("#progresstext");
        if(msg.status == 'downloading') {
            progress_text.text("Downloading...");
            let percentage = Math.round((msg.downloaded_bytes / msg.total_bytes) * 100) / 3;
            $("#progress").attr('aria-valuenow', percentage+"%");
            $("#progress").text(percentage + "%");
            $("#progress").css('width', parseInt(percentage)+'%');
        }
        else if(msg.status == 'finished_ytdl') {
            if(msg.total_bytes != 'Unknown') {
                $("#progress").attr('aria-valuenow', 33);
                $("#progress").text("33%");
                $("#progress").css('width', '33%');
            } else {
                progress_text.text('Finished downloading!');
            }
        } else if(msg.status == 'processing') {
            progress_text.text('Processing and converting file to desired output... ');
        } else if(msg.status == 'finished_ffmpeg') {
            $("#progress").attr('aria-valuenow', 66);
            $("#progress").text("66%");
            $("#progress").css('width', '66%');
            progress_text.text('Adding metadata...');
            var filepath = msg.filepath;
            let release_id = $(".audiocol-checkbox:checked").parent().parent().attr('id');
            let people = {};

            $.each($('.artist_relations'), function() {
                if($(this).val().trim().length < 1 || $(this).parent().siblings().find('.artist_relations').val().trim().length < 1) {
                    return;
                } else {
                    // Get ID by removing all letters from the ID, so the number remains
                    let id = $(this).parents('.personrow').attr('id').replace(/[a-zA-Z]/g, '');
                    if($(this).attr('id').replace(/[0-9]/g, '') == 'artist_relations_name') {
                        people[id].name = $(this).val();
                    } else {
                        people[id].type = $(this).val();
                    }
                }
            });

            let metadata = {
                'mbp_releaseid': $("#mbp_releaseid").val(),
                'mbp_albumid': $("#md_albumid").val(),
                'title': $("#md_title").val(),
                'artists': $("#md_artists").val(),
                'album': $("#md_album").val(),
                'album_artists': $("#md_album_artists").val(),
                'album_tracknr': $("#md_album_tracknr").val(),
                'album_releasedate': $("#md_album_releasedate").val(),
                'cover': $("#md_cover").val(),
                'people': JSON.stringify(people)
            };
            socket.emit('mergedata', filepath, release_id, metadata);
        } else if(msg.status == 'finished_metadata') {
            $("#progress").attr('aria-valuenow', 100);
            $("#progress").text("100%");
            $("#progress").css('width', '100%');
            progress_text.text('Finished adding metadata!');
            let ytid = $("#thumbnail_yt").attr('ytid');
            $("#downloadfilebtn").removeClass('d-none');
            $("#downloadfilebtn").attr('filepath', msg.data["filepath"]);
            socket.emit('insertdata', msg.data, ytid);
        } else {
            socketdata = msg;
        }
    });

    socket.on('ytdl_response', async (video, downloadform) => {
        let ytcol = await insertYTcol(video, downloadform);
        ytdata = video;
        $("#ytcol").append(ytcol);
        friconix_update();
        $(".modal-footer").removeClass('d-none').children().not('#downloadfilebtn').removeClass('d-none');
    });

    socket.on('mbp_response', async (mbp) => {
        let audiocol = await insertAudioCol(mbp);
        audiodata = mbp;
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
            $("#videorow").removeClass('d-none');
            $("#resolution").children('option:selected').prop('selected', false);
            $("#resolution").children("option[value='"+response.resolution+"']").prop('selected', true);
            $("#width").val(response.resolution.split(';')[0]);
            $("#height").val(response.resolution.split(';')[1]);
        } else {
            $("#videorow").addClass('d-none');
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
    });

    socket.on('searchvideo', (data) => {
        $("#defaultview").find(".spinner-border").parent('.d-flex').remove();
        $("#searchlog").text(data);
        $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
    });

    socket.on('overview', (data) => {
        if(data.msg == 'inserted_song') {
            additem(data)
        } else if(data.msg == 'download_file') {
            filedata = data.data;
            let blob = new Blob([filedata], {'type': data.mimetype})
            let uri = URL.createObjectURL(blob)
            downloadURI(uri, data.filename)
        } else {
            $("#overviewlog").text(data.msg)
        }
    });
})