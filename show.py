import pandas as pd


class Show:

    def __init__(self):
        self.data = None

    def load_df(self, data: pd.DataFrame):
        self.data = data

    def export(self):
        pass
