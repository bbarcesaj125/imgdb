from pathlib import Path
import pandas as pd
# import csv
# import time


tsv_title_basics = Path('./imdb_datasets/title.basics.tsv')
tsv_title_ratings = Path('./imdb_datasets/title.ratings.tsv')
tsv_title_basics_ratings = Path('./imdb_datasets/title_basics_ratings.tsv')

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


def imdb_get_rating(criteria={}):

    argument_list = criteria

    dtypes = {"tconst": str, "titeType": str, "primaryTitle": str, "originalTitle": str,
              "isAdult": str, "startYear": str, "endYear": str, "runtimeMinutes": str, "genres": str, "averageRating": float, "numVotes": int}

    for chunk in pd.read_csv(tsv_title_basics_ratings, sep="\t", chunksize=100000, dtype=dtypes, header=0):

        # print(chunk["primaryTitle"] == "Die Welt von Maurice Chevalier")
        # chunk_pd = pd.read_csv(chunk, sep="\t", header=0)

        # for index, row in chunk.iterrows():
        #     # print(row["startYear"])
        #     if row["primaryTitle"] == "The Expanse":2001
        #         print(row["startYear"])

        res = chunk.loc[(chunk["primaryTitle"] == argument_list["movie_title"])
                        & (chunk["titleType"] == argument_list["media_type"]) & (chunk["startYear"] == argument_list["movie_year"]), argument_list["column"]]

        if not res.empty:
            imdb_movie_rating = res.values[0]
            print("The Imdb movie rating is: ", imdb_movie_rating)
            print(
                f"Loading {res.values[0]} from function ended!")
            return imdb_movie_rating


""" for row in chunk["primaryTitle"]:
    print(chunk["startYear"])
    if row == "House":
        print(f"Hooraaaaay!!! {row}") """
# chunk = pd.read_csv(tsv_title_basics, chunksize=10000)
# end = time.time()
# print("Read csv with chunks: ", (end-start), "sec")


if __name__ == "__main__":
    imdb_search_criteria = {
        "movie_title": "Joker",
        "media_type": "movie",
        "movie_year": "2019",
        "column": "averageRating"
    }
    print(imdb_get_rating(imdb_search_criteria))

# try:
#     sqlite_connection = sqlite3.connect('./imdb_title_basics.db')
#     cursor = sqlite_connection.cursor()
#     print("Database was created successfully!")
#     db_file = Path('./imdb_title_basics.db')
#     tsv_file = Path('./imdb_datasets/title.basics.tsv')

#     print(db_file)
#     print(tsv_file)
#     """result = subprocess.run(['sqlite3',
#                              str(db_file),
#                              '-cmd',
#                              '.mode tsv',
#                              '.import --skip 1 ' +
#                              str(tsv_file)
#                              + ' title_basics'],
#                             capture_output=True) """

#     sqlite_select_query = "SELECT * FROM title_basics LIMIT 6"
#     cursor.execute(sqlite_select_query)
#     record = cursor.fetchall()
#     cursor.close()

# except sqlite3.Error as error:
#     print("Error while connecting to sqlite", error)
# finally:
#     if sqlite_connection:
#         sqlite_connection.close()
#         print("The SQLite connection is closed.")
