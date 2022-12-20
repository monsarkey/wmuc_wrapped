from scraper_api import ScraperAPIClient
from bs4 import BeautifulSoup

import pandas as pd
import sys
import csv
import os
import re


def scrape_genres():
    client = ScraperAPIClient('fee679c640f3210ac9fa227d0539f00d')

    f = open('genre_LUT.csv', 'a', newline='')
    writer = csv.writer(f)

    if os.stat("genre_LUT.csv").st_size == 0:
        header = ['artist', 'genres']
        writer.writerow(header)

    current_idx = len(pd.read_csv('genre_LUT.csv', encoding='unicode_escape'))

    artists = pd.read_csv('artist_list.csv')['artist'].values

    while current_idx < len(artists):
        artist = artists[current_idx]
        print(artist)

        # remove spaces
        artist_q = re.sub(r" ", "%20", artist)
        query = f"https://rateyourmusic.com/search?searchterm={artist_q}&searchtype=artist"

        result = client.get(url=query).text
        soup = BeautifulSoup(result, 'html.parser')

        first_tr = soup.select_one("tr:nth-of-type(1)")

        if first_tr is not None:
            artist_field = first_tr.select_one('td:nth-of-type(2)')

            if artist_field is not None:
                genres = artist_field.findChildren("a", attrs={"class": "smallgreen"})
                genres = '/'.join([x.find(text=True, recursive=False) for x in genres])
            else:
                genres = "None"
        else:
            genres = "None"

        row = [artist, genres]

        try:
            writer.writerow(row)
        except UnicodeEncodeError:
            genres = genres.encode('ascii', 'ignore')
            artist = artist.encode('ascii', 'ignore')
            row = [artist, genres]
            writer.writerow(row)
        except:
            print(f"{genres} cannot be written for {artist}")
            row[1] = "None"
            writer.writerow(row)

        current_idx += 1


def fix_artists():

    reference = pd.read_csv("artist_list.csv", dtype='str', encoding='utf-8')
    genre_lut = pd.read_csv("genre_LUT.csv", dtype='str', encoding='utf-8')

    genre_lut['artist'] = reference['artist']

    genres = genre_lut['genres']
    genres = genres.fillna(value="Not Found")

    for idx, genre in genres.items():
        genre = genre.lstrip("b'")
        genre = genre.rstrip("'")

        if genre is None or genre == "None" or genre == "":
            genre = "Not Found"

        genres[idx] = genre

    genre_lut['genres'] = genres
    genre_lut.to_csv("genre_LUT_final.csv", index=False, encoding='utf-8')


if __name__ == "__main__":

    # scrape_genres()
    fix_artists()

