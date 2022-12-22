import pandas as pd
import numpy as np

import os

from show import Show


def extract_artists():
    artists = df.groupby(['artist'])['song'].count().reset_index(name='Count') \
        .sort_values(['Count'], ascending=False).reset_index().drop(columns='index')
    artists.to_csv('genre_scraper/artist_list.csv')


if __name__ == "__main__":

    # placeholder
    csv = "spin_data/spins_8mo_12-09-22.csv"

    # reading in csv, changing column headers
    df = pd.read_csv(csv, header=0, names=['date', 'show_title', 'dj_id', 'dj_name', 'date2', 'artist', 'song', \
                                            'album', 'duration', 'isrc', 'release_date'])

    # dropping extra column
    df = df.drop(columns=["date2", "duration"])

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
    # df = df.reset_index()
    # df = df.drop(columns=['index'])

    # we make some manual edits to make sure 5 shows have their correct name
    df['show_title'] = df['show_title'].replace('the deep genre dive (piedmont blues)', 'the deep genre dive')
    df['show_title'] = df['show_title'].replace('Everything Reminds Me of Her- numbers', 'Everything Reminds Me of Her')
    df['show_title'] = df['show_title'].replace(' To the Top Floor <Ep. 1>', 'To the Top Floor')
    df['show_title'] = df['show_title'].replace('The Strip EP. 2', 'The Strip')
    df['show_title'] = df['show_title'].replace('The New Indie Canon 2022.11.22', 'The New Indie Canon')

    show_dfs = [x for _, x in df.groupby(by='dj_id')]

    for show in show_dfs:
        title = show['show_title'].mode()[0].strip()
        show['show_title'] = title

    df = pd.concat(show_dfs)
    show_dfs = [x for _, x in df.groupby(by='show_title')]

    shows = []

    show_dfs = [show_dfs[0]]

    for show in show_dfs:

        # we are only including shows with more than 20 spins
        if len(show) > 20:

            title = show['show_title'].mode()[0]
            show = show.reset_index()
            show = show.drop(columns=['index'])

            filepath = f"show_out/{title.replace(' ', '_')}.csv"

            if os.path.isfile(filepath):
                new_show = Show.from_csv(filepath)
                shows.append(new_show)
            else:
                new_show = Show(show)
                new_show.fill_spotify()
                new_show.to_csv(filepath)

                shows.append(new_show)

    pass




    # example_df = df[df['show_title'] == "insufferable art house cinema soundtrack"]
    # example_df = example_df.reset_index()
    # example_df = example_df.drop(columns=['index'])
    #
    # example_show = Show(example_df)
    # example_show.fill_spotify()
    #
    # example_show.to_csv()
    # test = Show.from_csv("show_out/test-show.csv")
    # pass
    # print(df)
