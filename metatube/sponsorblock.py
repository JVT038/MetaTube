import sponsorblock
from sponsorblock.errors import *
def segments(url):
    print(url)
    client = sponsorblock.Client()
    try:
        segments = client.get_skip_segments(url)
        response = []
        for segment in segments:
            response.append(segment.data)
        return response
    except Exception as e:
        return str(e)