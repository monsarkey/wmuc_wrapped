from __future__ import annotations

import pandas as pd
from show import Show


class Station:

    def __init__(self, shows: [Show], df: pd.DataFrame = None, title: str = "WMUC FM - College Park"):
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

        pass

    def __str__(self):
        return f"{self.title}, featuring {self.num_shows} shows and {self.num_songs} total spins."
