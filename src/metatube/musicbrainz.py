# from flask import Request
import musicbrainzngs
from musicbrainzngs.musicbrainz import NetworkError, ResponseError

from metatube import logger, sockets

musicbrainzngs.set_useragent("metatube", "0.1", "https://github.com/JVT038/MetaTube")


def search(args):
    title = args["title"]
    artist = args["artist"]
    max = int(args["max"])
    response = musicbrainzngs.search_releases(title, artistname=artist, limit=max)
    response["query"] = title
    logger.info("Searching for %s, with artist %s", title, artist)
    return response


def search_id_release(id):
    fields = [
        "artists",
        "release-groups",
        "recordings",
        "isrcs",
        "tags",
        "media",
        "artist-rels",
        "labels",
        "label-rels",
        "work-level-rels",
        "work-rels",
    ]
    try:
        response = musicbrainzngs.get_release_by_id(id, includes=fields)
        return response
    except Exception as e:
        return str(e)


def search_id_recording(query):
    response = musicbrainzngs.search_recordings(query)
    return response


def search_id_release_group(id):
    try:
        release_group = musicbrainzngs.search_release_groups(rgid=id)
        release_cover = musicbrainzngs.get_release_group_image_list(id)
        response = {"release_group": release_group, "release_cover": release_cover}
        return response
    except Exception as e:
        return str(e)


def get_cover(releaseid):
    logger.info("Searching for cover of release %s", releaseid)
    try:
        return musicbrainzngs.get_image_list(releaseid)
    except ResponseError as e:
        logger.error(str(e))
        return str(e.message)
    except NetworkError as e:
        logger.error("Musicbrainz network exception: %s", str(e))
        return "error"
    except Exception as e:
        logger.error(str(e))
        return "error"


def webui(args):
    releases = search(args)
    if len(releases["release-list"]) > 0:
        for release in releases["release-list"]:
            release["cover"] = get_cover(release["id"])
        sockets.musicbrainzresults(releases["release-list"])
        logger.info("Sent musicbrainz release")
    else:
        sockets.searchvideo("No releases from Musicbrainz have been found!")
