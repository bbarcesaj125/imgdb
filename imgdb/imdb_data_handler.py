from pathlib import Path
import pandas as pd
from utils import *
import logging

base_path = Path(__file__).parent
tsv_title_basics = (base_path / "../imdb_datasets/title.basics.tsv").resolve()
tsv_title_ratings = (
    base_path / "../imdb_datasets/title.ratings.tsv").resolve()
tsv_title_basics_ratings = (
    base_path / "../imdb_datasets/title_basics_ratings.tsv").resolve()


# title_ratings_pd = pd.read_csv(tsv_title_ratings, sep="\t", header=0, dtype={"tconst": str, "averageRating": float, "numVotes": int})

# start = time.time()
# title_basics_pd = pd.read_csv(tsv_title_basics, sep="\t", header=0, dtype={"tconst": str, "titeType": str, "primaryTitle": str, "originalTitle": str, "isAdult": str, "startYear": str, "endYear": str, "runtimeMinutes": str, "genres": str})

# title_basics_ratings_pd=title_basics_pd.merge(title_ratings_pd, on="tconst")
# title_basics_ratings_pd.to_csv("./imdb_datasets/title_basics_ratings.tsv", sep = "\t", index = False)

# res = title_basics_ratings_pd.loc[(title_basics_ratings_pd["primaryTitle"] == "The Hangover")
#                                   & (title_basics_ratings_pd["titleType"] == "movie") & (title_basics_ratings_pd["startYear"] == "2009"), "averageRating"]
# if not res.empty:
#     print(res.values[0])


# end = time.time()
# print("Loading tsv ended: ", end - start)

# start1 = time.time()
# res = title_basics_pd.loc[(title_basics_pd["primaryTitle"] == "The Dark Side of the Moon")
#                           & (title_basics_pd["titleType"] == "movie") & (title_basics_pd["startYear"] == "2015"), "primaryTitle"]
# if not res.empty:
#     print(res.values[0])
# end1 = time.time()
# print(f"Loading {res.values[0]} ended: ", end1 - start1)

# start2 = time.time()
# res1 = title_basics_pd.loc[(title_basics_pd["primaryTitle"] == "The Ghost of Peter Sellers")
#                            & (title_basics_pd["titleType"] == "movie") & (title_basics_pd["startYear"] == "2018"), "primaryTitle"]

# if not res1.empty:
#     print(res1.values[0])
# end2 = time.time()
# print(f"Loading {res1.values[0]} ended: ", end2 - start2)


def imdb_get_data_from_datasets(criteria={}):
    """ This function takes in a dictionary containing movie data as input to output the corresponding Imdb's data.
    The input dictionary has the following structure:
        criteria = {
                        "movie_title": The title of the movie,
                        "media_type": (e.g., movie, tvSeries, etc.),
                        "movie_year": The release year of the movie
                    }
    """

    argument_list = criteria

    chunk_size = 100000
    dtypes = {"tconst": str, "titeType": str, "primaryTitle": str, "originalTitle": str,
              "isAdult": str, "startYear": str, "endYear": str, "runtimeMinutes": str, "genres": str, "averageRating": float, "numVotes": int}

    for chunk in pd.read_csv(tsv_title_basics_ratings, sep="\t", chunksize=chunk_size, dtype=dtypes, header=0):

        # print(chunk["primaryTitle"] == "Die Welt von Maurice Chevalier")
        # chunk_pd = pd.read_csv(chunk, sep="\t", header=0)

        # for index, row in chunk.iterrows():
        #     # print(row["startYear"])
        #     if row["primaryTitle"] == "The Expanse":2001
        #         print(row["startYear"])

        res = chunk.loc[(chunk["primaryTitle"] == argument_list["movie_title"])
                        & (chunk["titleType"] == argument_list["media_type"]) & (chunk["startYear"] == argument_list["movie_year"])]

        if not res.empty:
            imdb_movie_raw_data = res.values[0]
            imdb_movie_data = {
                "tconst": imdb_movie_raw_data[0],
                "titleType": imdb_movie_raw_data[1],
                "primaryTitle": imdb_movie_raw_data[2],
                "originalTitle": imdb_movie_raw_data[3],
                "isAdult": imdb_movie_raw_data[4],
                "startYear": imdb_movie_raw_data[5],
                "endYear": imdb_movie_raw_data[6],
                "runtimeMinutes": imdb_movie_raw_data[7],
                "genres": imdb_movie_raw_data[8],
                "averageRating": imdb_movie_raw_data[9],
                "numVotes": imdb_movie_raw_data[10]
            }

            print("The Imdb movie rating is: ",
                  imdb_movie_data["averageRating"])
            logging.debug("The Imdb movie rating is: %s" %
                          imdb_movie_data["averageRating"])
            print(
                f"Retrieved this: {res.values[0]} from Imdb datasets!")
            logging.info(
                "The results were successfully retrieved from the datasets.")
            return imdb_movie_data


if __name__ == "__main__":
    imdb_search_criteria = {
        "movie_title": "Rams",
        "media_type": "movie",
        "movie_year": "2015"
    }
    print(imdb_get_data_from_datasets(imdb_search_criteria))
