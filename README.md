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
	🚧  MetaTube 🚀 Under construction...  🚧 <br/>
</h4>
<p>
  It's definitely not finished yet and these features are currently supported:

  - Fetch information from a YouTube video based on an URL
  - Query and fetch results from the Musicbrainz API
  - Set up templates and options for the YouTube download
  - Download YouTube videos based on a selected template
  - Exclude fragments (such as intros, outros, etc.) from the download

  To-Do before the first release:

  - Automatically merge metadata from Musicbrainz with the downloaded file
  - Store the information about downloaded releases in the database
  - Some decent mobile support
  - Docker support
</p>

<hr>

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/JVT038" target="_blank">Author</a>
</p>

<br>

## :dart: About ##

I made this project to download videos from YouTube easier, by automatically fetching music metadata from MusicBrainz Picard. 

## :sparkles: Features ##

:heavy_check_mark: Automatically download YouTube videos <br/>
:heavy_check_mark: Add metadata from the Musicbrainz Picard database <br/>
:heavy_check_mark: Set start and end point to cut off any outros  and/or intros

## :rocket: Technologies ##

The following tools were used in this project:

- [Python](https://python.org/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [JavaScript](https://www.javascript.com/)
- [Python Musicbrainz](https://python-musicbrainzngs.readthedocs.io)
- [Bootstrap 4.6](https://getbootstrap.com/docs/4.6)
- [jQuery 3.6.0](https://jquery.com/)
- [Friconix](https://friconix.com/)
- [Youtube-DLP](https://github.com/yt-dlp/yt-dlp)
- [Sponsorblock.py](https://github.com/wasi-master/sponsorblock.py)
- [FFmpeg 4.4.1](https://ffmpeg.org/)

## :white_check_mark: Requirements ##

Before starting :checkered_flag:, you need to have [Git](https://git-scm.com) and [Python](https://python.org) installed.

## :checkered_flag: Starting ##
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

# Before running the server, make sure to enter your environment variables in example.flaskenv and rename example.flaskenv to .flaskenv, so remove 'example'.

# Run the project
$ py metatube.py

# The server will initialize in the <http://localhost:3000>
```

## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE) file.<br/>
I am not responsible for any legal consequences the user may or may not face by using this project.


Made with :heart: by <a href="https://github.com/JVT038" target="_blank">JVT038</a>

## To-Do

- [ ] Catch and show errors properly
- [ ] Support looking for YouTube videos and downloading them
- [ ] Support querying the Musicbrainz database and matching YouTube videos with them
- [ ] Make a CLI to download and match music
- [ ] Store the information of downloaded songs in a SQL database
- [ ] Add support for the use of proxies to download YouTube videos
- [ ] Make it mobile-friendly
- [ ] Add Docker support
- [ ] Add it to the PyPi library
- [ ] Add support for other sites than YouTube
- [ ] Add support for YouTube playlists
- [X] Use Sponsorblock and ffmpeg-python to automatically skip intro and outro
- [ ] Build a logger
- [ ] Change metadata of file
- [X] Select output type (coding, extension, etc.)
- [ ] Add custom YouTube-DLP options
- [ ] Add authentication system with an optional reverse proxy
- [ ] Add support for TheAudioDB
- [ ] Add translations
- [ ] Add in-built file explorer, making paths optional
- [ ] Switch from AJAX to websockets
- [ ] Hardware acceleration with FFmpeg
- [ ] Improve the automatic creation of the database, the tables and the default rows, because it's horrible right now.
&#xa0;

<a href="#top">Back to top</a>