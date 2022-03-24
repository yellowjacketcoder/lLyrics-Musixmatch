import json
import urllib.request
import urllib.parse


class Parser(object):

    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        self.API_KEY = '1a2244035bb2332c83f241548413509f'
        self.API_URL = 'https://api.musixmatch.com/ws/1.1/'

    def parse(self):
        # URL encode artist and title strings
        encoded_artist = urllib.parse.quote(self.artist)
        encoded_title = urllib.parse.quote(self.title)

        # Match & Fetch Track Details
        METHOD = 'matcher.track.get'
        query = '%s%s?apikey=%s' % (self.API_URL, METHOD, self.API_KEY)

        # Add artist or title to query URL
        if encoded_artist:
            query += '&q_artist=%s' % (encoded_artist)
        if encoded_title:
            query += '&q_track=%s' % (encoded_title)

        # Call the API
        try:
            resp = urllib.request.urlopen(query, None, 5)
        except:
            print("Cannot connect to Musixmatch\nQuery URL:%s" % (query))
            return ""

        # Stop if HTTP Response code is not 200
        if resp.status != 200:
            print("Error! Query URL:%s\nHTML Reponse Code:%s" % (query, resp.status))
            return ""

        # Parse JSON response
        resp = resp.read().decode('utf-8')
        resp = json.loads(resp)

        # Check API Response Status Code
        status_code = resp['message']['header']['status_code']
        if status_code != 200:
            print("Error %s: %s" % (status_code, self.get_error_details_from_status_code(status_code)))
            return ""

        # Fetch and log track details and confidence score from the API
        track_details = resp['message']['body']['track']
        confidence_score = resp['message']['header']['confidence']
        print("Musixmatch Identified Track(Confidence %s%%) Details:>> %s" % (confidence_score, track_details))

        # Find if lyrics are available or terminate if not available
        has_lyrics = resp['message']['body']['track']['has_lyrics']
        if has_lyrics == 0:
            print("Musixmatch does not have lyrics for this song")
            return ""

        # Fetch track ID for getting lyrics
        track_id = track_details['track_id']
        # Fetch and return lyrics
        self.lyrics = self.get_lyrics(track_id)

        return self.lyrics

    def get_lyrics(self, trackId):
        METHOD = 'track.lyrics.get'
        url = '%s%s?apikey=%s&track_id=%s' % (self.API_URL, METHOD, self.API_KEY, trackId)

        try:
            html = urllib.request.urlopen(url).read()
        except:
            print("Cannot connect to Musixmatch")
            return ""

        # Convert response to a string
        html = html.decode("utf-8")
        # Parse string to JSON
        response_json = json.loads(html)
        # Fetch lyrics from the response json
        lyrics = response_json['message']['body']['lyrics']['lyrics_body']

        return lyrics

    def get_error_details_from_status_code(self, statusCode):
        details = {
            200: "The request was successful.",
            400: "The request had bad syntax or was inherently impossible to be satisfied.",
            401: "Authentication failed, probably because of invalid/missing API key.",
            402: "The usage limit has been reached, either you exceeded per day requests limits or your balance is insufficient.",
            403: "You are not authorized to perform this operation.",
            404: "The requested resource was not found.",
            405: "The requested method was not found.",
            500: "Ops. Something were wrong.",
            503: "Our system is a bit busy at the moment and your request can't be satisfied."
        }
        # Return error details based on API's status code
        return details.get(statusCode, 'Some error occurred')
