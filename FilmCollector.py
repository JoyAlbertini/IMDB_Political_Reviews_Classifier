# Joy Albertini
import asyncio
import json

from IMDB_Extended import IMDB_Extended
import os
import aiofiles
import pandas as pd


class Film_collector:
    def __init__(self):
        if not os.path.exists("Data"):
            os.makedirs("Data")

    async def get_film_data(self, id_imdb, directory, force_update, verbose=True):
        film_path = f'{directory}/{id_imdb}_film.json'
        if os.path.exists(film_path) and not force_update:
            if verbose:
                print("Retrieving film data from local storage")
            async with aiofiles.open(film_path, 'r') as file:
                film_data = await file.read()
            return film_data
        else:
            if verbose:
                print("Fetching film data from IMDB")
            film_data = IMDB_Extended(show_chrome=False).get_by_id(id_imdb)
            film_data = json.loads(film_data)

            film_data['political_m'] = False

            film_data = json.dumps(film_data)

            async with aiofiles.open(film_path, 'w') as file:
                await file.write(film_data)
            return film_data

    async def get_film_reviews(self, id_imdb, directory, force_update, verbose=True):
        review_path = f'{directory}/{id_imdb}_review.csv'
        if os.path.exists(review_path) and not force_update:
            return pd.read_csv(review_path)
        else:
            if verbose:
                print("Fetching reviews from IMDB")
            reviews = IMDB_Extended(show_chrome=False).fetch_reviews(id_imdb, verbose=verbose)
            reviews_df = self.convert_to_df_reviews(reviews)
            reviews_df.to_csv(review_path, index=False)
            return reviews_df

    def convert_to_df_reviews(self, reviews):
        reviews_df = pd.DataFrame(reviews)
        reviews_df.drop("reviewer_name", axis=1, inplace=True)
        if not reviews_df['rating'].empty:
            reviews_df['rating'] = reviews_df['rating'].apply(
                lambda x: int(x.split('/')[0]) if pd.notnull(x) and '/' in x else None)
        return reviews_df

    async def get_all(self, id_imdb, force_update=False, verbose=True):
        if id_imdb is None:
            return
        directory = f'Data/{id_imdb}'
        if not os.path.exists(directory):
            os.makedirs(directory)

        film_data_json = await self.get_film_data(id_imdb, directory, force_update, verbose)
        film_reviews = await self.get_film_reviews(id_imdb, directory, force_update, verbose)

        return film_data_json, film_reviews

    async def get_film(self, id_imdb, force_update=False):
        if id_imdb is None:
            return
        directory = f'Data/{id_imdb}'
        if not os.path.exists(directory):
            os.makedirs(directory)

        film_data_json = await self.get_film_data(id_imdb, directory, force_update)

        return film_data_json

    async def get_reviews(self, id_imdb, force_update=False):
        if id_imdb is None:
            return
        directory = f'Data/{id_imdb}'
        if not os.path.exists(directory):
            os.makedirs(directory)

        film_reviews_df = await self.get_film_reviews(id_imdb, directory, force_update)
        return film_reviews_df


if __name__ == "__main__":
    collector = Film_collector()
    result = asyncio.run(collector.get_all('tt6133466', True))
