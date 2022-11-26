import pandas as pd
import requests
import json
import time
import urllib.parse

from spotipy.oauth2 import SpotifyOAuth
from secrets import *

scope = ""
search_url = "https://api.spotify.com/v1/search?"

percent_encoding = {
    " ": "%20",
    "!": "%21",
    "#": "%23",
    "$": "%24",
    "%": "%25",
    "&": "%26",
    "'": "%27",
    "(": "%28"
}


class Show:

    def __init__(self, data: pd.DataFrame):

        self.token = None

        self.title = data['show_title'].mode()[0]
        self.dj_name = data['dj_name'].mode()[0]
        self.dj_id = data['dj_id'].mode()[0]
        self.channel = data['channel'].mode()[0]
        self.df = data.drop(columns=['show_title', 'dj_id', 'dj_name', 'channel'])

    def _get_token(self) -> str:
        auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, show_dialog=True,
                                    redirect_uri=redirect_uri, scope=None)
        return auth_manager.get_access_token(as_dict=False)

    def fill_spotify(self, include_stats: bool = True):

        if not self.token:
            self.token = self._get_token()

        i = 0
        ids = []
        song_names = self.df['song'].values
        artist_names = self.df['artist'].values

        while i < len(song_names):

            track = song_names[i]
            artist = artist_names[i]
            q_type = "track"

            import re

            # remove special characters from track
            track = re.sub(r"[]", "", track)
            artist = re.sub(r"[]", "", artist)

            q = f"track:{track}%20artist:{artist}"

            query = f'{search_url}q={q}&type={q_type}&limit=1'
            response = requests.get(query, headers={"Content-Type": "application/json",
                                                    "Authorization": "Bearer " + self.token})

            if response.status_code == 200:  # continue as normal
                json_response = response.json()
                if len(json_response['tracks']['items']) != 0:
                    ids.append(json_response['tracks']['items'][0]['name'])
                else:
                    print(f"track #{i} ({track} by {artist}) not found.")
                    ids.append(ids[i - 1]) if len(ids) > 0 else ids.append(None)  # if not found, append previous entry
                i += 1
            elif response.status_code == 401:  # authentication failed, get new token
                self.token = self._get_token()
            elif response.status_code == 429:  # rate limited, wait and try again
                retry_time = response.headers["Retry-After"]
                print(f"hit rate limit, waiting {retry_time}s.")
                time.sleep(retry_time)
            else:  # some other error, just fill array with previous id
                print(f"error code {response.status_code} on track #{i} ({track} by {artist}).")
                ids.append(ids[i - 1]) if len(ids) > 0 else ids.append(None)
                i += 1

        # if our first entry wasn't found, then we replace it with the next one
        if ids[0] is None:
            ids[0] = ids[1]

        print(song_names)
        print(ids)

    def export(self):
        pass

    def __str__(self) -> str:
        return f"{self.title} on {self.channel}, presented by {self.dj_name}: {len(self.df)} total spins."
