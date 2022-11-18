import pandas as pd

from spotipy.oauth2 import SpotifyOAuth
from secrets import *

scope = ""

class Show:

    def __init__(self, data: pd.DataFrame):

        self.token = None

        self.title = data['show_title'].mode()[0]
        self.dj_name = data['dj_name'].mode()[0]
        self.dj_id = data['dj_id'].mode()[0]
        self.channel = data['channel'].mode()[0]
        self.df = data.drop(columns=['show_title', 'dj_id', 'dj_name', 'channel'])


    def _get_token(self) -> str:
        auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, show_dialog=True, redirect_uri=redirect_uri, scope=None)
        return auth_manager.get_access_token(as_dict=False)


    def fill_spotify(self):
        
        if not self.token:
            self.token = self._get_token()

        print(self.token)


    def export(self):
        pass

    def __str__(self) -> str:
        return f"{self.title} on {self.channel}, presented by {self.dj_name}: {len(self.df)} total spins."
