#################################
#####How to use this script:#####
#1. python fixartists.py#########
#2. Enter directory in CLI#######
#3. Let it run###################
#################################
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
import os
directory = input('Enter relative or absolute path to audio files: ')
files = os.listdir(directory)
for file in files:
    extensions = ['MP3', 'OPUS', 'FLAC', 'OGG']
    filepath = os.path.join(directory, file)
    extension = filepath.split('.')[len(filepath.split('.')) - 1].upper()
    if os.path.isfile(filepath):
        if extension.upper() in extensions:
            if extension == 'MP3':
                audio = EasyID3(filepath)
            elif extension == 'OPUS':
                audio = OggOpus(filepath)
            elif extension == 'FLAC':
                audio = FLAC(filepath)
            elif extension == 'OGG':
                audio = OggVorbis(filepath)
            if 'artist' in audio:
                old_artists = audio["artist"]
                if len(old_artists) == 1 and '; ' in old_artists[0]:
                    new_artists = old_artists[0].split('; ')
                    audio["artist"] = new_artists
                    audio.save()
                    print(f'Fixed artists of {file}')
                else:
                    print(f'{file} already has the correct artist format, skipping...')
            else:
                print(f'{file} contains no TPE1 tag, skipping')
        else:
            print(f'{file} has an unsupported extension, skipping')