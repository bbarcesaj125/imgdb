from pathlib import Path
import pandas as pd
import logging
import click
import datetime
from imgdb.utils import Tcolors, unzip, pickler
from imgdb.config import Config
from imgdb.imdb_poster_fetcher import imdb_download_poster
import re


def datasets_updater(freq):
    """This functions downloads Imdb's datasets and updates
    them according to a user-defined interval."""

    title_basics_url = "https://datasets.imdbws.com/title.basics.tsv.gz"
    title_ratings_url = "https://datasets.imdbws.com/title.ratings.tsv.gz"
    datasets_list = [title_basics_url, title_ratings_url]
    regex_tsv_title = r"(?<=com/)(.*?)(?=.gz)"
    tsv_time_saved = {}
    date_now = datetime.datetime.now()
    date_test = datetime.datetime(2021, 11, 24, 23, 59, 59)
    tsv_files = []
    tsv_save_pickle_path = Path(Config.IMDB_DATASETS_DIR / "tsv_save.pickle")
    regex_freq = r"(^[0-9]{1,}h|d)$"
    freq_test = re.search(regex_freq, freq)
    is_pickle = tsv_save_pickle_path.is_file()

    if is_pickle:
        saved_pickle = pickler(tsv_save_pickle_path)
        time_difference = (date_now - saved_pickle["time"]).total_seconds()
        logging.debug("Time difference is: %s" % time_difference)
        logging.debug("Content of pickle file: %s" % saved_pickle)

    update_freq = {"daily": 86400, "weekly": 604800, "bi-weekly": 1209600}

    count_freq = 0
    for key, value in update_freq.items():
        count_freq += 1
        if key == freq:
            threshold = update_freq[key]
            break
        elif freq_test:
            if freq[-1:] == "h":
                threshold = int(freq[:-1]) * 3600
            elif freq[-1:] == "d":
                threshold = int(freq[:-1]) * 86400
            break
        elif count_freq == len(update_freq):
            logging.warning(
                "The update frequency format is wrong." " Using 'weekly' as a fallback!"
            )
            click.echo(
                Tcolors().WARNING + "The update frequency format is wrong."
                " Using 'weekly' as a fallback!" + Tcolors.ENDC
            )
            threshold = update_freq["weekly"]
            logging.debug("Threshold inside loop is %s" % threshold)
        else:
            continue

    logging.debug("The threshold is %s" % threshold)

    count_url = 0
    for url in datasets_list:
        count_url += 1
        file_name_url_test = re.search(regex_tsv_title, url)
        if file_name_url_test:
            tsv_file_name = re.findall(regex_tsv_title, url)[0]
            tsv_gz_file_name = url.split("/")[-1]
            tsv_gz_file_path = Path(Config.IMDB_DATASETS_DIR / tsv_gz_file_name)
            tsv_file_path = Path(Config.IMDB_DATASETS_DIR / tsv_file_name)
            tsv_files.append(tsv_file_path)
            logging.debug("The filename of the tsv file is: %s" % tsv_file_name)
            is_file = tsv_file_path.is_file()

            if (not is_file or not is_pickle) or (
                is_pickle and time_difference > threshold
            ):
                download_msg = "Downloading" if not is_pickle else "Updating"
                logging.info("Downloading dataset file %s... yay :)" % tsv_gz_file_name)
                if count_url == 1:
                    click.echo(
                        Tcolors.OK_GREEN
                        + "%s IMDb datasets!" % download_msg
                        + Tcolors.ENDC
                    )
                # Downloading IMDb datasets
                imdb_download_poster(
                    url,
                    name=tsv_file_name,
                    filepath=tsv_gz_file_path,
                    download_or_update=download_msg,
                )

                click.echo(
                    Tcolors.OK_GREEN + "Unzipping: %s" % tsv_gz_file_name + Tcolors.ENDC
                )
                logging.info("Unzipping: %s" % tsv_gz_file_name)
                # Unzipping the datsets
                unzip(tsv_gz_file_path, tsv_file_path)

                if count_url == len(datasets_list):
                    tsv_time_saved["time"] = date_now
                    logging.debug("Time inside pickle file is: %s" % date_now)
                    pickler(tsv_save_pickle_path, tsv_time_saved)

                    logging.debug("The tsv list: %s" % tsv_files)
                    merge_tsv_files(
                        tsv_files[0], tsv_files[1], Config.IMDB_DATASETS_DIR
                    )
                    logging.debug("The tsv files were merged successfully!")


