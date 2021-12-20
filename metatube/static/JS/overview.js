var socket = io();
$(document).ready(function() {
    for(let i = 0; i < document.getElementsByClassName('cover_img').length; i++) {
        socket.emit('fetchcover', document.getElementsByClassName('cover_img')[i].parentNode.parentNode.id);
    }

    $("#metadataview").find('input').attr('autocomplete', 'off');
    // If the user presses Enter or submits the form in some other way, it'll trigger the 'find' button
    function insertYTcol(response, form) {
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

    function insertAudioCol(mbp_data) {
        let release_id = mbp_data.id;
        let title = mbp_data.title;
        let artists = mbp_data['artist-credit'].length > 1 ? "Artists: <br />" : "Artist: ";
        let date = mbp_data.date;
        let language = ""
        if("text-representation" in mbp_data) {
            if("language" in mbp_data["text-representation"]) {
                language =  mbp_data["text-representation"]["language"]
            } else {
                language = "Unknown"
            }
        } else {
            language = "Unknown"
        }
        $.each(mbp_data["artist-credit"], function(key_artist, value_artist) {
            if(typeof(value_artist) == 'object') {
                let a = '<a href="https://musicbrainz.org/artist/'+value_artist.artist.id+'" target="_blank">'+value_artist.name+'</a><br/>';
                artists+=a;
            }
        });
        let release_type = mbp_data["release-group"].type;
        let mbp_url = 'https://musicbrainz.org/release/'+release_id;
        let mbp_image = "";
        if("cover" in mbp_data && mbp_data.cover != "None") {
            mbp_image = mbp_data.cover.images[0].thumbnails.small.replace(/^http:/, 'https:');
        } else {
            mbp_image = Flask.url_for('static', {"filename": "images/empty_cover.png"});
        }
        
        // html = {
        //     'img': '<img src="'+mbp_image+'" class="align-self-center mr-3" alt="Thumbnail for '+release_id+'"/>',
        //     'desc': '<div class="media-body"><h5 class="mt-0 mb-1"><a href="'+mbp_url+'" target="_blank">'+title+'</a></h5><p>'+artists+'Type: '+release_type+'<br/>Date: '+date+'<br/>Language: '+language+'</p></div>',
        //     'checkbox': '<div class="input-group-text"><input class="audiocol-checkbox" type="radio" aria-label="Radio button for selecting an item"></div>',
        // }

        let ul = document.createElement('ul');
        let img = document.createElement('img');
        let desc = document.createElement('div');
        let header = document.createElement('h5');
        let headeranchor = document.createElement('a');
        let paragraph = document.createElement('p');
        let inputgroup = document.createElement('div');
        let checkbox = document.createElement('input');
        let list = document.createElement('li');

        ul.classList.add('list-unstyled');
        img.classList.add('align-self-center', 'mr-3', 'img-fluid');
        desc.classList.add('media-body');
        header.classList.add('mt-0', 'mb-1');

        headeranchor.href = mbp_url;
        headeranchor.target = '_blank';
        headeranchor.innerText = title;

        img.src = mbp_image;
        img.target = '_blank';

        paragraph.innerHTML = artists+'Type: '+release_type+'<br/>Date: '+date+'<br/>Language: '+language;
        
        inputgroup.classList.add("input-group-text");
        
        checkbox.classList.add('audiocol-checkbox');
        checkbox.type = 'radio';
        checkbox.ariaLabel = 'Radio button for selecting an item';

        list.classList.add('media', 'mbp-item');
        list.setAttribute('style', 'cursor: pointer');
        list.id = release_id;

        header.append(headeranchor);
        desc.append(header, paragraph);

        inputgroup.appendChild(checkbox);
        list.append(img, desc, inputgroup);
        ul.appendChild(list);

        $(".spinner-border").parent().remove();
        $("#audiocol").append(ul);
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
        let td_ext = document.createElement('td');
        let td_actions = document.createElement('td');
        let dropdown = document.createElement('div');
        let dropdownbtn = document.createElement('button');
        let dropdownmenu = document.createElement('div');
        let editfileanchor = document.createElement('a');
        let editmetadataanchor = document.createElement('a');
        let downloadanchor = document.createElement('a');
        let viewanchor = document.createElement('a');
        let deleteanchor = document.createElement('a');
        let cover = document.createElement('img');
        
        td_name.innerText = itemdata["name"];
        td_artist.innerText = itemdata["artist"].replace('/', ';');
        td_album.innerText = itemdata["album"];
        td_date.innerText = itemdata["date"];
        td_ext.innerText = itemdata["filepath"].split('.')[itemdata["filepath"].split('.').length - 1].toUpperCase();
        dropdownbtn.innerText = 'Select action';
        editfileanchor.innerText = 'Change file data';
        editmetadataanchor.innerText = ['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A', 'WAV'].indexOf(td_ext.innerText) > -1 ? 'Change metadata' : 'Item has been moved or deleted or metadata is not supported';
        downloadanchor.innerText = 'Download item';
        viewanchor.innerText = 'View YouTube video';
        deleteanchor.innerText = 'Delete item';

        td_name.setAttribute('style', 'vertical-align: middle;');
        td_artist.setAttribute('style', 'vertical-align: middle;');
        td_album.setAttribute('style', 'vertical-align: middle;');
        td_date.setAttribute('style', 'vertical-align: middle;');
        td_ext.setAttribute('style', 'vertical-align: middle;');
        td_actions.setAttribute('style', 'vertical-align: middle;');

        td_name.classList.add('td_name')
        td_artist.classList.add('td_artist')
        td_album.classList.add('td_album')
        td_date.classList.add('td_date')
        td_ext.classList.add('td_ext')
        
        dropdown.classList.add('dropdown');
        dropdownbtn.classList.add('btn', 'btn-primary', 'dropdown-toggle');
        dropdownbtn.setAttribute('data-toggle', 'dropdown');
        dropdownmenu.classList.add('dropdown-menu');

        editfileanchor.href = "javascript:void(0)";
        editfileanchor.classList.add('dropdown-item', 'editfilebtn');
        
        editmetadataanchor.href = "javascript:void(0)";
        editmetadataanchor.classList.add('dropdown-item', 'editmetadatabtn');
        
        downloadanchor.href = "javascript:void(0)";
        downloadanchor.classList.add('dropdown-item', 'downloaditembtn');
        
        viewanchor.href = "https://youtu.be/" + itemdata["ytid"];
        viewanchor.classList.add('dropdown-item');
        viewanchor.setAttribute('target', '_blank');

        deleteanchor.href = "javascript:void(0)";
        deleteanchor.classList.add('dropdown-item', 'deleteitembtn');        
        
        tr.id = itemdata["id"];

        let blob = new Blob([itemdata.image]);
        let uri = URL.createObjectURL(blob);

        cover.classList.add('img-fluid', 'cover-img');
        cover.setAttribute('style', 'width: 100px; height: 100px;');
        cover.src = uri;

        dropdownmenu.append(editfileanchor, editmetadataanchor, downloadanchor, viewanchor, deleteanchor);
        dropdown.append(dropdownbtn, dropdownmenu);
        td_actions.appendChild(dropdown);

        td_name.prepend(cover);

        tr.append(td_name, td_artist, td_album, td_date, td_ext, td_actions);
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

    function searchresult(data) {
        let ul = document.createElement('ul');
        let li = document.createElement('li');
        let img = document.createElement('img');
        let body = document.createElement('div');
        let header = document.createElement('a');
        let channel = document.createElement('a');
        let desc = document.createElement('p');

        ul.classList.add('list-unstyled', 'youtuberesult');
        li.classList.add('media');
        img.classList.add('img-fluid');
        body.classList.add('media-body');
        header.classList.add('youtubelink');

        header.href = data.link;
        header.innerText = data.title;
        header.target = '_blank';

        img.src = data.thumbnails[0].url;
        channel.href = data.channel.link;
        channel.innerText = data.channel.name;
        channel.target = '_blank';

        ul.setAttribute('style', 'cursor: pointer');

        desc.innerHTML = 'Channel: ' + channel.outerHTML + '<br />Description: ';
        try {
            for(let i = 0; i < data.descriptionSnippet.length; i++) {
                desc.innerHTML += data.descriptionSnippet[i].text;
            }
        } catch {
            desc.innerHTML += 'No description available';
        }
        body.append(header, desc);
        li.append(img, body);
        ul.append(li);
        $("#defaultview").append(ul);
    }

    $(document).on('mouseenter', '.mbp-item, .youtuberesult', function() {
        $(this).css('filter', 'brightness(50%)');
        $(this).css('background-colour', '#009999');
    });
    $(document).on('mouseleave', '.mbp-item, .youtuberesult', function() {
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
        $(this).siblings('input').click();
    });
    
    $(document).on('change', '#extension', function() {
        if($("#extension option:selected").parent().attr('label') == 'Video') {
            $("#type").val('Video');
            $("#videorow").removeClass('d-none');
        } else if($("#extension option:selected").parent().attr('label') == 'Audio') {
            $("#videorow").addClass('d-none');
            $("#type").val('Audio');
        }
        if(['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A', 'WAV'].indexOf($("#extension").val().toUpperCase()) < 0)  {
            $("#editmetadata").addClass('d-none');
        } else {
            $("#editmetadata").removeClass('d-none');
        }
    });

    $(document).on('change', '#resolution', function() {
        if($(this).val() != 'best') {
            $("#width").val($(this).val().split(';')[0]);
            $("#height").val($(this).val().split(';')[1]);
            $(this).parent().siblings().removeClass('d-none');
        } else {
            $("#width").val('best');
            $("#height").val('best');
            $(this).parent().siblings().addClass('d-none');
        }
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
        if($(this).val() == 'None') {
            $("#proxy_row").addClass('d-none');
        } else {
            $("#proxy_row").removeClass('d-none');
        }
    });

    
    $(document).on('click', ".deleteitembtn", function() {
        $("#removeitemmodal").find('.btn-danger').attr('id', $(this).parents('tr').attr('id'));
        $("#removeitemmodaltitle").text('Delete ' + $(this).parents('tr').children(':first').text())
        $("#removeitemmodal").modal('show');
    });

    $(document).on('click', '.editmetadatabtn', function() {
        if(['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A', 'WAV'].indexOf($(this).parents('td').siblings('.td_ext').text()) > -1) {
            socket.emit('editmetadata', $(this).parents('tr').attr('id'));
        }
    });

    $(document).on('click', '.editfilebtn', function() {
        socket.emit('editfile', $(this).parents('tr').attr('id'));
    });

    $(document).on('click', '.downloaditembtn', function() {
        let id = $(this).parents('tr').attr('id');
        socket.emit('downloaditem', id)
    });

    $(document).on('click', "#fetchmbpreleasebtn", function(){
        let release_id = $(this).parent().siblings('input').val();
        if(release_id.length > 0) {
            $(".removeperson").parents('.personrow').remove();
            socket.emit('fetchmbprelease', release_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").text('<p>Enter a Musicbrainz ID!</p>')
        }
    });

    $(document).on('click', "#fetchmbpalbumbtn", function(){
        let album_id = $(this).parent().siblings('input').val();
        if(album_id.length > 0) {
            socket.emit('fetchmbpalbum', album_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").text('<p>Enter a Musicbrainz ID!</p>')
        }
    });

    $(document).on('click', '#edititembtnmodal', function() {
        let people = {};
        let release_id = $("#mbp_releaseid").val(); 
        let filepath = $("#item_filepath").val();
        let id = $("#edititemmodal").attr('itemid');
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
        socket.emit('editmetadatarequest', metadata, release_id, filepath, id);
        $("#edititemmodal").modal('hide');
    });

    $(document).on('click', '.youtuberesult', function() {
        let link = $(this).find('.youtubelink').attr('href');
        socket.emit('ytdl_search', link);
        $("#defaultview").children('ul').remove();
        let spinner = '<div class="d-flex justify-content-center"><div class="spinner-border text-success" role="status"><span class="sr-only">Loading...</span></div></div>';
        $("#searchlog, #progresstext").empty();
        $("#defaultview").removeClass('d-none');
        $("#ytcol, #audiocol").empty().removeClass('d-none').append(spinner);
        // Reset the modal
        $("#progress").attr('aria-valuenow', "0").css('width', '0');
        $("#searchvideomodalfooter, #metadataview, #progressview, #downloadfilebtn").addClass('d-none');
        $(".removeperson").parents('.personrow').remove();
        $("#metadataview").find('input').val('');
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
        $("#defaultview, #ytcol, #audiocol").removeClass('d-none');
        $("#defaultview").children('.youtuberesult').remove();
        $("#ytcol, #audiocol").empty().append(spinner);
        // Reset the modal
        $("#progress").attr('aria-valuenow', "0").css('width', '0');
        $("#searchvideomodalfooter, #metadataview, #progressview, #downloadfilebtn").addClass('d-none');
        $(".removeperson").parents('.personrow').remove();
        $("#metadataview").find('input').val('');
    });

    $("#downloadbtn").on('click', function(e) {
        if($(".audiocol-checkbox:checked").length < 1) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Select a release on the right side before downloading a video');
        }  else if($(".timestamp_input").val() == '' && !$("#segments_check").is(':checked')) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Enter all segment fields or disable the segments');
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
                'proxy_type': $("#proxy_type").val(),
                'proxy_address': $("#proxy_type").val() == 'None' ? '' : $("#proxy_address").val(),
                'proxy_port': $("#proxy_type").val() == 'None' ? '' : $("#proxy_port").val(),
                'proxy_username': $("#proxy_type").val() == 'None' ? '' : $("#proxy_username").val(),
                'proxy_password': $("#proxy_type").val() == 'None' ? '' : $("#proxy_password").val(),
            })
            $("#progress_status").siblings('p').empty();
            data = {
                'url': url,
                'ext': ext,
                'output_folder': output_folder,
                'output_format': output_format,
                'type': type,
                'bitrate': bitrate,
                'skipfragments': skipfragments,
                'proxy_data': proxy_data,
                'width': width,
                'height': height
            }
            socket.emit('ytdl_download', data, function(ack) {
                if(ack == "OK") {
                    $("#editmetadata, #downloadbtn, #defaultview").addClass('d-none');
                    $("#progressview").removeClass('d-none');
                    $("#searchlog").empty();
                }
            });
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
        $("#editmetadata, #downloadbtn, #defaultview").addClass('d-none');
        $("#progressview").removeClass('d-none');
        $("#searchlog").empty();
        var progress_text = $("#progresstext");
        if(msg.status == 'downloading') {
            progress_text.text("Downloading...");
            let percentage = Math.round(((msg.downloaded_bytes / msg.total_bytes) * 100) / 3);
            $("#progress").attr('aria-valuenow', percentage+"%");
            $("#progress").text(percentage + "%");
            $("#progress").css('width', parseInt(percentage)+'%');
        }
        else if(msg.status == 'finished_ytdl' || msg.status == 'processing') {
            $("#progress").attr('aria-valuenow', 33);
            $("#progress").text("33%");
            $("#progress").css('width', '33%');
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
            msg.data["ytid"] = $("#thumbnail_yt").attr('ytid');
            try {
                socket.emit('insertitem', msg.data);
                $("#downloadfilebtn").removeClass('d-none');
                $("#downloadfilebtn").attr('filepath', msg.data["filepath"]);
            } catch (error) {
                console.error(error);
            }
        } else if(msg.status == 'metadata_unavailable') {
            msg.data["ytid"] = $("#thumbnail_yt").attr('ytid');
            progress_text.text('Metadata has NOT been added, because metadata is not supported for the selected extension');
            $("#progress").attr('aria-valuenow', 100);
            $("#progress").text("100%");
            $("#progress").css('width', '100%');
            $("#downloadfilebtn").removeClass('d-none');
            $("#downloadfilebtn").attr('filepath', msg.data["filepath"]);
            socket.emit('insertitem', msg.data);
        } else if(msg.status == 'error') {
            progress_text.text(msg.message);
            $("#progress").attr('aria-valuenow', 100);
            $("#progress").html('ERROR <i class="fi-cwluxl-smiley-sad-wide"></i>');
            $("#progress").css('width', '100%');
        }
    });

    socket.on('ytdl_response', (video, downloadform, metadataform) => {
        console.info('Got YouTube info');
        $("#metadataview").empty().prepend(metadataform);
        let ytcol = insertYTcol(video, downloadform);
        ytdata = video;
        $("#ytcol").append(ytcol);
        friconix_update();
        $(".modal-footer").removeClass('d-none').children().not('#downloadfilebtn').removeClass('d-none');
    });

    socket.on('mbp_response', (mbp) => {
        console.info('Got musicbrainz info');
        for(let i = 0; i < Object.keys(mbp).length; i++) {
            let list = insertAudioCol(mbp[i]);
        }
        $(".modal-footer").removeClass('d-none');
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
        $("#proxy_type").val(response.proxy_type ? $("#proxy_status") != false : 'None');
        $("#proxy_address").val(response.proxy_address);
        $("#proxy_port").val(response.proxy_port);
        $("#proxy_username").val(response.proxy_username);
        $("#proxy_password").val(response.proxy_password);
        if(response.proxy_status == true) {
            $("#proxy_row").removeClass('d-none');
        } else {
            $("#proxy_row").addClass('d-none');
        }
        if(response.type == 'Video') {
            $("#videorow").removeClass('d-none');
            $("#resolution").children('option:selected').prop('selected', false);
            $("#resolution").children("option[value='"+response.resolution+"']").prop('selected', true);
            if(response.width == 'best' || response.height == 'best') {
                $("#width").val('best');
                $("#height").val('best');
                $("#resolution").parent().siblings().addClass('d-none');
            } else {
                $("#width").val(response.resolution.split(';')[0]);
                $("#height").val(response.resolution.split(';')[1]);
            }
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
        artists = artists.trim().slice(0, artists.trim().length -1).replace('/', ';');
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
        $("#defaultview, #downloadbtn, #editmetadata").removeClass('d-none');
        $("#progressview").addClass('d-none');
        $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
    });

    socket.on('overview', (data) => {
        if(data.msg == 'inserted_song') {
            additem(data)
        } else if(data.msg == 'download_file') {
            filedata = data.data;
            let blob = new Blob([filedata], {'type': data.mimetype});
            let uri = URL.createObjectURL(blob);
            downloadURI(uri, data.filename);
        } else if(data.msg == 'load_cover') {
            let blob = new Blob([data.data]);
            let uri = URL.createObjectURL(blob);
            $("tr#"+data.id).find('img.cover_img').attr('src', uri);
        } else if(data.msg == 'changed_metadata') {
            socket.emit('updateitem', data.data);
        } else if(data.msg == 'changed_metadata_db') {
            let tr = $("tr#"+data.data.itemid);
            let blob = new Blob([data.data.image]);
            let uri = URL.createObjectURL(blob);
            tr.find('img').attr('src', uri);
            tr.find('img').siblings('span').text(data.data.name);
            tr.find('.td_artist').text(data.data.artist);
            tr.find('.td_album').text(data.data.album);
            tr.find('.td_date').text(data.data.date);
            tr.find('.td_filepath').text(data.data.filepath.split('.')[data.data.filepath.split('.').length - 1]);
            $("#overviewlog").text("Item metadata has been changed!");
        } else {
            $("#overviewlog").text(data.msg);
        }
    });

    socket.on('edit_metadata', (data) => {
        $("#downloadsection, #metadatasection, #metadataview").empty();
        $("#metadatasection").append(data.metadataview);
        $("#metadatasection").find('#mbp_releaseid').val(data.metadata.musicbrainz_id);
        $("#metadatasection").find('#mbp_albumid').val(data.metadata.mbp_releasegroupid);
        $("#metadatasection").find('#md_title').val(data.metadata.title);
        $("#metadatasection").find('#md_artists').val(data.metadata.artist);
        $("#metadatasection").find('#md_album').val(data.metadata.album);
        $("#metadatasection").find('#md_album_artists').val(data.metadata.artist);
        $("#metadatasection").find('#md_album_tracknr').val(data.metadata.tracknr);
        $("#metadatasection").find('#md_album_releasedate').val(data.metadata.date);
        $("#metadatasection").prepend('<div class="form-row"><div class="col"><label for="#itemfilepath">Filepath of item:</label><input type="text" value="'+data.metadata.filepath+'" class="form-control" id="item_filepath" style="cursor: not-allowed" disabled /></div></div>');
        $("#edititemmodal").attr('itemid', data.metadata.itemid)
        friconix_update();
        $("#edititemmodal").modal('show');
    });

    socket.on('metadatalog', (msg) => {
        $("#metadatalog").text(msg);
    });

    socket.on('edit_file', (data) => {
        $("#downloadsection, #ytcol, #metadatasection").empty();
        $("#downloadsection").append(data.downloadview);
        friconix_update();
        $("#edititemmodal").modal('show');
    });

    socket.on('youtubesearch', (data) => {
        $("#defaultview").children().addClass('d-none');
        for(let i = 0; i < Object.keys(data.result).length; i++) {
            searchresult(data.result[i]);
        };
    });
});