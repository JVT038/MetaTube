import sponsorblock
from sponsorblock.errors import *
from metatube import logger
async def segments(url):
    client = sponsorblock.Client()
    logger.info('Fetching sponsorblock segments for %s', url)
    try:
        segments = client.get_skip_segments(url)    
    except Exception as e:
        logger.error("Error in metatube/sponsorblock.py: " + str(e))
        return str(e)
    
    response = []
    for segment in segments:
        response.append(segment.data)
    return response