import pandas as pd
import numpy as np

from show import Show

if __name__ == "__main__":

    # placeholder
    csv = "spin_data/spins_8mo_11-17-22.csv" 

    # reading in csv, changing column headers
    df = pd.read_csv(csv, header=0, names=['date', 'show_title', 'dj_id', 'dj_name', 'date2', 'artist', 'song', \
                                            'album', 'duration', 'isrc', 'release_date'])

    # dropping extra column
    df = df.drop(columns=["date2"])

    # we split FM and DIG channels off from show titles
    titles = df.show_title

    channel = titles.apply(lambda x: x.split(':')[0])
    titles = titles.apply(lambda x: x.split(':')[1] if len(x.split(':')) > 1 else x.split(':')[0])

    df['show_title'] = titles
    df['channel'] = channel

    # filter out channels that are not DIG or FM
    valid_DIG = (df['channel'] == 'DIG').values
    valid_FM = (df['channel'] == 'FM').values

    valid_channels = np.logical_or(valid_DIG, valid_FM)
    
    # filter and re-index
    df = df[valid_channels]
    df = df.reset_index()
    df = df.drop(columns=['index'])

    print(df)
