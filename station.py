from __future__ import annotations

import pandas as pd
from show import Show


class Station:

    def __init__(self, shows: [Show], df: pd.DataFrame = None, title: str = "WMUC FM - College Park"):

        self.required_features = ['danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness',
                                  'valence', 'tempo', 'duration_ms', 'time_signature']

        self.title = title
        self.shows = shows
        self.num_shows = len(shows)

        show_dfs = [x.df for x in shows]
        self.total_df = pd.concat(show_dfs).reset_index().drop(columns='index')
        self.num_songs = len(self.total_df)

        self.df = self.construct_df() if df is None else df

    def construct_df(self) -> pd.DataFrame:

        show_details = [{"title": show.title, "dj_name": show.dj_name, "dj_id": show.dj_id, "spins": show.spin_count}
                        for show in self.shows]

        df = pd.DataFrame(show_details, columns=["title", "dj_name", "dj_id", "spins"])

        show_stats = [show.get_stats() for show in self.shows]
        show_stats = pd.DataFrame(show_stats, columns=["avg_" + x for x in self.required_features])

        show_genres = [show.get_genres() for show in self.shows]
        show_genres = pd.DataFrame(show_genres, columns=["genre_1", 'genre_2', "genre_3"])

        df = pd.concat([df, show_stats, show_genres], axis=1)
        return df

    def to_csv(self, filepath: str = None):
        if filepath:
            self.df.to_csv(filepath)
        else:
            self.df.to_csv(f"station_out/{self.title.replace(' ', '_').replace('/', '_').replace('?', '_')}.csv")

    def __str__(self):
        return f"{self.title}, featuring {self.num_shows} shows and {self.num_songs} total spins."