def merge_tsv_files(tsv_title_basics, tsv_title_ratings, base_path):
    """This function merges two tsv files."""

    title_basics_ratings_file_path = Path(base_path / "title_basics_ratings.tsv")
    try:
        title_basics_pd = pd.read_csv(
            tsv_title_basics,
            sep="\t",
            header=0,
            dtype={
                "tconst": str,
                "titeType": str,
                "primaryTitle": str,
                "originalTitle": str,
                "isAdult": str,
                "startYear": str,
                "endYear": str,
                "runtimeMinutes": str,
                "genres": str,
            },
        )
        title_ratings_pd = pd.read_csv(
            tsv_title_ratings,
            sep="\t",
            header=0,
            dtype={"tconst": str, "averageRating": float, "numVotes": int},
        )
    except Exception as e:
        logging.critical("We couldn't read the tsv files!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.FAIL + "We couldn't read the tsv files!" + Tcolors.ENDC)
        return 0

    # Merging the two tsv files
    click.echo(Tcolors.OK_GREEN + "Merging IMDb datasets!" + Tcolors.ENDC)
    logging.info("Merging IMDb datasets!")
    try:
        title_basics_ratings_pd = title_basics_pd.merge(title_ratings_pd, on="tconst")
    except Exception as e:
        logging.critical("We failed to merge the tsv files!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.FAIL + "We failed to merge the tsv files!" + Tcolors.ENDC)
        return 0
    else:
        click.echo(
            Tcolors.OK_GREEN + "Successfully merged IMDb datasets!" + Tcolors.ENDC
        )
        logging.info("Successfully merged IMDb datasets!")

    # Saving the merged file to disk
    click.echo(
        Tcolors.OK_GREEN + "Saving the merged dataset file to disk!" + Tcolors.ENDC
    )
    logging.info("Saving the merged dataset file to disk!")
    try:
        title_basics_ratings_pd.to_csv(
            title_basics_ratings_file_path, sep="\t", index=False
        )
    except Exception as e:
        logging.critical("We failed to write the merged tsv file!")
        logging.debug("Error: %s" % e)
        click.echo(
            Tcolors.FAIL + "We failed to write the merged tsv file!" + Tcolors.ENDC
        )
        return 0
    else:
        click.echo(
            Tcolors.OK_GREEN
            + "Merged dataset file saved as:\n <%s>" % title_basics_ratings_file_path
            + Tcolors.ENDC
        )
        logging.info(
            "Merged dataset file saved as: <%s>" % title_basics_ratings_file_path
        )


def imdb_get_data_from_datasets(criteria={}):
    """This function takes in a dictionary containing movie data
    as input to output the corresponding Imdb's data.

    The input dictionary has the following structure:
        criteria = {
                        "media_title": The title of the movie,
                        "media_pageconst": The ID of the title,
                        "media_type": (e.g., movie, tvSeries, etc.),
                        "media_year": The release year of the movie,
                    }
    """

    tsv_title_basics_ratings = Path(
        Config.IMDB_DATASETS_DIR / "title_basics_ratings.tsv"
    )

    argument_list = criteria

    chunk_size = 100000
    dtypes = {
        "tconst": str,
        "titeType": str,
        "primaryTitle": str,
        "originalTitle": str,
        "isAdult": str,
        "startYear": str,
        "endYear": str,
        "runtimeMinutes": str,
        "genres": str,
        "averageRating": float,
        "numVotes": int,
    }

    for chunk in pd.read_csv(
        tsv_title_basics_ratings, sep="\t", chunksize=chunk_size, dtype=dtypes, header=0
    ):

        if argument_list["media_pageconst"]:
            res = chunk.loc[
                (chunk["tconst"] == argument_list["media_pageconst"])
                & (chunk["titleType"] == argument_list["media_type"])
            ]
        else:
            res = chunk.loc[
                (chunk["primaryTitle"] == argument_list["media_title"])
                & (chunk["titleType"] == argument_list["media_type"])
                & (chunk["startYear"] == argument_list["media_year"])
            ]

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
                "numVotes": imdb_movie_raw_data[10],
            }

            logging.debug("Imdb movie data: %s" % imdb_movie_data)
            logging.info("The results were successfully retrieved from the datasets.")
            return imdb_movie_data


if __name__ == "__main__":
    imdb_search_criteria = {
        "movie_title": "Rams",
        "media_type": "movie",
        "movie_year": "2015",
    }
    print(imdb_get_data_from_datasets(imdb_search_criteria))
