var socket = io();
$(document).ready(function() {
    ap = new APlayer({
        container: document.getElementById('audioplayer'),
        autoplay: true,
        mini: false,
        loop: 'none'
    });
    $("#metadataview").find('input').attr('autocomplete', 'off');
    $("#searchitem, #filename").val('');
    $(".selectitem, #selectall").prop('checked', false);
    function submitOutputTemplate() {
        if($("#downloadmodal").css('display') != 'none') {
            let val = $("#outputname").val()
            let url = $("#thumbnail_yt").attr('ytid');
            let info_dict = $("#thumbnail_yt").attr('info_dict');
            socket.emit('ytdl_template', {'template': val, 'url': url, 'info_dict': info_dict});
        }
    }
    function createSpinner(msg, location) {
        let spinner = '<div class="spinner-border text-success" role="status"><span class="sr-only">'+msg+'</span></div>';
        $(location).remove('div.spinner-border');
        $(location).prepend(spinner);
    }
    // If the user presses Enter or submits the form in some other way, it'll trigger the 'find' button
    function insertYTcol(response, form) {
        let downloadform = document.createElement('div');
        downloadform.innerHTML = form;

        let data = response;
        let artist = 'artist' in data ? data.artist : "Unknown";
        let track = 'track' in data && data["track"] != null ? data.track : "Unknown";
        let album = 'album' in data ? data.album : "Unknown";
        let channel = 'channel' in data ? data.channel : data.uploader;
        let thumbnail = "";

        $.each(data.thumbnails, function(key_thumbnail, value_thumbnail) {
            if(value_thumbnail.preference == -23) {
                
                thumbnail = value_thumbnail.url;
            }
        });

        let minutes = Math.floor(data.duration / 60);
        let seconds = data.duration % 60;
        if(seconds < 10) {
            seconds = '0' + data.duration % 60;
        }
        
        let length = minutes + ":" + seconds;
        let img = document.createElement('img');
        let paragraph = document.createElement('p');
        let ytcol = document.createElement('div');
        let media = document.createElement('div');
        let body = document.createElement('div');
        let mediaheader = document.createElement('h5');

        img.classList.add('img-fluid');
        img.id = "thumbnail_yt";
        img.setAttribute('ytid', data.id);
        img.src = thumbnail;
        img.title = 'Click to watch video';
        img.alt = 'Thumbnail for video' + data.title;
        img.setAttribute('onClick', "window.open('https://youtu.be/"+data.id+"', '_blank')");
        img.setAttribute('style', 'cursor: pointer');
        img.setAttribute('url', data.webpage_url);
        img.setAttribute('info_dict', JSON.stringify(data));

        if($(window).width() >= 650) {
            media.classList.add('media');
        }
        body.classList.add('media-body');
        mediaheader.classList.add('mt-0');
        mediaheader.innerText = data.title;

        paragraph.innerHTML = 'Channel: <span id="channelspan">'+channel+'</span><br/>Length: '+length+'</br/>Track name: <span id="trackspan">'+track+'</span><br/>Artist: <span id="artistspan">'+artist+'</span><br/><span id="albumspan">Album: '+album+'</span>';
        ytcol.id = 'ytcol';
        ytcol.setAttribute('style', 'width: 100%;');

        body.append(mediaheader, paragraph);
        media.append(img, body);
        
        $("#defaultview").empty().append(ytcol);
        $("#ytcol").append(media, downloadform.firstChild);
        
        $("#searchvideomodalfooter").removeClass('d-none')
        $("#resetviewbtn, #editmetadata, #downloadbtn").addClass('d-none');
        $('#nextbtn, #ytcol, hr').removeClass('d-none');
    }

    function createaudiocol(data) {

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

        headeranchor.href = data["url"];
        headeranchor.target = '_blank';
        headeranchor.innerText = data["title"];
        headeranchor.className = 'darkanchor';

        img.src = data["cover"];
        img.target = '_blank';
        img.style = "width: 300px; height: 300px;";

        paragraph.innerHTML = data["artists"]+'<br />Type: '+data["type"]+'<br/>Date: '+data["date"]+'<br/>Language: '+data["language"] + "<br />Source: <span class='metadatasource'>" + data["source"] + "</span>";
        
        inputgroup.classList.add("input-group-text");
        
        checkbox.classList.add('audiocol-checkbox');
        checkbox.type = 'radio';
        checkbox.ariaLabel = 'Radio button for selecting an item';

        list.setAttribute('style', 'cursor: pointer');
        list.id = data["id"];
        if($(window).width() >= 600) {
            list.classList.add('media');
            list.append(img, desc, inputgroup);
        } else {
            list.append(img, inputgroup, desc);
            inputgroup.classList.add('float-right');
            img.classList.add('mw-100', 'w-75');
        }
        list.classList.add('mbp-item');

        header.append(headeranchor);
        desc.append(header, paragraph);

        inputgroup.appendChild(checkbox);
        ul.appendChild(list);

        $("#editmetadata, #downloadbtn, #resetviewbtn, #geniusbtn").removeClass('d-none');
        $(".spinner-border").remove();
        $("#nextbtn").addClass('d-none');
        if(data["source"] == 'Genius') {
            if(!$("#geniuscol").length) {
                let geniuscol = document.createElement('div');
                geniuscol.setAttribute('style', 'width: 100%;');
                geniuscol.id = 'geniuscol'
                $("#defaultview").append(geniuscol);
            }
            $("#geniuscol").append(ul);
        } else {
            if(!$("#audiocol").length) {
                let audiocol = document.createElement('div');
                audiocol.setAttribute('style', 'width: 100%;');
                audiocol.id = 'audiocol'
                $("#defaultview").append(audiocol);
            }
            $("#audiocol").append(ul);
        }
    }

    function insertmusicbrainzdata(mbp_data) {
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
                let a = '<a href="https://musicbrainz.org/artist/'+value_artist.artist.id+'" class="darkanchor" target="_blank">'+value_artist.name+'</a> <br/>';
                artists+=a;
            }
        });
        let release_type = mbp_data["release-group"].type;
        let mbp_url = 'https://musicbrainz.org/release/'+release_id;
        let mbp_image = "";
        if("cover" in mbp_data && mbp_data.cover != "None" && mbp_data.cover != 'error') {
            mbp_image = mbp_data.cover.images[0].thumbnails.small.replace(/^http:/, 'https:');
        } else {
            mbp_image = "/static/images/empty_cover.png";
        }
        let data = {
            'url': mbp_url,
            'title': title,
            'artists': artists.slice(0, artists.length - 5),
            'type': release_type,
            'date': date,
            'language': language,
            'source': 'Musicbrainz',
            'cover': mbp_image,
            'id': release_id
        };
        createaudiocol(data);
    }

    function insertspotifydata(spotifydata) {
        let title = spotifydata["name"];
        let artists = spotifydata["artists"].length > 1 ? "Artists: " : "Artist: ";
        let date = spotifydata["album"]["release_date"];
        let language = "Unknown";
        let type = spotifydata["album"]["type"];
        let id = spotifydata["id"];
        let url = spotifydata["external_urls"]["spotify"];
        let cover = "";
        for(let i = 0; i < Object.keys(spotifydata["artists"]).length; i++) {
            if(typeof(spotifydata["artists"][i]) == 'object') {
                let link = "<a href='https://open.spotify.com/artist/" + spotifydata["artists"][i]["id"]+"' class='darkanchor' target='_blank'>"+spotifydata["artists"][i]["name"]+"</a> <br />";
                artists += link;
            }
        }
        for(let i = 0; i < Object.keys(spotifydata["album"]["images"]).length; i++) {
            if(spotifydata["album"]["images"][i].height == '300') {
                cover = spotifydata["album"]["images"][i]["url"];
            }
        }
        let data = {
            'url': url,
            'title': title,
            'artists': artists.slice(0, artists.length - 7),
            'type': type,
            'date': date,
            'language': language,
            'source': 'Spotify',
            'cover': cover,
            'id': id
        }
        createaudiocol(data);
    }

    function insertdeezerdata(deezerdata) {
        let title = deezerdata["title"];
        let artists = "Artist: <a href='"+deezerdata["link"]+"' class='darkanchor' target='_blank'>"+deezerdata["artist"]["name"]+"</a>";
        let type = deezerdata["album"]["type"];
        let url = deezerdata["link"];
        let date = "Unknown";
        let language = "Unknown";
        let cover = deezerdata["album"]["cover_medium"];
        let id = deezerdata["id"];
        let data = {
            'url': url,
            'title': title,
            'artists': artists,
            'type': type,
            'date': date,
            'language': language,
            'source': 'Deezer',
            'cover': cover,
            'id': id
        }
        createaudiocol(data);
    }

    function insertgeniusdata(geniusdata) {
        let title = geniusdata["title"];
        let artists = geniusdata["featured_artists"].length > 0 ? "Artists: " : "Artist: ";
        let type = "Song";
        let url = geniusdata["url"];
        let date = geniusdata["release_date_components"] != null ? geniusdata["release_date_components"]["day"] + geniusdata["release_date_components"]["month"] + geniusdata["release_date_components"]["year"] : "Unknown"
        let language = "Unknown";
        let cover = geniusdata["header_image_thumbnail_url"];
        let id = geniusdata["id"];
        artists += "<a href='"+geniusdata["primary_artist"]["url"]+"' class='darkanchor' target='_blank'>"+geniusdata["primary_artist"]["name"]+"</a> <br />";
        for(let i = 0; i < geniusdata["featured_artists"].length; i++) {
            artists += "<a href='"+geniusdata["featured_artists"][i]["url"]+"' class='darkanchor' target='_blank'>"+geniusdata["featured_artists"][i]["name"]+"</a> <br />";
        }
        let data = {
            'url': url,
            'title': title,
            'artists': artists.slice(0, artists.length - 7),
            'type': type,
            'date': date,
            'language': language,
            'source': 'Genius',
            'cover': cover,
            'id': id
        }
        createaudiocol(data);
    }

    function addPerson() {
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
        
        icon.classList.add('bi', 'bi-dash');
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

        
        return $('.personrow:last');
    }

    function addSegment(id) {
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
        removeicon.classList.add('bi', 'bi-dash');
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
    }

    function addItem(data) {
        function addLeadingZeros(n) {
            if (n <= 9) {
              return "0" + n;
            }
            return n
        }
        let itemdata = data.data;
        let dateobj = new Date(itemdata["date"]);
        let date = addLeadingZeros(dateobj.getDate()) + "-" + addLeadingZeros(dateobj.getMonth() + 1) + "-" + dateobj.getFullYear();
        let tr = document.createElement('tr');
        let td_name = document.createElement('td');
        let td_artist = document.createElement('td');
        let td_album = document.createElement('td');
        let td_date = document.createElement('td');
        let td_ext = document.createElement('td');
        let td_actions = document.createElement('td');
        let input_group = document.createElement('div');
        let form_check = document.createElement('div');
        let checkbox = document.createElement('input');
        let dropdown = document.createElement('div');
        let dropdownbtn = document.createElement('button');
        let dropdownmenu = document.createElement('div');
        let cover = document.createElement('img');
        let covercol = document.createElement('div');
        let namecol = document.createElement('div');
        let namespan = document.createElement('span');
        let namerow = document.createElement('div');
        
        td_artist.innerText = itemdata["artist"].join('; ');
        td_album.innerText = itemdata["album"];
        td_date.innerText = date;
        td_ext.innerText = itemdata["filepath"].split('.')[itemdata["filepath"].split('.').length - 1].toUpperCase();
        dropdownbtn.innerText = 'Select action';
        namespan.innerText = itemdata["name"];

        namerow.classList.add('row', 'd-flex', 'justify-content-center');
        namecol.classList.add('align-self-center');
        namespan.classList.add('align-middle');
        if($(window).width() > 991) {
            covercol.classList.add('col');
            namecol.classList.add('col');
        }
        namecol.style.margin = "0 10px 0 10px";

        td_name.setAttribute('style', 'vertical-align: middle;');
        td_artist.setAttribute('style', 'vertical-align: middle;');
        td_album.setAttribute('style', 'vertical-align: middle;');
        td_date.setAttribute('style', 'vertical-align: middle;');
        td_ext.setAttribute('style', 'vertical-align: middle;');
        td_actions.setAttribute('style', 'vertical-align: middle;');

        td_name.classList.add('td_name', 'text-dark');
        td_artist.classList.add('td_artist', 'text-dark');
        td_album.classList.add('td_album', 'text-dark');
        td_date.classList.add('td_date', 'text-dark');
        td_ext.classList.add('td_ext', 'text-dark');

        input_group.classList.add('d-flex', 'justify-content-end');
        form_check.classList.add('form-check', 'ml-2');
        checkbox.classList.add('form-check-input', 'selectitem');
        checkbox.type = 'checkbox';
        
        dropdown.classList.add('dropdown');
        dropdownbtn.classList.add('btn', 'btn-primary', 'dropdown-toggle');
        dropdownbtn.setAttribute('data-toggle', 'dropdown');
        dropdownmenu.classList.add('dropdown-menu'); 
        
        tr.id = itemdata["id"];

        cover.classList.add('img-fluid', 'cover-img');
        cover.setAttribute('style', 'width: 100px; height: 100px;');
        cover.src = itemdata["image"];

        form_check.appendChild(checkbox);       

        dropdown.append(dropdownbtn, dropdownmenu);
        input_group.append(dropdown, form_check);
        td_actions.appendChild(input_group);

        namecol.appendChild(namespan);
        covercol.appendChild(cover);
        namerow.append(covercol, namecol);
        td_name.appendChild(namerow);

        tr.append(td_name, td_artist, td_album, td_date, td_ext, td_actions);
        $("#emptyrow").remove();
        $("#recordstable").children("tbody").append(tr);
        createDropdownMenu(itemdata["id"], itemdata["ytid"]);
    }

    function fetchDownloadData() {
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
        downloadData = {
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
        return downloadData;
    }

    function fetchMetadata() {
        let release_id = $(".audiocol-checkbox:checked").parent().parent().attr('id');
        let people = {};
        let metadata_source = $("#audiocol").length > 0 ? $(".audiocol-checkbox:checked").parents('li').find('span.metadatasource').text() : "Unavailable";
        let cover_url = $("#audiocol").length > 0 ? $(".audiocol-checkbox:checked").parents('li').children('img').attr('src') : "Unavailable";

        if(metadata_source == 'Unavailable') {
            // The priority order is: Spotify -> Deezer -> Musibrainz
            var trackid = $("#spotify_trackid").length > 0 ? $("#spotify_trackid").val() : ($("#deezer_releaseid").val().length > 0 ? $("#deezer_trackid").val() : $("#mbp_trackid").val());
            var albumid = $("#spotify_albumid").length > 0 ? $("#spotify_albumid").val() : ($("#deezer_albumid").val().length > 0 ? $("#deezer_albumid").val() : $("#mbp_albumid").val());
        } else if(metadata_source == 'Spotify') {
            var trackid = $("#spotify_trackid").val();
            var albumid = $("#spotify_albumid").val();   
        } else if(metadata_source == 'Musicbrainz') {
            var trackid = $("#mbp_releaseid").val();
            var albumid = $("#mbp_albumid").val();
        } else if(metadata_source == 'Deezer') {
            var trackid = $("#deezer_trackid").val();
            var albumid = $("#deezer_albumid").val();
        } else if(metadata_source == 'Genius') { 
            var trackid = $("#genius_songid").val();
        }

        $.each($('.artist_relations'), function() {
            if($(this).val().trim().length < 1 || $(this).parent().siblings().find('.artist_relations').val().trim().length < 1) {
                return;
            } else {
                // Get ID by removing all letters from the ID, so the number remains
                let id = $(this).parents('.personrow').attr('id').replace(/[a-zA-Z]/g, '');
                if(this.id.replace(/[0-9]/g, '') == 'artist_relations_name') {
                    people[id].name = $(this).val();
                } else {
                    people[id].type = $(this).val();
                }
            }
        });

        let artists = $("#md_artists").val().split(';');
        let albumartists = $("#md_album_artists").val().split(';');
        let metadata = {
            'trackid': trackid,
            'albumid': albumid,
            'title': $("#md_title").val(),
            'artists': JSON.stringify(artists),
            'album': $("#md_album").val(),
            'album_artists': JSON.stringify(albumartists),
            'album_tracknr': $("#md_album_tracknr").val(),
            'album_releasedate': $("#md_album_releasedate").val(),
            'cover': $("#md_cover").val(),
            'people': JSON.stringify(people),
            'release_id': release_id,
            'cover_url': cover_url,
            'source': metadata_source
        };
        return metadata;
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

    function createSearchResult(data) {
        let ul = document.createElement('ul');
        let li = document.createElement('li');
        let img = document.createElement('img');
        let body = document.createElement('div');
        let header = document.createElement('a');
        let channel = document.createElement('a');
        let desc = document.createElement('p');

        ul.classList.add('list-unstyled', 'youtuberesult');
        img.classList.add('img-fluid');
        body.classList.add('media-body');
        header.classList.add('youtubelink');

        header.href = data.link;
        header.innerText = data.title;
        header.target = '_blank';
        header.classList.add('youtubelink', 'darkanchor');

        img.src = data.thumbnails[0].url;
        channel.href = data.channel.link;
        channel.innerText = data.channel.name;
        channel.target = '_blank';
        channel.className = 'darkanchor'

        ul.setAttribute('style', 'cursor: pointer');

        desc.innerHTML = 'Channel: ' + channel.outerHTML + '<br />Description: ';
        try {
            for(let i = 0; i < data.descriptionSnippet.length; i++) {
                desc.innerHTML += data.descriptionSnippet[i].text;
            }
        } catch {
            desc.innerHTML += 'No description available';
        }
        if($(window).width() >= 700) {
            li.classList.add('media');
        }
        body.append(header, desc);
        li.append(img, body);
        ul.append(li);
        $("#defaultview").find('.spinner-border').remove();
        $("#defaultview").removeClass(['d-flex', 'justify-content-center']);
        $("#defaultview").append(ul);
    }

    function insertFileBrowserItem(item) {
        // Thanks to https://stackoverflow.com/a/18650828
        function formatBytes(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
        
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        
            const i = Math.floor(Math.log(bytes) / Math.log(k));
        
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }

        let tr = document.createElement('tr');
        let td_filename = document.createElement('td');
        let td_lastmodified = document.createElement('td');
        let td_filesize = document.createElement('td');
        let span = document.createElement('span');
        let itemicon = document.createElement('i');
        let removeicon = document.createElement('i');
        let removeanchor = document.createElement('a');
        let nbsp = document.createTextNode('\u00A0');
        
        let extensions = item["filename"].split('.')[item["filename"].split('.').length - 1].toUpperCase();
        let video_extensions = ['MP4', 'M4A', 'FLV', 'WEBM', 'OGG', 'MKV', 'AVI'];
        let iconclass = 'bi';
        let timestamp = new Date(item["lastmodified"] * 1000);

        span.innerText = item['filename'];
        td_lastmodified.innerText = timestamp.toLocaleString();
        td_filesize.innerText = formatBytes(item["filesize"]);

        td_filename.classList.add('text-dark');
        td_lastmodified.classList.add('text-dark');
        td_filesize.classList.add('text-dark');

        td_filename.style.width = '40%';
        td_lastmodified.style.width = '30%';
        td_filesize.style.width = '30%';

        if(item["pathtype"] == 'directory') {
            let confirm = document.createElement('button');
            let cancel = document.createElement('button');
            let popovergroup = document.createElement('div');
    
            confirm.classList.add('btn', 'btn-danger', 'confirmremoval');
            cancel.classList.add('btn', 'btn-success', 'cancelremoval');
            popovergroup.classList.add('btn-group');
    
            confirm.type = 'button';
            cancel.type = 'button';
            confirm.innerText = 'Confirm';
            cancel.innerText = 'Cancel';
    
            popovergroup.setAttribute('role', 'group');
            popovergroup.setAttribute('aria-label', 'Button group');
            popovergroup.setAttribute('filepath', item["filepath"]);
            popovergroup.append(cancel, confirm);

            removeanchor.href = 'javascript:void(0)';
            removeanchor.classList.add('text-dark', 'removefolder');
            removeanchor.style.textDecoration = 'None';
            removeanchor.style.float = 'right';

            let popoveroptions = {
                'html': true,
                'placement': 'auto',
                'title': 'Delete directory?',
                'trigger': 'focus',
                'content': popovergroup,
            };
            $(removeanchor).popover(popoveroptions);

            removeicon.classList.add('bi', 'bi-folder-minus')
            removeanchor.append(removeicon);
            td_lastmodified.append(removeanchor);
            iconclass += ' bi-folder-fill';
        } else {
            if(video_extensions.indexOf(extensions) > -1) {
                iconclass += ' bi-camera-video-fill';
            } else {
                iconclass += ' bi-file-music-fill';
            }
        }

        itemicon.className = iconclass;

        if('createnewfolder' in item) {
            let input = document.createElement('input');
            let button = document.createElement('button');
            let check = document.createElement('i');
            let form = document.createElement('span');
            
            input.classList.add('form-control', 'directory_input', 'w-75');
            input.setAttribute('placeholder', 'Enter directory name');
            form.classList.add('form-inline');
            form.append(itemicon, nbsp, input);
            td_filename.append(form);

            button.classList.add('btn', 'btn-success', 'createdirectorybtn', 'ml-2');
            button.type = 'button';
            button.setAttribute('data-toggle', 'tooltip');
            button.setAttribute('data-placement', 'right');
            button.title = 'Create directory';
            check.classList.add('bi', 'bi-check');
            button.append(check);

            td_lastmodified.append(button);
        } else {
            td_filename.append(itemicon, nbsp, span);
        }
        
        tr.classList.add('filebrowserrow', item["pathtype"]);
        tr.style.cursor = 'pointer';
        tr.setAttribute('filepath', item["filepath"]);
        tr.append(td_filename, td_filesize, td_lastmodified);
        if($("#filebrowserup").parent().children().length == 1 || !('createnewfolder' in item)) {
            $("#filebrowserup").parent().children(':last-child').after(tr);
        }
        else {
            if($(".file").length > 0) {
                $('.file:first').before(tr);
            } else {
                $('.directory:last').after(tr);
            }
        }
    }

    function createDropdownMenu(rowid, youtube_id=null) {
        let editfilebtn = document.createElement('a');
        let editmetadatabtn = document.createElement('a');
        let downloaditembtn = document.createElement('a');
        let playitembtn = document.createElement('a');
        let moveitembtn = document.createElement('a');
        let youtubebtn = document.createElement('a');
        let deletebtn = document.createElement('a');

        let elements = [editfilebtn, editmetadatabtn, downloaditembtn, playitembtn, moveitembtn, youtubebtn, deletebtn];
        let metadata_extensions = ['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A'];
        let extension = $("tr#" + rowid).children('.td_ext').text();

        elements.forEach((button) => {
            button.href = 'javascript:void(0)';
            button.className = 'dropdown-item';
        });

        editfilebtn.innerText = 'Change filedata';
        editmetadatabtn.innerText = metadata_extensions.indexOf(extension) > -1 ? 'Change metadata' : 'Metadata is not supported';
        downloaditembtn.innerText = 'Download item';
        playitembtn.innerText = 'Play item';
        moveitembtn.innerText = 'Move item\'s file location';
        youtubebtn.innerText = 'View YouTube video';
        deletebtn.innerText = 'Delete item';

        editfilebtn.classList.add('d-none', 'd-md-block', 'editfilebtn');
        editmetadatabtn.classList.add('d-none', 'd-md-block', 'editmetadatabtn');
        moveitembtn.classList.add('d-none', 'd-md-block', 'moveitembtn');
        downloaditembtn.classList.add('downloaditembtn');
        playitembtn.classList.add('playitembtn');
        deletebtn.classList.add('deleteitembtn');

        if(youtube_id != null) {
            youtubebtn.href = youtube_id;
            $("tr#" + rowid).find('.dropdown-menu').append(youtubebtn, deletebtn);
        }
        $("tr#" + rowid).find('.dropdown-menu').children(':first-child').before(editfilebtn, editmetadatabtn, downloaditembtn, playitembtn, moveitembtn);
        $("tr#" + rowid).find('.finditembtn').remove();
    }

    $(window).resize(function() {
        if ($(window).width() < 700) {
            $(".youtuberesult").children('li').removeClass('media');
        } else {
            $(".youtuberesult").children('li').addClass('media');
        }
        if($(window).width() < 650) {
            $("#ytcol").children('div').removeClass('media');
        } else {
            $("#ytcol").children('div').addClass('media');
        }
        if($(window).width() < 600) {
            $('.mbp-item').removeClass('media');
            let input_group = $(".mbp-item").children('.input-group-text');
            for(let i = 0; i < input_group.length; i++) {
                let li = $('.mbp-item')[i];
                $(li).children('.media-body').before(input_group[i]);
            }
            input_group.addClass('float-right');
            $(".mbp-item").removeClass('media');
            $(".mbp-item").children('img').addClass(['mw-100', 'w-75']);
        } else {
            let input_group = $(".mbp-item").children('.input-group-text');
            for(let i = 0; i < input_group.length; i++) {
                let li = $('.mbp-item')[i];
                $(li).children('.media-body').after(input_group[i]);
            }
            input_group.removeClass('float-right');
            $('.mbp-item').addClass('media');
            $(".mbp-item").children('img').removeClass(['mw-100', 'w-75']);
        }
        if($(window).width() < 992) {
            $(".td_name").find('.col').removeClass('col');
        } else {
            $(".td_name").children('.row').children('div').addClass('col');
        }
    }).resize();

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

    $(document).on('keydown', '#outputname', submitOutputTemplate)

    $(document).on('click', ".removesegment", function() {
        $(this).parents('.form-row').remove();
    });
    $(document).on('click', "#addsegment", function() {
        let id = $(this).parents('.form-row').siblings('.timestamp_row').length > 0 ? parseInt($(this).parents('.form-row').siblings('.timestamp_row:last').attr('id').slice(4)) + 1 : parseInt($(this).parents('.form-row').attr('id').slice(4)) + 1;
        addSegment(id);
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
        if($("#extension option:selected").hasAttr('nosupport')) {
            $("#nextbtn").addClass('d-none');
            $("#downloadbtn").removeClass('d-none');
        } else {
            $("#nextbtn").removeClass('d-none');
            $("#downloadbtn").addClass('d-none');
        }
        submitOutputTemplate();
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

    $(document).on('click', '#metadataviewbtn', function() {
        $("#geniuscol, #audiocol, #metadataviewbtn, #geniusbtn").toggleClass('d-none');
    })
    
    $(document).on('click', "#editmetadata", function() {
        $("#audiocol, #geniuscol, #queryform, #geniusbtn, #downloadbtn, #resetviewbtn, #metadataviewbtn").addClass('d-none');
        $("#metadataview").removeClass('d-none')
        $(this).attr('id', 'savemetadata');
        $(this).text('Save metadata')
    });
    
    $(document).on('click', '#savemetadata', function() {
        $("#audiocol, #geniuscol, #queryform, #geniusbtn, #downloadbtn, #resetviewbtn, #metadataviewbtn").removeClass('d-none');
        $("#metadataview").addClass('d-none')
        if($("#audiocol").length < 1) {
            $("#searchmetadataview").removeClass('d-none');
        }
        $(this).attr('id', 'editmetadata');
        $(this).text('Edit metadata')
    });

    $(document).on('click', '.addperson', addPerson);

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

    $(document).on('change', ".selectitem", function() {
        if($(".selectitem:checked").length > 0) {
            if($(".selectitem:checked").length == $(".selectitem").length) {
                $("#selectall").prop('checked', true);
            }
            $("#bulkactionsrow").css('visibility', 'visible');
        } else {
            $("#selectall").prop('checked', false);
            $("#bulkactionsrow").css('visibility', 'hidden');
        }
    });
    
    $(document).on('click', ".deleteitembtn", function() {
        $("#removeitemmodal").find('.btn-danger').attr('id', '["' + $(this).parents('tr').attr('id') + '"]');
        $("#removeitemmodaltitle").text('Delete ' + $(this).parents('tr').children(':first').text())
        $("#removeitemmodal").addClass(['d-flex', 'justify-content-center']);
        $("#removeitemmodal").find('p').html('Are you sure you want to delete this item? <br />This action will delete the file itself too!');
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
        socket.emit('downloaditem', id);
    });

    $(document).on('click', '.playitembtn', function() {
        let id = $(this).parents('tr').attr('id');
        socket.emit('playitem', id);
    });

    $(document).on('click', '.finditembtn', function() {
        let id = $(this).parents('tr').attr('id');
        let visible = ['files', 'directories'];
        socket.emit('showfilebrowser', visible, id);
    });

    $(document).on('click', '.moveitembtn', function() {
        let id = $(this).parents('tr').attr('id');
        let visible = ['directories'];
        socket.emit('showfilebrowser', visible, id);
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

    $(document).on('click', '#fetchspotifytrack', function() {
        let track_id = $(this).parent().siblings('input').val();
        if(track_id.length > 0) {
            socket.emit('fetchspotifytrack', track_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").text('<p>Enter a Spotify track ID!</p>')
        }
    });

    $(document).on('click', '#fetchdeezertrack', function() {
        let track_id = $(this).parent().siblings('input').val();
        if(track_id.length > 0) {
            socket.emit('fetchdeezertrack', track_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").text('<p>Enter a Deezer track ID!</p>')
        }
    });

    $(document).on('click', '#fetchgeniussong', function() {
        let song_id = $(this).parent().siblings('input').val();
        if(song_id.length > 0) {
            socket.emit('fetchgeniussong', song_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").text('<p>Enter a Genius song ID!</p>')
        }
    });

    $(document).on('click', '#fetchgeniusalbum', function() {
        let album_id = $(this).parent().siblings("input").val();
        if(album_id.length > 0) {
            socket.emit("fetchgeniusalbum", album_id)
        } else {
            $("p:contains('* All input fields with an *, are optional')").text('<p>Enter a Genius song ID!</p>')
        }
    });

    $(document).on('click', '#editmetadatabtnmodal', function() {
        if($("#metadatasection").find('input[required]').val() == '') {
            $("#metadatalog").text('Fill all required fields!');
        } else if($("#outputname").val().startsWith('tmp_')) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#metadatalog").text('Your output name can not begin with tmp_!');
        } else {
            let people = {};
            let filepath = $("#item_filepath").val();
            let id = $("#edititemmodal").attr('itemid');
            let trackid = $("#spotify_trackid").length > 0 ? $("#spotify_trackid").val() : $("#mbp_releaseid").val();
            let albumid = $("#spotify_albumid").length > 0 ? $("#spotify_albumid").val() : $("#mbp_albumid").val();
            let source = $("#spotify_trackid").length > 0 ? 'Spotify' : 'Musicbrainz';
            $.each($('.artist_relations'), function() {
                if($(this).val().trim().length < 1 || $(this).parent().siblings().find('.artist_relations').val().trim().length < 1) {
                    return;
                } else {
                    // Get ID by removing all letters from the ID, so the number remains
                    let id = $(this).parents('.personrow').attr('id').replace(/[a-zA-Z]/g, '');
                    if(this.id.replace(/[0-9]/g, '') == 'artist_relations_name') {
                        people[id].name = $(this).val();
                    } else {
                        people[id].type = $(this).val();
                    }
                }
            });
            
            let metadata = {
                'trackid': trackid,
                'albumid': albumid,
                'title': $("#md_title").val(),
                'artists': $("#md_artists").val(),
                'album': $("#md_album").val(),
                'album_artists': $("#md_album_artists").val(),
                'album_tracknr': $("#md_album_tracknr").val(),
                'album_releasedate': $("#md_album_releasedate").val(),
                'cover': $("#md_cover").val(),
                'people': JSON.stringify(people),
                'source': source
            };
            socket.emit('editmetadatarequest', metadata, filepath, id);
            $("#progressedit").attr({
                'aria-valuenow': '66',
                'aria-valuemin': '0',
                'style': 'width: 66%'
            });
            $("#progresstextedit").text('Skipping download and processing, adding metadata...');
            $("#downloadsection, #metadatasection, #editmetadatabtnmodal").addClass('d-none');
            $("#progressection").removeClass('d-none');
        }
    });

    $(document).on('click', '#editfilebtnmodal', function() {
        $("#downloadsection").find('h5').after('<p class="text-center" id="editfilelog"></p>');
        if($(".timestamp_input").val() == '' && !$("#segments_check").is(':checked')) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#editfilelog").text('Enter all segment fields or disable the segments');
        } else {
            let url = $("#edititemmodal").attr('ytid');
            let ext = $("#extension").val();
            let output_folder = $("#output_folder").val();
            let type = $("#type").val();
            let output_format = "tmp_" + $("#outputname").val();
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
                    $("#metadatasection, #downloadsection, #editfilebtnmodal").addClass('d-none');
                    $("#progressection").removeClass('d-none');
                }
            });
        }
    });

    $(document).on('click', '.youtuberesult', function() {
        let link = $(this).find('.youtubelink').attr('href');
        socket.emit('ytdl_search', link);
        $("#defaultview").children('ul').remove();
        $("#searchlog, #progresstext").empty();
        $("#defaultview").addClass(['d-none', 'justify-content-center'])
        $("#defaultview").removeClass('d-none');
        createSpinner('Loading', $("#defaultview").empty());
        // Reset the modal
        $("#progress").attr('aria-valuenow', "0").css('width', '0');
        $("#searchvideomodalfooter, #metadataview, #progressview, #downloadfilebtn").addClass('d-none');
        $(".removeperson").parents('.personrow').remove();
        $("#metadataview").find('input').val('');
    });


    $(document).on('click', '#outputfolderbtn', function() {
        $("#downloadmodal").modal('hide');
        let id = '-1'
        let visible = ['directories'];
        socket.emit('showfilebrowser', visible, id);
    })

    $(document).on('keyup', '.directory_input', function(e) {
        e.preventDefault();
        let match = '^[^<>:;,?"*|/]+$';
        if(!$(this).val().match(match) && $(this).val() != '') {
            e.preventDefault();
            $("#filebrowserlog").text('Directory contains invalid characters!');
            $(this).parent().parent().siblings(':last-child').children('button').addClass('disabled');
            $(this).parent().parent().siblings(':last-child').children('button').attr('disabled', '');
        } else if($(this).val() == '') {
            $("#filebrowserlog").text('');
            $(this).parent().parent().siblings(':last-child').children('button').addClass('disabled');
            $(this).parent().parent().siblings(':last-child').children('button').attr('disabled', '');
        } else {
            $("#filebrowserlog").text('');
            $(this).parent().parent().siblings(':last-child').children('button').removeClass('disabled');
            $(this).parent().parent().siblings(':last-child').children('button').removeAttr('disabled');
        }
    });

    $(document).on('click', '.createdirectorybtn', function() {
        let directoryname = $(this).parent().siblings(':first-child').find('input.directory_input').val();
        let currentdirectory = $("#filebrowsertitle").children('span').text();
        let newrow = $(this).parents('tr');
        socket.emit('createdirectory', currentdirectory, directoryname, function(response) {
            $("#filebrowserlog").text(response.msg);
            if(response.status == 200) {
                newrow.attr('filepath', response.filepath);
                let icon = document.createElement('i');
                let span = document.createElement('span');
                let nbsp = document.createTextNode('\u00A0');
                span.innerText = directoryname;
                icon.classList.add('bi', 'bi-folder-fill');
                newrow.children(':first-child').empty();
                newrow.children(':first-child').append(icon, nbsp, span);
                newrow.find('button').tooltip('hide');
                newrow.find('button').remove();
            }
        });
    });

    $(document).on('click', '.removefolder', function(e) {
        e.stopPropagation();
        $(this).popover('toggle');
    });

    $(document).on('click', '.cancelremoval', function() {
        $(this).parents('a.removefolder').popover('hide');
    });
    
    $(document).on('click', '.confirmremoval', function() {
        let directory = $(this).parents('.btn-group').attr('filepath');
        if(directory == 'new') {
            $('tr.directory[filepath="new"]').remove();
        } else {
            socket.emit('removedirectory', directory, function(response) {
                $("#filebrowserlog").text(response.msg);
                if(response.status == 200) {
                    $('tr.directory:contains("'+response.directory+'")').remove();
                }
            });
        }
    });

    $(document).on('click', '.filebrowserrow', function() {
        if($(this).hasClass('directory')) {
            if($(this).find('input.directory_input').length < 1) {
                let directorypath = $(this).attr('filepath');
                let id = $("#filebrowsermodal").attr('item');
                let visible = $("#filenameform").hasClass('d-none') ? ['files', 'directories'] : ['directories'];
                socket.emit('showfilebrowser', visible, id, directorypath);
            }
        } else {
            if($(this).hasClass('selectedrow')) {
                $(this).removeClass('selectedrow');
                $("#selectfilebtn").addClass('disabled');
                $("#selectfilebtn").attr('disabled', '');
                $("#selectedfile").text('');
            } else if($(".selectedrow").length > 0) {
                $('.selectedrow').removeClass('selectedrow');
                $(this).addClass('selectedrow');
                $("#selectedfile").text('Selected file ' + $(this).find('span').text());
            } else {
                $(this).toggleClass('selectedrow');
                $("#selectfilebtn").removeClass('disabled');
                $("#selectfilebtn").removeAttr('disabled');
                $("#selectedfile").text('Selected file ' + $(this).find('span').text());
            }
        }
    });

    $("#filebrowserup").on('click', function() {
        let currentdirectory = $("#filebrowsertitle").children('span').text();
        let id = $("#filebrowsermodal").attr('item');
        let visible = $("#filenameform").hasClass('d-none') ? ['files', 'directories', 'parent'] : ['directories', 'parent'];
        socket.emit('showfilebrowser', visible, id, currentdirectory);
    });

    $("#selectfilebtn").on('click', function() {
        let selectedfile = $('.selectedrow').attr('filepath');
        let id = $("#filebrowsermodal").attr('item');
        socket.emit('updatefile', selectedfile, id);
    });

    $("#filenameform").on('submit', function(e) {
        e.preventDefault();
        let filename = $("#filename").val();
        let directory = $("#filebrowsertitle").children('span').text();
        let id = $("#filebrowsermodal").attr('item');
        let overwrite = $("#overwritecheck").is(':checked') ? true : false
        socket.emit('movefile', directory, filename, id, overwrite, function(msg) {
            $("#filebrowserlog").text(msg);
        });
    });

    $("#closefilebrowserbtn").on('click', function() {
        $("#filebrowsermodal").modal('hide');
        if($("#filebrowsermodal").attr('item') === '-1') {
            $("#downloadmodal").modal('show');
        }
    })

    $("#selectdirectorybtn").on('click', function() {
        let directory = $('#filebrowsertitle').children('span').text();
        $("#output_folder").val(directory);
        $("#filebrowsermodal").modal('hide');
        $("#downloadmodal").modal('show');
    });
    $('#downloadmodal').on('shown.bs.modal', function() {
        $("body").addClass("modal-open");  // for some reason it doesn't add this class, making the screen unscrollable, which is why I'm adding this manually
    });

    $(".addfolder").on('click', function() {
        item = {
            'filepath': 'new',
            'filename': '',
            'lastmodified': Date.now() / 1000,
            'filesize': 0,
            'pathtype': 'directory',
            'createnewfolder': true
        };
        insertFileBrowserItem(item);
    });

    $("#filename").on('keyup', function(e) {
        let match = '^[^<>:;,?"*|/]+$';
        if(!$(this).val().match(match) && $(this).val() != '') {
            e.preventDefault();
            $("#filebrowserlog").text('Filename contains invalid characters!');
            $("#submitfilename").addClass('disabled');
            $("#submitfilename").attr('disabled', '');
        } else if($(this).val() == '') {
            $("#filebrowserlog").text('');
            $("#submitfilename").addClass('disabled');
            $("#submitfilename").attr('disabled', '');
        } else {
            $("#filebrowserlog").text('');
            $("#submitfilename").removeClass('disabled');
            $("#submitfilename").removeAttr('disabled');
        }
    });

    $("#nextbtn").on('click', function() {
        if($(".timestamp_input").val() == '' && !$("#segments_check").is(':checked')) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Enter all segment fields or disable the segments');
        } else if($("#audiocol").length > 0){
            $("#audiocol, #editmetadata, #downloadbtn, #resetviewbtn").removeClass('d-none');
            $("#nextbtn, #ytcol").addClass('d-none');
        } else if($("#outputname").val().startsWith('tmp_')) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Your output name can not begin with tmp_!');
        } else if($("#proxy_type").val() != 'None' && $("#proxy_row").find('input[required]').val() == '') {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Enter a proxy port and address!');
        } else {
            let args = {
                'title': $("#trackspan").text() != 'Unknown' ? $("#trackspan").text() : $(".media-body").children('h5').text().replace('(Official Video)', '').trim(),
                'artist': $("#artistspan").text() != 'Unknown' ? $("#artistspan").text() : $("#channelspan").text(),
                'type': 'webui'
            };
            socket.emit('searchmetadata', args);
            $("#searchlog, #progresstext").empty();
            $("#defaultview").addClass(['d-flex', 'justify-content-center'])
            createSpinner("Loading metadata...", $("#defaultview"));
            $("#searchvideomodalfooter, #ytcol").addClass('d-none');
        }
    });

    $("#selectall").on('click', function(e) {
        if($(".selectitem").length > 0) {
            if($(this).is(':checked')) {
                $("#bulkactionsrow").css('visibility', 'visible');
                $(".selectitem").prop('checked', true);
            } else {
                $("#bulkactionsrow").css('visibility', 'hidden');
                $(".selectitem").prop('checked', false);
            }
        } else {
            e.preventDefault()
        }
    });

    $("#downloaditems").on('click', function() {
        let items = [];
        for(let i = 0; i < $(".selectitem:checked").length; i++) {
            items.push($($(".selectitem:checked")[i]).parents('tr').attr('id'));
        }
        socket.emit('downloaditems', items);
    });

    $("#deleteitems").on('click', function() {
        let items = [];
        for(let i = 0; i < $(".selectitem:checked").length; i++) {
            items.push($($(".selectitem:checked")[i]).parents('tr').attr('id'));
        }
        $("#removeitemmodal").find('.btn-danger').attr('id', JSON.stringify(items));
        $("#removeitemmodaltitle").text('Deleting ' + items.length + " items");
        $("#removeitemmodal").find('p').html('Are you sure you want to delete these items? <br />This action will delete the files themselves too!')
        $("#removeitemmodal").modal('show');
    });

    $("#delitembtnmodal").on('click', function() {
        let items = JSON.parse(this.id);
        socket.emit('deleteitem', this.id, function(ack) {
            if(ack == 'OK') {
                for(let i = 0; i < items.length; i++) {
                    $("tr#"+items[i]).remove();
                }
                $("#removeitemmodal").modal('hide');
            }
        });
    });

    $("#queryform").on('submit', function(e) {
        e.preventDefault();
        $("#searchsongbtn").trigger('click');
    });

    $("#metadataqueryform").on('submit', function(e) {
        e.preventDefault();
        $("#searchmetadatabtn").trigger('click');
    });
    
    $("#searchsongbtn").on('click', function() {
        // Send request to the server
        let query = $("#query").val();
        socket.emit('ytdl_search', query);
        $("#searchlog, #progresstext").empty();
        $("#defaultview").removeClass('d-none');
        $("#defaultview").addClass(['d-flex', 'justify-content-center']);
        $("#defaultview").children('.youtuberesult').remove();
        createSpinner("Loading...", $("#defaultview"));
        // Reset the modal
        $("#progress").attr('aria-valuenow', "0").css('width', '0');
        $("#searchvideomodalfooter, #metadataview, #progressview, #downloadfilebtn, #searchmetadataview, #geniusbtn").addClass('d-none');
        $(".removeperson").parents('.personrow').remove();
        $("#metadataview").find('input').val('');
        $("#ytcol, #audiocol").empty();
    });

    $("#downloadbtn").on('click', function(e) {
        if($(".audiocol-checkbox:checked").length < 1 && $("#audiocol").length > 0 && !$("#extension option:selected").hasAttr('nosupport')) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Select a release on the right side before downloading a video');
        }  else if($(".timestamp_input").val() == '' && !$("#segments_check").is(':checked')) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Enter all segment fields or disable the segments');
        } else if($("#audiocol").length < 1 && $("#metadataview").find('input[required]').val() == '' && !$("#extension option:selected").hasAttr('nosupport')) {
            $("#metadatalog").text('Enter all required fields!');
        } else {
            let data = {
                'downloadData': fetchDownloadData(),
                'metadata': fetchMetadata()
            }

            socket.emit('ytdl_download', data, function(ack) {
                if(ack == "OK") {
                    $("#editmetadata, #downloadbtn, #searchmetadataview, #404p, #defaultview, #resetviewbtn, #geniusbtn, #audiocol, #savemetadata, #metadataview, #geniuscol").addClass('d-none');
                    $("#progressview").removeClass('d-none');
                    $("#searchlog").empty();
                }
            });
        }
    });

    $("#searchitem").on('keyup', function() {
        var table = $("#recordstable").children('tbody').clone(true, true);
        if($(this).val().length > 2) {
            socket.emit('searchitem', $(this).val());
        } else if($(this).val() == '') {
            socket.emit('fetchallitems')
        }
    });

    $("#addvideo").on('click', function() {
        if($("#progress").text() == '100%') {
            $("#defaultview, #downloadbtn").removeClass('d-none');
            $("#progressview, #downloadfilebtn, #searchvideomodalfooter, #searchmetadataview, #404p").addClass('d-none');
            $("#progresstext, #progress").text('');
            $("#progress").attr({
                'aria-valuenow': '0',
                'aria-valuemin': '0',
                'style': ''
            });
        }
        $("#progressview").addClass('d-none');
        $("#downloadmodal").addClass(['d-flex', 'justify-content-center']);
        $("#downloadmodal").modal('toggle');
    });

    $("#downloadmodal, #removeitemmodal, #edititemmodal").on('hidden.bs.modal', function() {
        $(this).removeClass(['d-flex', 'justify-content-center']);
    });

    $("#downloadfilebtn").on('click', function() {
        socket.emit('downloaditem', $(this).attr('filepath'));
    });

    $("#resetviewbtn").on('click', function() {
        if($("#ytcol").children().length > 0) {
            $("#defaultview, #ytcol, #nextbtn").removeClass('d-none');
            $("#progressview, #audiocol, #resetviewbtn, #editmetadata, #downloadbtn, #metadataview, #geniusbtn").addClass('d-none');
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
        } else {
            $("#defaultview, #searchlog").empty();
        }
    });

    $("#geniusbtn").on('click', function() {
        if($(".audiocol-checkbox:checked").length < 1 && $("#audiocol").length > 0) {
            $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
            $("#searchlog").text('Select a release on the right side before searching for lyrics');
        } else {
            $("#audiocol").addClass('d-none');
            let args = {
                'title': $("#trackspan").text() != 'Unknown' ? $("#trackspan").text() : $(".media-body").children('h5').text(),
                'artist': $("#artistspan").text() != 'Unknown' ? $("#artistspan").text() : $("#channelspan").text(),
                'type': 'lyrics'
            };
            createSpinner('Loading Genius data...', $("#defaultview"));
            socket.emit('searchmetadata', args);
            $("#searchmetadataview, #searchvideomodalfooter").addClass('d-none');
        }
    });

    $("#searchmetadatabtn").on('click', function() {
        let args = {
            'title': $("#metadataquery").val(),
            'artist': "",
            'type': 'webui'
        }
        socket.emit('searchmetadata', args);
        // $("#defaultview").children('#audiocol').remove();
        createSpinner('Loading metadata...', $("#defaultview"));
    });

    socket.on('downloadprogress', function(msg) {
        var progress = $("#edititemmodal").css('display').toLowerCase() != 'none' ? $("#progressedit") : $("#progress");
        function setprogress(percentage) { 
            progress.attr({
                'aria-valuenow': percentage + "%",
                'style': 'width: ' + parseInt(percentage) + '%'
            }).text(percentage + "%");
        }

        $("#editmetadata, #nextbtn, #defaultview, #ytcol").addClass('d-none');
        $("#progressview").removeClass('d-none');
        $("#searchlog").empty();
        var progress_text = $("#edititemmodal").css('display').toLowerCase() != 'none' ? $("#progresstextedit") : $("#progresstext");
        let phases = $("#segments_check").is(':checked') ? 4 : 5;

        if(msg.status == 'downloading') {
            if(msg.total_bytes != 'Unknown') {
                if((msg.downloaded_bytes / msg.total_byes) == 1) {
                    progress_text.text("Extracting audio...");
                    setprogress(100 / phases);
                } else {
                    progress_text.text("Downloading...");
                    let percentage = Math.round(((msg.downloaded_bytes / msg.total_bytes) * 100) / phases);
                    setprogress(percentage);
                }
            } else {
                progress_text.text("Downloading...");
            }
        }
        else if(msg.status == 'finished_ytdl') {
            let percentage = 100 / phases;
            setprogress(percentage);
            progress_text.text('Extracting audio...');
        } else if(msg.status == 'finished_ffmpeg') {
            if(msg.postprocessor == 'ExtractAudio') {
                let percentage = (100 / phases) * 2;
                setprogress(percentage);
                progress_text.text('Cutting segments from the video... ');
            } else if(msg.postprocessor == 'ModifyChapters') {
                let percentage = (100 / phases) * 3;
                setprogress(percentage);
                progress_text.text('Moving the files to its destination... ');
            } else if(msg.postprocessor == 'MoveFiles') {
                let percentage = (100 / phases) * (phases - 1);
                setprogress(percentage);
                progress_text.text('Adding metadata...');
                var filepath = msg.filepath;
                if($("#edititemmodal").css('display').toLowerCase() == 'none') {
                    
                   
                    // socket.emit('mergedata', filepath, release_id, metadata, cover, metadata_source);
                } else {
                    let itemid = $("#edititemmodal").attr('itemid');
                    socket.emit('editfilerequest', filepath, itemid);
                }
            }
        } else if(msg.status == 'finished_metadata') {
            setprogress("100");
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
            setprogress("100");
            $("#downloadfilebtn").removeClass('d-none');
            $("#downloadfilebtn").attr('filepath', msg.data["filepath"]);
            socket.emit('insertitem', msg.data);
        } else if(msg.status == 'error') {
            progress_text.text(msg.message);
            progress.attr('aria-valuenow', 100);
            progress.html('ERROR <i class="fi-cwluxl-smiley-sad-wide" aria-hidden="true"></i>');
            progress.css('width', '100%');
            progress_text.text(msg.message);
            if($("#edititemmodal").css('display').toLowerCase() != 'block') {
                $("#resetviewbtn").removeClass('d-none');
            }
        }
    });

    socket.on('ytdl_response', (video, downloadform, metadataform) => {
        console.info('Got YouTube info');
        $("#metadataview").empty().prepend(metadataform);
        insertYTcol(video, downloadform);
        submitOutputTemplate();
        ytdata = video;
    });

    socket.on('mbp_response', (mbp) => {
        console.info('Got musicbrainz info');
        mbpdata = mbp;
        $("#searchmetadataview").removeClass('d-none');
        if(Object.keys(mbp).length > 0) {
            // $("#audiocol").empty();
            for(let i = 0; i < Object.keys(mbp).length - 2; i++) {
                insertmusicbrainzdata(mbp[i]);
            }
            $("#metadataquery").val(mbp["query"])
        } else if($("#404p").hasClass('d-none')) {
            $("#defaultview").children('.spinner-border').remove();
            $("#nextbtn, #otherp").addClass('d-none');
            $("#404p, #searchvideomodalfooter, #editmetadata, #resetviewbtn, #geniusbtn").removeClass('d-none');
        }
        $("#searchvideomodalfooter").removeClass('d-none');
    });

    socket.on('spotify_response', (spotify) => {
        console.info('Spotify info');
        spotifydata = spotify;
        $("#searchmetadataview").removeClass('d-none');
        if(spotify["tracks"]["items"].length  > 0) {
            // $("#audiocol").empty();
            for(let i = 0; i < spotify["tracks"]["items"].length; i++) {
                insertspotifydata(spotify["tracks"]["items"][i]);
            }
            $("#metadataquery").val(spotifydata["query"]);
            $("#searchvideomodalfooter, #editmetadata").removeClass('d-none');
        } else if($("#404p").hasClass('d-none')) {
            $("#defaultview").children('.spinner-border').remove();
            $("#nextbtn, #otherp").addClass('d-none');
            $("#404p, #searchvideomodalfooter, #editmetadata, #resetviewbtn, #geniusbtn").removeClass('d-none');
        }
    });

    socket.on('deezer_response', (deezer) => {
        console.info('Deezer info');
        deezerdata = deezer;
        $("#searchmetadataview").removeClass('d-none');
        if(deezer.length > 0) {
            // $("#audiocol").empty();
            for(let i = 0; i < deezer.length - 2; i++) {
                insertdeezerdata(deezer[i]);
                $("#searchvideomodalfooter, #editmetadata").removeClass('d-none');
            }
            $("#metadataquery").val(deezer[deezer.length - 1]);
        } else if($("#404p").hasClass('d-none')) {
            $("#defaultview").children('.spinner-border').remove();
            $("#nextbtn, #otherp").addClass('d-none');
            $("#404p, #searchvideomodalfooter, #editmetadata, #resetviewbtn, #geniusbtn").removeClass('d-none');
        }
    });

    socket.on('genius_response', (genius) => {
        console.info('Genius info')
        geniusdata = genius;
        if(geniusdata["hits"].length > 0) {
            for(let i = 0; i < genius["hits"].length; i++) {
                insertgeniusdata(genius["hits"][i]["result"])
                $("#searchvideomodalfooter, #editmetadata, #metadataviewbtn").removeClass('d-none');
            }
            $("#geniusbtn").addClass('d-none');
        } else {
            $("#defaultview").children('.spinner-border').remove();
            $("#nextbtn, #otherp, #geniusbtn").addClass('d-none');
            $("#404p, #searchvideomodalfooter, #editmetadata, #resetviewbtn").removeClass('d-none');
        }
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
            if(response.resolution.split(';').indexOf('best') > -1) {
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
        $("#mbp_albumid").val(album_id);
    
        if("artist-relation-list" in mbp["release"] && mbp["release"]["artist-relation-list"].length > 0) {
            $.each(mbp["release"]["artist-relation-list"], function(key, value) {
                let name = value.artist.name;
                let type = value.type;
                if($(".personrow").length > 1 || ($("#artist_relations_name0").val() != "" || $("#artist_relations_type0").val() != "")) {
                    var row = addPerson($(".addperson"));
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

    socket.on('spotify_track', (data) => {
        let artists = "";
        let albumartists = "";
        let cover = "";

        for(let i = 0; i < Object.keys(data["artists"]).length; i++) {
            artists += data["artists"][i]["name"] + "; ";
        }
        for(let i = 0; i < Object.keys(data["album"]["artists"]).length; i++) {
            albumartists += data["album"]["artists"][i]["name"] + "; ";
        }
        for(let i = 0; i < Object.keys(data["album"]["images"]).length; i++) {
            if(data["album"]["images"][i]["height"] == '300') {
                cover = data["album"]["images"][i]["url"]
            }
        }

        $("#md_title").val(data["name"]);
        $("#md_artists").val(artists.slice(0, artists.length - 2));
        $("#md_album").val(data["album"]["name"]);
        $("#md_album_artists").val(albumartists.slice(0, albumartists.length - 2))
        $("#md_album_tracknr").val(data["track_number"]);
        $("#md_album_releasedate").val(data["album"]["release_date"]);
        $("#spotify_albumid").val(data["album"]["id"]);
        $("#md_cover").val(cover);
    });

    socket.on('deezer_track', (data) => {
        let contributors = "";

        for(let i = 0; i < Object.keys(data["contributors"]).length; i++) {
            contributors += data["contributors"][i]["name"] + "; ";
        }
        $("#md_title").val(data["title"]);
        $("#md_artists").val(contributors);
        $("#md_album").val(data["album"]["title"]);
        $("#md_album_artists").val(data["artist"]["name"])
        $("#md_album_tracknr").val(data["track_position"]);
        $("#md_album_releasedate").val(data["release_date"]);
        $("#spotify_albumid").val(data["album"]["id"]);
        $("#md_cover").val(data["album"]["cover_medium"]);
    });

    socket.on('genius_song', (data) => {
        console.log(data);
        let songdata = data["song"];
        let artists = songdata["primary_artist"]["name"] + "; ";
        for(let i = 0; i < songdata["featured_artists"].length; i++) {
            artists += songdata["featured_artists"][i]["name"] + "; ";
        }
        $("#md_title").val(songdata["title"]);
        $("#md_artists").val(artists.slice(0, artists.length - 2));
        $("#md_album").val(songdata["album"]["name"]);
        $("#md_cover").val(songdata["song_art_image_thumbnail_url"]);
        $("#md_album_releasedate").val(songdata["release_date"]);
        $("#genius_albumid").val(songdata["album"]["id"]);
    });

    socket.on('genius_album', (data) => {
        console.log(data);
        let albumtracks = data["tracks"];
        let albumartists = albumtracks[0]["song"]["primary_artist"]["name"] + "; ";
        for(let i = 0; i < albumtracks.length; i++) {
            if(albumtracks[i]["song"]["featured_artists"].length > 0) {
                for(let j = 0; j < albumtracks[i]["song"]["featured_artists"].length; j++) {
                    albumartists += albumtracks[i]["song"]["featured_artists"][j]["name"] + "; ";
                }
            }
            if(albumtracks[i]["song"]["title"] == $("#md_title").val()) {
                $("#md_album_tracknr").val(i + 1);
            }
        }
        $("#md_album_artists").val(albumartists);
    });

    socket.on('searchvideo', (data) => {
        $("#defaultview").find(".spinner-border").remove();
        $("#searchlog").text(data);
        $("#defaultview").removeClass('d-none');
        $("#progressview, #ytcol, #audiocol").addClass('d-none');
        $("#downloadmodal").animate({ scrollTop: 0 }, 'fast');
    });

    socket.on('overview', (data) => {
        if(data.msg == 'inserted_song') {
            $("#overviewlog").empty();
            addItem(data)
        } else if(data.msg == 'download_file') {
            filedata = data.data;
            let blob = new Blob([filedata], {'type': data.mimetype});
            let uri = URL.createObjectURL(blob);
            downloadURI(uri, data.filename);
        } else if(data.msg == 'play_file') {
            let filedata = data.data;
            let itemdata=  data.itemdata;
            let blob = new Blob([filedata], {'type': data.mimetype});
            let uri = URL.createObjectURL(blob);
            ap.list.add([{
                name: itemdata["name"],
                artist: itemdata["artist"],
                url: uri,
                cover: itemdata["cover"]
            }]);
            ap.play();
            $("#recordstable").parent().css('height', '65vh');
            $("#audioplayer").removeClass('d-none')
        } else if(data.msg == 'changed_metadata') {
            socket.emit('updateitem', data.data);
        } else if(data.msg == 'changed_metadata_db') {
            let tr = $("tr#"+data.data.itemid);
            tr.find('img').attr('src', data.data.image);
            tr.find('img').siblings('span').text(data.data.name);
            tr.find('.td_artist').text(data.data.artist);
            tr.find('.td_album').text(data.data.album);
            tr.find('.td_date').text(data.data.date);
            tr.find('.td_filepath').text(data.data.filepath.split('.')[data.data.filepath.split('.').length - 1]);
            $("#overviewlog").text("Item metadata has been changed!");
            $("#edititemmodal").modal('hide');
        } else if(data.msg == 'deleteitems') {
            $(".selectitem:checked").parents('tr').remove();
            $("#bulkactionsrow").css('visibility', 'hidden');
            $("#selectall").prop('checked', false);
            $("#overviewlog").text(data.data);
        } else if(data.msg == 'showfilebrowser') {
            $("#filebrowserup").siblings('tr').remove();
            if(data.visible.indexOf('files') > -1) {
                $("#filenameform, #selectdirectorybtn, #submitfilename").addClass('d-none');
                $("#selectedfile, #selectfilebtn").removeClass('d-none');
                $("#browsermodaltitle").text('Select a file');
            } else {
                $("#filenameform, #submitfilename").removeClass('d-none');
                $("#selectedfile, #selectdirectorybtn, #selectfilebtn").addClass('d-none');
                $("#browsermodaltitle").text('Select a directory');
            }
            if(data.files.length > 0) {
                for(let i = 0; i < data.files.length; i++) {
                    insertFileBrowserItem(data.files[i]);
                }
            } else {
                let tr = document.createElement('tr');
                let td = document.createElement('td');
                td.setAttribute('colspan', 3);
                td.classList.add('text-dark', 'text-center');
                td.innerHTML =  data.visible.indexOf('files') > -1 ? 'No files or directories found with any of the following extensions: <br/> AAC, FLAC, MP3, M4A, OPUS, VORBIS, WAV, MP4, M4A, FLV, WEBM, OGG, MKV, AVI' : 'No directories found';
                tr.append(td);
                $("#filebrowserup").after(tr);
            }
            if(data.id === "-1") {
                $("#filenameform, #selectfilebtn").addClass('d-none');
                $("#selectdirectorybtn").removeClass('d-none');
            }
            $("#filebrowsertitle").children('span').text(data.directory);
            $("#filebrowsermodal").attr('item', data.id);
            $("#filebrowsermodal").modal('show');
        } else if(data.msg == 'updated_filepath') {
            $("#filebrowsermodal").modal('hide');
            $("#overviewlog").text('File location succesfully updated to ' + data["filepath"]);
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
        $("#metadatasection").find('#md_artists').val(data.metadata.artists);
        $("#metadatasection").find('#md_album').val(data.metadata.album);
        $("#metadatasection").find('#md_album_artists').val(data.metadata.artists);
        $("#metadatasection").find('#md_album_tracknr').val(data.metadata.tracknr);
        $("#metadatasection").find('#md_album_releasedate').val(data.metadata.date);
        $("#metadatasection").find('#md_cover').val(data.metadata.cover);
        $("#metadatasection").prepend('<div class="form-row"><div class="col"><label for="#itemfilepath">Filepath of item:</label><input type="text" value="'+data.metadata.filename+'" class="form-control" id="item_filepath" style="cursor: not-allowed" disabled /></div></div>');
        $("#edititemmodal").attr('itemid', data.metadata.itemid)
        $("#editfilebtnmodal").attr('id','editmetadatabtnmodal');
        $("#metadatasection, #editmetadatabtnmodal").removeClass('d-none');
        $("#progressection").addClass('d-none');
        $("#progressedit").attr({
            'aria-valuenow': '0',
            'aria-valuemin': '0',
            'style': ''
        });
        if(data.metadata.mbp_releasegroupid == '' && data.metadata.mbp_releaseid == '' && $("#spotify_trackid").length > 0) {
            $("#spotify_trackid").val(data.metadata.audio_id);
        }
        
        $("#edititemmodal").addClass(['d-flex', 'justify-content-center']);
        $("#edititemmodal").modal('show');
    });

    socket.on('metadatalog', (msg) => {
        $("#metadatalog").text(msg);
    });

    socket.on('edit_file', (data) => {
        $("#downloadsection, #ytcol, #metadatasection").empty();
        $("#downloadsection").append(data.downloadview);
        $("#progressection").addClass('d-none');
        $("#progressedit").attr({
            'aria-valuenow': '0',
            'aria-valuemin': '0',
            'style': ''
        });
        $("#editmetadatabtnmodal").attr('id', 'editfilebtnmodal');
        $("#downloadsection, #editfilebtnmodal").removeClass('d-none');
        $("#downloadsection").find('hr').remove();
        $("#edititemmodal").attr({'itemid': data.filedata.itemid, 'ytid': data.filedata.youtube_id});
        $("hr").addClass('d-none');
        
        $("#edititemmodal").addClass(['d-flex', 'justify-content-center']);
        $("#edititemmodal").modal('show');
    });

    socket.on('youtubesearch', (data) => {
        searchdata = data;
        $("#defaultview").children().addClass('d-none');
        for(let i = 0; i < Object.keys(data.result).length; i++) {
            createSearchResult(data.result[i]);
        };
    });

    socket.on('ytdl_template', (data) => {
        let extension = $("#extension").val().indexOf('m4a') > -1 ? 'm4a' : $("#extension").val();
        let filename = data.split('.').slice(0, data.split('.').length - 1).join('.') + "." + extension
        if($("#filenamespan").length > 0) {
            $("#filenamespan").text("Filename: " + filename);
        } else {
            $("#albumspan").after('<br/><span id="filenamespan">Filename: '+filename+'</span>');
        }
    })

    socket.on('searchitem', (data) => {
        $("#recordstable").children('tbody').empty();
        if(data.length < 1) {
            let tr = document.createElement('tr');
            let td = document.createElement('td');
            let h5 = document.createElement('h5');
            td.setAttribute('colspan', '6');
            h5.textContent = 'No items found!';
            h5.classList.add("text-center", 'text-dark');
            td.append(h5);
            tr.append(td);
            $("#recordstable").children('tbody').append(tr);
        }
        for(let i = 0; i < data.length; i++) {
            additem({"data": data[i]});
        }
    });

    ap.on('ended', function() {
        if($(".aplayer-list").children('ol').children().length > 1) {
            ap.list.remove($(".aplayer-list-light").index() - 1);
        } else {
            ap.list.clear();
        }
    });
    ap.on('listclear', function() {
        $("#recordstable").parent().css('height', '75vh');
        $("#audioplayer").addClass('d-none');
    })
});