from pathlib import Path
import pandas as pd
import logging
import click

base_path = Path(__file__).parent
tsv_title_basics_ratings = (
    base_path / "../imdb_datasets/title_basics_ratings.tsv").resolve()


def merge_tsv_files(tsv_title_basics, tsv_title_ratings, base_path):
    """ This function merges two tsv files. """

    title_basics_ratings_file_path = (
        base_path / "title_basics_ratings.tsv").resolve()
    try:
        title_basics_pd = pd.read_csv(tsv_title_basics, sep="\t", header=0, dtype={
            "tconst": str, "titeType": str, "primaryTitle": str, "originalTitle": str, "isAdult": str, "startYear": str, "endYear": str, "runtimeMinutes": str, "genres": str})
        title_ratings_pd = pd.read_csv(tsv_title_ratings, sep="\t", header=0, dtype={
            "tconst": str, "averageRating": float, "numVotes": int})
    except Exception as e:
        logging.critical("We couldn't read the tsv files!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.fail +
                   "We couldn't read the tsv files!" + Tcolors.endc)

    # Merging the two tsv files
    try:
        title_basics_ratings_pd = title_basics_pd.merge(
            title_ratings_pd, on="tconst")
    except Exception as e:
        logging.critical("We failed to merge the tsv files!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.fail +
                   "We failed to merge the tsv files!" + Tcolors.endc)

    # Saving the merged file on disk
    try:
        title_basics_ratings_pd.to_csv(
            title_basics_ratings_file_path, sep="\t", index=False)
    except Exception as e:
        logging.critical("We failed to write the merged tsv file!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.fail +
                   "We failed to write the merged tsv file!" + Tcolors.endc)


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
                "genres": imdb_movie_raw_data[8].split(","),
                "averageRating": imdb_movie_raw_data[9],
                "numVotes": imdb_movie_raw_data[10]
            }

            logging.debug("Imdb movie data: %s" % imdb_movie_data)
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
    base_path = Path("./imdb_datasets/").resolve()

    merge_tsv_files("/home/yusarch/Documents/Programming/Python/rt_movie_cover/imdb_datasets/title.basics.tsv",
                    "/home/yusarch/Documents/Programming/Python/rt_movie_cover/imdb_datasets/title.ratings.tsv", base_path)
