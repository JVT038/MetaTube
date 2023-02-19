<!-- <div align="center" id="top"> 
  <img src="./.github/app.gif" alt="metatube" />

  &#xa0;

  <a href="https://metatube.netlify.app">Demo</a>
</div> -->
<h1 align="center">MetaTube</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/JVT038/metatube">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/JVT038/metatube">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/JVT038/metatube">

  <img alt="License" src="https://img.shields.io/github/license/JVT038/metatube">

  <img alt="Github issues" src="https://img.shields.io/github/issues/JVT038/metatube" />

  <img alt="Github forks" src="https://img.shields.io/github/forks/JVT038/metatube" />

  <img alt="Github stars" src="https://img.shields.io/github/stars/JVT038/metatube" />
</p>

<h2 align="center">Status</h2>

<h4 align="center">
 :heavy_check_mark:  MetaTube 🚀 Finished! :heavy_check_mark: <br/>
</h4>

<hr>

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0;
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="#disclaimer">Disclaimer</a> &#xa0; | &#xa0;
  <a href="https://github.com/JVT038" target="_blank">Author</a>
</p>

<br>

## :dart: About ##

MetaTube downloads video from YouTube and can add metadata from a specified metadata provider on the downloaded file.
Normal view | Dark mode|
--- | ---
![startpage](https://user-images.githubusercontent.com/47184046/147980156-e3ee71e4-a4cd-4fee-808b-c4b3c9530e9f.png) | ![darkstartpage](https://user-images.githubusercontent.com/47184046/147980017-bd3bc8bf-2589-4ee5-8d9c-1785ba906982.png)

## :sparkles: Features ##

It's finished (for now) and these features are currently supported:

:heavy_check_mark: Fetch information from a YouTube video based on an URL <br />
:heavy_check_mark: Query and fetch results from the Musicbrainz API, the Spotify Web API, and the Deezer API <br />
:heavy_check_mark: Set up templates and options for the YouTube download <br />
:heavy_check_mark: Download YouTube videos based on a selected template <br />
:heavy_check_mark: Exclude fragments (such as intros, outros, etc.) from the download <br />
:heavy_check_mark: Metadata from either the user or the chosen metadata provider can be merged with MP3, Opus, FLAC, WAV, OGG, M4A & MP4 files <br />
:heavy_check_mark: Hardware encoding using NVENC, Intel Quick Sync <br />
:heavy_check_mark: Hardware encoding is supported, but not yet tested for Video Toolbox, Video Acceleration API (VAAPI), AMD AMF & OpenMax OMX <br />
:heavy_check_mark: Manually set height and width, if a video type has been selected <br />
:heavy_check_mark: Store the information about downloaded releases in the database, to edit the downloaded metadata or the file itself later after the download <br />
:heavy_check_mark: Dark mode is available <br />
:heavy_check_mark: Docker is [supported](#whale-using-docker)

I'm currently not planning on adding any new features; I'll only fix any bugs, but if you have a nice feature, feel free to create an issue, and I'll decide whether I'll actually do it.

## :rocket: Technologies ##

The following tools were used in this project:

- [Python](https://python.org/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [JavaScript](https://www.javascript.com/)
- [Bootstrap 4.6](https://getbootstrap.com/docs/4.6)
- [Dark Mode Switch](https://github.com/coliff/dark-mode-switch)
- [jQuery 3.6.0](https://jquery.com/)
- [APlayer](https://aplayer.js.org/#/)
- [Youtube-DLP](https://github.com/yt-dlp/yt-dlp)
- [youtube-search-python](https://github.com/alexmercerind/youtube-search-python)
- [Spotipy](https://github.com/plamere/spotipy)
- [Deezer-python](https://github.com/browniebroke/deezer-python)
- [Python Musicbrainz](https://github.com/alastair/python-musicbrainzngs)
- [Sponsorblock.py](https://github.com/wasi-master/sponsorblock.py)
- [FFmpeg 4.4.1](https://ffmpeg.org/)

For a complete list, visit the [Dependencies overview](https://github.com/JVT038/MetaTube/network/dependencies#requirements.txt) in the Insights.

## :white_check_mark: Requirements ##

Before starting :checkered_flag:, you need to have [Git](https://git-scm.com) and [Python 3.8 or higher](https://python.org/downloads) installed.

## :checkered_flag: Starting ##

### :whale: Using Docker ###

CLI docker:

```docker
docker run \
  -d \
  --name metatube \
  --restart always \
  -p 5000:5000 \
  -e PORT=5000 \
  -e HOST=0.0.0.0 \
  -v /downloads:/downloads:rw \
  -v /metatube:/database:rw \
  jvt038/metatube:latest
```

Docker-compose:

```
version: '3.3'
services:
    metatube:
        container_name: metatube
        restart: always
        image: jvt038/metatube:latest
        ports:
            - '5000:5000'
        environment:
            - PORT=5000
            - HOST=0.0.0.0
        volumes:
            - '/downloads:/downloads:rw'
            - '/metatube:/database:rw'        
```

You need to set the variable `DATABASE_URL` to a custom mount point (in these examples `/database`), because otherwise your database file will reset everytime the Docker container updates.

### :hammer_and_wrench: Manually build and start server ###

```bash
# Clone this project
$ git clone https://github.com/JVT038/metatube

# Access
$ cd metatube

# Skip these steps if you don't want to use a virtual environment
# Install virtualenv
$ pip install virtualenv
# Create virtual environment in current directory
$ virtualenv .
# Activate environment
# Windows:
$ cd Scripts
$ activate
# Linux:
$ source bin/activate
 
# Navigate to the root directory
$ cd ../

# Install dependencies
$ pip install -r requirements.txt

# If you're using Windows, you need to install python-magic-bin
$ pip install python-magic-bin
# If you're using Debian / Ubuntu, you'll need to install libmagic1
$ sudo apt-get install libmagic1
# If you're using iOS, you'll need to install libmagic
$ brew install libmagic

# Run the file
$ python metatube.py

# The server will initialize in the <http://localhost:5000>
```

You can set the following environment variables:
Name | Description | Default value
---|---|---
PORT|Set the port on which the MetaTube server will be available|5000
HOST|Set the address on which the MetaTube server will run | 127.0.0.1
DEBUG|Whether to enable debug mode or not | False
DATABASE_URL | The URL to your Database. Currently only SQLite3 is supported. | sqlite:///app.db
FFMPEG | An absolute path to the folder containing ffmpeg. | Empty
DOWNLOADS | An absolute path to the default download folder | /absolute/path/to/MetaTube/downloads; absolute path will be calculated automatically
LOG | Whether to keep logs or not | False
SOCKET_LOG | Whether to log in- and outcoming websocket connections; warning: your console can be spammed with connections | False
LOG_LEVEL | Numeric value from which MetaTube will keep logs. Info [here](https://docs.python.org/3/howto/logging.html#logging-levels) | 10
URL_SUBPATH | Set the URL subpath, if you want to run MetaTube on a subpath. Example: `/metatube` will run the server on `host:port/metatube` | /

```bash
# On Windows 10, you can set an environment variable like this: 
$ set ENVIRONMENT_VARIABLE = Value

# On Linux and MacOS, you can set an environment variable like this:
$ export ENVIRONMENT_VARIABLE = Value
```

Additionally you can create a file called `.flaskenv` and set the environment variables in there.
An example is provided in [example.flaskenv](example.flaskenv). You can use that template and rename the file to `.flaskenv`.

## Fix the artist values

So I recently discovered I made a mistake in the process of adding artists to files. <br/>
Some songs have tags multiple artists, and I noticed these tags were misinterpreted by my audio player. <br/>
Basically, the `TPE1` tag contained was like this: `['artist 1; artist 2']`, while it should've been `['artist 1', 'artist 2']`. <br/>
Thanks to [#310](https://github.com/quodlibet/mutagen/issues/310) I discovered this, corrected it in `metadata.py` and wrote a small script in [fixartists.py](fixartists.py) to fix the existing audio files that had the tags in the wrong way. <br/>
Put all the wrong audio files in one directory, run the file and enter the path to the directory containing the incorrect tags, and it should be fixed. <br/>
My apologies for this (annoying) bug.

## :memo: License ##

This project is under license from GNUv3. For more details, see the [LICENSE](LICENSE) file.<br/>
I am not responsible for any legal consequences the user may or may not face by using this project.

Made with :heart: by <a href="https://github.com/JVT038" target="_blank">JVT038</a>

## To-Do

### Finished

- [X] Add support for the use of proxies to download YouTube videos
- [X] Add Docker support
- [X] Add Docker support for ARM64/v8 devices (such as Raspberry Pi 4)
- [X] Add Github action / workflow thing, to automatically create Docker image upon a new commit
- [X] Add support for Spotify as a metadata provider
- [X] Add support for Deezer as a metadata provider
- [X] Add support for Genius as a metadata provider
- [X] Add support for subpath (such as `localhost:5000/metatube`)
- [X] Add a nice progress bar
- [X] Add a function to allow users to download the song onto their device
- [X] Add button in settings to download all the downloaded content
- [X] Add ability to manually set video width & height, if a video type has been selected
- [X] Add ability to manually set video width & height, if a video type has been selected, AFTER the item has been inserted into the database
- [X] Preview filenames when entering an output template
- [X] Make the Docker file smaller, because it's huge
- [X] Build a logger
- [X] Catch and show errors properly
- [X] Support looking for YouTube videos and downloading them
- [X] Store the information of downloaded songs in a SQL database
- [X] Make it mobile-friendly
- [X] Use Sponsorblock and yt-dlp to automatically skip fragments
- [X] Manually edit metadata of file, before the download
- [X] Manually edit metadata of file, after the download
- [X] Select output type (coding, extension, etc.)
- [X] Switch from AJAX to websockets
- [X] Hardware transcoding with NVENC, Intel Quick Sync, Video Acceleration API (VAAPI) & AMD AMF
- [X] Improve the automatic creation of the database, the tables and the default rows, because it's horrible right now.
- [X] Use multiprocessing and websockets to make the overview page faster
- [X] Dark mode support
- [X] Fix error `Synchronous XMLHttpRequest on the main thread is deprecated because of its detrimental effects to the end user’s experience. For more help http://xhr.spec.whatwg.org/` in overview
- [X] Make sure the search for downloaded song field works

### Not finished (I'll never finish this)

- [ ] Add it to the PyPi library
- [ ] Add support for sites other than YouTube
- [ ] Add support for YouTube playlists
- [ ] Add custom YouTube-DLP options
- [ ] Add support for H.265 / HEVC
- [ ] Add authentication system with an optional reverse proxy
- [ ] Add support for TheAudioDB
- [ ] Add support for YouTube Music
- [ ] Add support for Last.fm!
- [ ] Add support for embedded lyrics (if possible)
- [ ] Add translations
- [ ] Add in-built file explorer, making manual paths optional
- [ ] Add some nice animations
- [ ] Add a cancel download button when the video is being downloaded
- [ ] Add button in settings to download the entire SQlite3 Database
- [ ] Add support for HTTPS / SSL
- [ ] Give the user the option which level of logs to show / log and whether to save the logs to a file
- [ ] Support querying the Musicbrainz database and matching YouTube videos with them
- [ ] Support MySQL
- [ ] Make a CLI to download and match music
- [ ] Have a proper versioning system, because it's impossible to keep track of versions rn
- [ ] Cache and store the segments and other video data, so next time of loading a video will be faster
- [ ] Send websocket requests to one specific device / client only, to prevent duplicate websocket requests
- [ ] Make sure the progress bar works properly in a Docker container, because it doesn't work properly rn.
- [ ] Use proper queues and threading during download instead of the weird ping-pong system between the client and the server.
&#xa0;

## Disclaimer

I made this project to educate myself about Python, and to learn how metadata works in combination with files.
Additionally, I want to emphasize I do NOT encourage any pirating, or any other illegal activities.
This project's purpose isn't to illegally download content from YouTube; its purpose is to educate and enlighten myself (and others viewing the source code) about Python, how Python interacts with metadata in files, and  metadata works, and how yt-dlp works.
I am not responsible if the user downloads illegal content, or faces any (legal) consequences.

<a href="#top">Back to top</a>
