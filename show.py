from __future__ import annotations

import os.path

import pandas as pd
import requests
import json
import time
import urllib.parse

from spotipy.oauth2 import SpotifyOAuth
from secrets import *

scope = ""
search_url = "https://api.spotify.com/v1/search?"
audio_features_url = "https://api.spotify.com/v1/audio-features?"

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

    def __init__(self, data: pd.DataFrame, fill_data: bool = False):

        self.token = None

        self.title = data['show_title'].mode()[0]
        self.dj_name = data['dj_name'].mode()[0] if not data['dj_name'].mode().empty else ""
        self.dj_id = data['dj_id'].mode()[0] if not data['dj_id'].mode().empty else ""
        self.channel = data['channel'].mode()[0]

        self.spin_count = len(data)
        self.df = data

        if fill_data:
            self.fill_spotify()
            self.get_genres()

    @staticmethod
    def _get_token() -> str:
        auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, show_dialog=True,
                                    redirect_uri=redirect_uri, scope=None)
        return auth_manager.get_access_token(as_dict=False)

    @staticmethod
    def from_csv(filename: str) -> Show:

        if not filename:
            raise Exception("csv File name cannot be None")

        if not os.path.isfile(filename):
            raise Exception(f"file \"{filename}\" not found locally")

        df = pd.read_csv(filename)

        return Show(df)

    def fill_spotify(self, include_stats: bool = True):

        if not self.token:
            self.token = self._get_token()

        i = 0
        ids = []
        song_names = self.df['song'].values
        artist_names = self.df['artist'].values

        num_tracks = len(song_names)

        while i < num_tracks:

            track = song_names[i]
            artist = artist_names[i]
            q_type = "track"

            #TODO: remove special characters from track

            # import re

            # track = re.sub(r"[]", "", track)
            # artist = re.sub(r"[]", "", artist)

            q = f"track:{track}%20artist:{artist}"

            query = f'{search_url}q={q}&type={q_type}&limit=1'
            response = requests.get(query, headers={"Content-Type": "application/json",
                                                    "Authorization": "Bearer " + self.token})

            if response.status_code == 200:  # continue as normal
                json_response = response.json()
                if len(json_response['tracks']['items']) != 0:
                    ids.append(json_response['tracks']['items'][0]['id'])
                else:
                    # print(f"track #{i} ({track} by {artist}) not found.")
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
        # TODO: if the first two entries are null, this doesn't help. Maybe a while loop?
        # if ids[0] is None:
        #     ids[0] = ids[1]

        i = 0
        while i < len(ids) and ids[i] is None:
            i += 1

        for j in range(i):
            ids[j] = ids[i]

        self.df['id'] = ids

        # get audio features if required
        if include_stats:

            # change which audio features we're looking for here
            required_features = ['danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness',
                                 'valence', 'tempo', 'duration_ms', 'time_signature']

            # we can request track info in batches of 100
            num_requests = (num_tracks // 100) + 1

            dfs = []

            for i in range(num_requests):

                start_idx = i * 100

                if i == num_requests - 1:
                    id_str = '%2C'.join(ids[start_idx:(start_idx + num_tracks % 100)])
                else:
                    id_str = '%2C'.join(ids[start_idx:(start_idx + 100)])

                query = f'{audio_features_url}ids={id_str}'
                response = requests.get(query, headers={"Content-Type": "application/json",
                                                        "Authorization": "Bearer " + self.token})

                if response.status_code == 200:  # continue as normal
                    json_response = response.json()
                    audio_features = json_response['audio_features']
                    audio_features = [x if x is not None else audio_features[i - 1] for i, x in
                                      enumerate(audio_features)]
                    dfs.append(pd.DataFrame(audio_features))
                elif response.status_code == 401:  # authentication failed, get new token
                    self.token = self._get_token()
                elif response.status_code == 429:  # rate limited, wait and try again
                    retry_time = response.headers["Retry-After"]
                    print(f"hit rate limit, waiting {retry_time}s.")
                    time.sleep(float(retry_time))
                else:  # some other error, just fill array with previous id
                    print(f"error code {response.status_code} on request #{i}.")

            # join request DataFrames into one
            features_df = pd.concat(dfs).reset_index().drop(columns='index')
            features_df = features_df[required_features]

            self.df = pd.concat([self.df, features_df], axis=1)

    def get_genres(self):

        genre_LUT = pd.read_csv('genre_scraper/genre_LUT_final.csv', dtype='str', encoding='utf-8')
        genre_LUT = genre_LUT.to_dict(orient='split')
        genre_LUT = dict(genre_LUT['data'])

        def genres(artist):
            genre_split = genre_LUT[artist].split('/') if genre_LUT[artist] is not None else None

            if genre_split:
                return genre_split[0], \
                    genre_split[1] if len(genre_split) > 1 else "Not Found", \
                    genre_split[2] if len(genre_split) > 2 else "Not Found"
            else:
                return "Not Found", "Not Found", "Not Found"

        self.df['genre_1'], self.df['genre_2'], self.df['genre_3'] = zip(*self.df['artist'].map(genres))

    def to_csv(self, filepath: str = None):
        if filepath:
            self.df.to_csv(filepath)
        else:
            self.df.to_csv(f"show_out/{self.title.replace(' ', '_').replace('/', '_').replace('?', '_')}.csv")

    def __str__(self) -> str:
        return f"{self.title} on {self.channel}, presented by {self.dj_name}: {self.spin_count} total spins."
