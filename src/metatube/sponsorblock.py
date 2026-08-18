import sponsorblock
from sponsorblock.errors import *

from metatube import logger


def segments(url):
    # return "404"
    client = sponsorblock.Client()
    logger.info("Fetching sponsorblock segments for %s", url)
    try:
        segments = client.get_skip_segments(url)
    except NotFoundException:
        logger.warn("No segments found for %s", str(url))
        return "404"
    except Exception as e:
        logger.error("Error in metatube/sponsorblock.py: %s", str(e))
        return str(e)

    response = []
    for segment in segments:
        response.append(segment.data)
    return response
