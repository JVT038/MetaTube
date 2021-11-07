import sponsorblock, json
def segments(url):
    client = sponsorblock.Client()
    segments = client.get_skip_segments(url)
    response = []
    for segment in segments:
        response.append(json.dumps(segment.data))
    return response