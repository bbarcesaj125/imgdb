import datetime
import json
from urllib.request import urlopen, Request
import urllib.parse
from bs4 import BeautifulSoup
from random import uniform, choice
from time import sleep
import re
from urllib.error import URLError, HTTPError
import os
from imgdb.imdb_data_handler import (
    imdb_get_data_from_datasets,
    merge_tsv_files,
    datasets_updater,
)
from imgdb.imdb_poster_fetcher import imdb_download_poster
from imgdb.image_processor import generate_media_image
import click
from imgdb.utils import *
from imgdb.exceptions import InputError
from imgdb.config import check_config_file, Config
from pathlib import Path
from difflib import SequenceMatcher


@click.command()
@click.option("--mov", help="The title of the movie.")
@click.option("--tv", help="The title of the series.")
@click.option("--tvmini", help="The title of the mini series.")
@click.option("--debug", default="debug", help="The logging level of the application.")
@click.option("--logfile", help="The path of the log file.")
@click.option("--freq", help="The update frequency of the datasets.")
@click.option(
    "-d", is_flag=True, default=False, help="Download the movie's poster image."
)
@click.option(
    "-e",
    is_flag=True,
    default=False,
    help="Save the edited image containing the movie's ratings.",
)
def imdb_cli_init(mov, tv, tvmini, debug, logfile, freq, d, e):
    """Imdb CLI search."""

    # Checking and creating or getting current config info
    current_config = check_config_file(debug)
    if current_config == 0:
        return

    # Making sure that command-line options override those present in the configuration file
    runtime_options = {
        "download": d if d else current_config.get("download"),
        "image_edit": e if e else current_config.get("image editing"),
        "log_file_path": logfile if logfile else current_config.get("log_file_path"),
        "freq": freq if freq else current_config.get("update frequency"),
        "gsearch_api_key": current_config.get("google search api key"),
        "imdb_gsearch_id": current_config.get("imdb custom search id"),
    }
    logging.debug("Runtime options: %s" % runtime_options)

    # Setting up a logger
    if runtime_options["log_file_path"]:
        if runtime_options["log_file_path"].split(".")[-1] == "log":
            log_file_path = Path(runtime_options["log_file_path"]).resolve()
            logfile_directory = log_file_path.parents[0]
            is_logfile = log_file_path.is_file()
            is_logfile_path = logfile_directory.is_dir()
            test_log_paths = (
                str(log_file_path) == Config.DEFAULT_CONFIG["general"]["log file path"]
            )

            if not test_log_paths:
                if is_logfile_path:
                    try:
                        os.link(
                            Config.DEFAULT_CONFIG["general"]["log file path"],
                            log_file_path,
                        )
                    except PermissionError:
                        click.echo(
                            Tcolors.FAIL
                            + "Permission denied. You don't have the required permissions on '%s'!"
                            % logfile_directory
                            + Tcolors.ENDC
                        )
                        logging.critical(
                            "Permission denied. You don't have the required permissions on '%s'!"
                            % logfile_directory
                        )
                        return
                else:
                    click.echo(
                        Tcolors.WARNING
                        + "The log file's directory does not exist!"
                        + Tcolors.ENDC
                    )
                    logging.warning("The log file's directory does not exist!")
                    return
        else:
            click.echo(
                Tcolors.WARNING
                + "Either the log file's path is invalid or that it doesn't end with the .log extension!"
                + Tcolors.ENDC
            )
            logging.warning(
                "Either the log file's path is invalid or that it doesn't end with the .log extension!"
            )
            return

    # Updating the datasets
    dataset_update_status = datasets_updater(runtime_options["freq"])
    if dataset_update_status == 0:
        return

    # Creating a dictionary containing a list of all mutually exclusive options
    options = {"mov": mov, "tv": tv, "tvmini": tvmini}

    used_options = []

    # Retrieving all used options and storing them in a list
    for key, value in options.items():
        if options[key] != None:
            used_options.append(options[key])
    try:
        if len(used_options) == 0:
            raise InputError("Command launched without options!")
    except InputError as e:
        logging.warning("Error: %s. Context: %s" % (e.name, e.error_ctx))
        click.echo(
            Tcolors.WARNING + "Please specify the media type argument!" + Tcolors.ENDC
        )
    else:
        # Here, this code only executes when the user has specified only one option from the mutually exclusive options
        if len(used_options) == 1:
            media_name = used_options[0]
            media_type = list(options.keys())[list(options.values()).index(media_name)]

            logging.debug("Media title: %s" % media_name)
            logging.debug("Media type: %s" % media_type)
            click.echo(Tcolors.OK_GREEN + "Fetching data..." + Tcolors.ENDC)

            imdb_data = imdb_get_data(
                media_name,
                media_type,
                api_keys=[
                    runtime_options["gsearch_api_key"],
                    runtime_options["imdb_gsearch_id"],
                ],
            )

            if imdb_data:
                rt_data = rt_get_data(
                    imdb_data["imdb_title"],
                    imdb_data["imdb_original_title"],
                    media_type,
                    imdb_data["imdb_year"],
                )
                rt_media_rating = rt_data["rt_rating"] if rt_data else "N/A"

                click.echo(
                    "Title: %s" % imdb_data["imdb_title"]
                    + "\nGenres: %s" % ", ".join(map(str, imdb_data["imdb_genres"]))
                    + "\nYear: %s" % imdb_data["imdb_year"]
                    + "\nRuntime: %s min" % imdb_data["imdb_runtime"]
                    + "\nIMDb Rating: %s" % imdb_data["imdb_rating"]
                    + "\nRottenTomatoes Rating: %s" % rt_media_rating
                    + "\nDescription: %s"
                    % replace_every_nth(50, " ", "\n", imdb_data["imdb_description"])
                )

                if (
                    runtime_options["download"] == True
                    or runtime_options["image_edit"] == True
                ):
                    downloaded_image_data = imdb_download_poster(
                        imdb_data["imdb_poster_url"], imdb_data["imdb_title"]
                    )
                    if runtime_options["image_edit"] == True:
                        generate_media_image(
                            imdb_data["imdb_title"],
                            imdb_data["imdb_rating"],
                            rt_media_rating,
                            downloaded_image_data["filename"],
                            downloaded_image_data["filepath"],
                        )
                    elif runtime_options["download"]:
                        click.echo(
                            Tcolors.FAIL
                            + "The image editing option is invalid!"
                            + Tcolors.ENDC
                        )
                    logging.critical("The image editing option is invalid!")

                elif runtime_options["download"]:
                    click.echo(
                        Tcolors.FAIL + "The download option is invalid!" + Tcolors.ENDC
                    )
                    logging.critical("The download option is invalid!")

        else:
            # The user has specified at least two mutually exclusive options
            mut_exclusive_options = [
                ex for ex in options.keys() if options[ex] is not None
            ]
            click.echo(
                Tcolors.WARNING
                + " and ".join(mut_exclusive_options)
                + " are conflicting options. Please use only one option at a time!"
                + Tcolors.ENDC
            )
            logging.warning(
                " and ".join(mut_exclusive_options)
                + " are conflicting options. Please use only one option at a time!"
            )


def rt_construct_json():
    """This function creates a JSON file that contains a list of movies with their respective metadata."""

    data = rt_parse_json()
    final_data = []

    for item in data:
        logging.info("Here we go! The movie's title is: %s" % item["title"])
        # Random wait to avoid rate limits
        sleep(uniform(1, 2.5))
        imdb_results = imdb_get_data(item["title"])

        movie_data = {
            "tomatoTitle": item["title"],
            "tomatoScore": item["tomatoScore"],
            "imdbRating": imdb_results["imdb_rating"],
            "dvdReleaseDate": item.get("dvdReleaseDate")
            if item.get("dvdReleaseDate")
            else "N/A",
            "year": rt_get_movie_year(item["url"]),
            "runtime": item.get("runtime") if item.get("runtime") else "N/A",
            "mpaaRating": item.get("mpaaRating") if item.get("mpaaRating") else "N/A",
            "thumbnailUrl": imdb_results["imdb_thumbnail_url"],
            "posterUrl": imdb_results["imdb_poster_url"],
        }

        final_data.append(movie_data.copy())

    # Writing the resulting dictionary to a JSON file
    write_json_to_file(final_data)


def rt_parse_json():
    """This is a function that fetches and parses JSON data from a url (RottenTomatoes semi-public API)."""

    api_urls = [
        "https://www.rottentomatoes.com/api/private/v2.0/browse?minTomato=70&maxTomato=100&maxPopcorn=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified=true&sortBy=release&type=cf-dvd-streaming-all",
        "https://www.rottentomatoes.com/api/private/v2.0/browse?maxTomato=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified&sortBy=release&type=cf-dvd-streaming-all&page=2",
    ]
    full_results = []

    for url in api_urls:
        try:
            res = urlopen(url)
        except HTTPError as e:
            logging.critical("RT server couldn't fulfill the request.")
            logging.debug("Error code: %s" % e.code)
            click.echo(
                Tcolors.FAIL + "RT server couldn't fulfill the request." + Tcolors.ENDC
            )
        except URLError as e:
            logging.critical("We failed to reach RT server.")
            click.echo(Tcolors.FAIL + "We failed to reach RT server." + Tcolors.ENDC)
            if hasattr(e, "reason"):
                logging.debug("Reason: %s" % e.reason)

        else:
            data = json.loads(res.read().decode())
            results = data["results"]
            full_results.extend(results)
    return full_results


def rt_search_media(title, mtype):
    """This is a function that searches RT site for a specific title (movie or series)."""

    rt_search_term = title
    media_type = mtype
    query = urllib.parse.quote_plus(rt_search_term)
    url = f"https://www.rottentomatoes.com/search?search={query}"

    # Implementing a random wait timer to avoid some anti-scraping detection methods (not sure if it works but gonna keep it anyway).
    sleep(uniform(0.05, 0.1))

    # Creating a list of user agents to use with urllib
    user_agents_list = [
        "Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)",
        "CheckMarkNetwork/1.0 (+http://www.checkmarknetwork.com/spider.html)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone11,8;FBMD/iPhone;FBSN/iOS;FBSV/13.3.1;FBSS/2;FBID/phone;FBLC/en_US;FBOP/5;FBCR/]",
        "Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 7.1.2; AFTMM Build/NS6265; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36",
    ]

    # Picking up a random user agents each time we make a connection to the server
    headers = {
        "User-Agent": choice(user_agents_list),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    req = Request(url, headers=headers)

    try:
        response = urlopen(req)
    except HTTPError as e:
        logging.critical("RT server couldn't fulfill the request.")
        logging.debug("Error code: %s" % e.code)
        click.echo(
            Tcolors.FAIL + "RT server couldn't fulfill the request." + Tcolors.ENDC
        )
    except URLError as e:
        logging.critical("We failed to reach RT server.")
        click.echo(Tcolors.FAIL + "We failed to reach RT server." + Tcolors.ENDC)
        if hasattr(e, "reason"):
            logging.debug("Reason: %s" % e.reason)

    else:
        soup = BeautifulSoup(response.read(), "html.parser")
        try:
            if media_type == "movies":
                rt_media_title = soup.find(
                    "search-page-result", {"type": "movie"}
                ).find("a", {"data-qa": "info-name"})
            elif media_type == "tvSeries":
                rt_media_title = soup.find("search-page-result", {"type": "tv"}).find(
                    "a", {"data-qa": "info-name"}
                )
        except Exception as e:
            logging.critical("We couldn't retrieve the movie's title from RT.")
            logging.debug("Error: %s" % e)
            click.echo(
                Tcolors.FAIL
                + "We couldn't retrieve the movie's title from RT."
                + Tcolors.ENDC
            )
            return
        logging.info("RT media title is %s: " % rt_media_title.text.strip())
        return rt_media_title.text.strip()


def imdb_get_data(title, mtype, api_keys=[]):
    """This function fetches the poster url and other data related to Imdb movies from Google Custom Search JSON API."""

    movie_title = title
    media_type = mtype
    gcsearch_api_key = api_keys[0]
    imdb_custom_search_id = api_keys[1]
    query = urllib.parse.quote_plus(movie_title)
    url = f"https://www.googleapis.com/customsearch/v1/siterestrict?key={gcsearch_api_key}&cx={imdb_custom_search_id}&num=10&q={query}"
    regex_url = r"(?<=UY1200)(.*?)(?=.(jpg|png|jpeg)\b)"
    regex_year_parentheses = r"\(([^)]+)\)"
    regex_year = r"\d+"
    regex_title = r"(^.*?)(?=\s\()"

    try:
        res = urlopen(url)
    except HTTPError as e:
        logging.critical("Google Search server couldn't fulfill the request.")
        logging.debug("Error code: %s" % e.code)
        click.echo(
            Tcolors.FAIL
            + "Google Search server couldn't fulfill the request."
            + Tcolors.ENDC
        )
    except URLError as e:
        logging.critical("We failed to reach Google Search server.")
        click.echo(
            Tcolors.FAIL + "We failed to reach Google Search server." + Tcolors.ENDC
        )
        if hasattr(e, "reason"):
            logging.debug("Reason: %s" % e.reason)

    else:
        data = json.loads(res.read().decode())
        item_list = data.get("items")
        results = {}

        if item_list:
            for item in item_list:
                try:
                    imdb_title = item["title"]
                    # imdb_rating = item["pagemap"]["aggregaterating"][0]["ratingvalue"]
                    imdb_description = item["pagemap"]["metatags"][0]["og:description"]
                    imdb_movie_thumbnail_url = item["pagemap"]["cse_thumbnail"][0][
                        "src"
                    ]
                    imdb_movie_cropped_poster_url = item["pagemap"]["metatags"][0][
                        "og:image"
                    ]
                except KeyError as err:
                    logging.critical("KeyError: {0}".format(err))
                    click.echo(Tcolors.FAIL + "KeyError: %s" % err + Tcolors.ENDC)
                    continue
                except NameError as err:
                    logging.critical("NameError: {0}".format(err))
                    click.echo(Tcolors.FAIL + "NameError: %s" % err + Tcolors.ENDC)
                except IndexError as err:
                    logging.critical("IndexError: {0}".format(err))
                    click.echo(Tcolors.FAIL + "IndexError: %s" % err + Tcolors.ENDC)
                except Exception as e:
                    logging.critical("Unexpected error: {0}".format(e))
                    click.echo(Tcolors.FAIL + "Unexpected error: %s" % e + Tcolors.ENDC)
                    raise
                else:

                    # Google custom search engine changed their JSON response. Now, there is no need to process the imdb_movie_cropped_poster_url.
                    # The imdb_movie_cropped_poster_url which we get directly from the JSON results already contains the desired image size.
                    # Thus, there is no need to use regex substitutions on imdb_movie_cropped_poster_url.
                    # But I will leave the part that deals with substitutions intact as Google can change their API anytime they want.
                    imdb_poster_url_pattern = re.search(
                        regex_url, imdb_movie_cropped_poster_url
                    )
                    imdb_poster_url = (
                        re.sub(regex_url, "", imdb_movie_cropped_poster_url)
                        if imdb_poster_url_pattern
                        else imdb_movie_cropped_poster_url
                    )

                    imdb_year_parentheses_test = re.search(
                        regex_year_parentheses, imdb_title
                    )
                    imdb_year_parentheses = (
                        re.findall(regex_year_parentheses, imdb_title)[0]
                        if imdb_year_parentheses_test
                        else "N/A"
                    )

                    imdb_title_without_parentheses_test = re.search(
                        regex_title, imdb_title
                    )
                    imdb_title_without_parentheses = (
                        re.findall(regex_title, imdb_title)[0]
                        if imdb_title_without_parentheses_test
                        else imdb_title
                    )
                    logging.debug(
                        "The IMDB raw poster URL is: %s" % imdb_movie_cropped_poster_url
                    )
                    logging.debug("The IMDB poster URL is: %s" % imdb_poster_url)
                    logging.debug(
                        "Imdb extracted title without parentheses is: %s"
                        % imdb_title_without_parentheses
                    )

                    try:
                        int(imdb_year_parentheses)
                        is_year_int = True
                    except ValueError:
                        is_year_int = False

                    # If the value between the parentheses is not an integer, then we extract the first
                    # year value from the text inside the parentheses.
                    if not is_year_int:
                        imdb_year_string_test = re.search(
                            regex_year, imdb_year_parentheses
                        )
                        if imdb_year_string_test:
                            imdb_year_from_string = re.findall(
                                regex_year, imdb_year_parentheses
                            )[0]
                        else:
                            imdb_year_from_string = "N/A"

                    imdb_media_types = {
                        "mov": "movie",
                        "tv": "tvSeries",
                        "tvmini": "tvMiniSeries",
                    }

                    try:
                        imdb_pageconst = item["pagemap"]["metatags"][0][
                            "imdb:pageconst"
                        ]
                    except Exception as e:
                        imdb_pageconst = None

                    imdb_search_criteria = {
                        "media_title": imdb_title_without_parentheses,
                        "media_pageconst": imdb_pageconst,
                        "media_type": imdb_media_types[media_type],
                        "media_year": imdb_year_parentheses
                        if is_year_int
                        else imdb_year_from_string,
                    }

                    imdb_movie_data = imdb_get_data_from_datasets(imdb_search_criteria)

                    # If imdb_get_data_from_datasets() function doesn't return anything, then we assume that either the requested
                    # movie doesn't exist on the dataset or that the media type was incorrect
                    # (e.g., specifying "tvSeries" instead of "movie" for a movie).
                    try:
                        if imdb_movie_data == None:
                            raise TypeError
                    except TypeError:
                        click.echo(
                            Tcolors.FAIL
                            + "Either the requested title doesn't exist or that the media type was incorrectly specified!"
                            + Tcolors.ENDC
                        )
                        logging.warning(
                            "Either the requested title doesn't exist or that the media type was incorrectly specified!"
                        )
                        return

                    try:
                        float(imdb_movie_data["averageRating"])
                        is_rating_float = True
                    except (ValueError, TypeError) as e:
                        is_rating_float = False

                    results = {
                        "imdb_title": imdb_movie_data["primaryTitle"],
                        "imdb_original_title": imdb_movie_data["originalTitle"],
                        "imdb_year": imdb_year_parentheses
                        if is_year_int
                        else imdb_year_from_string,
                        "imdb_rating": imdb_movie_data["averageRating"]
                        if is_rating_float
                        else "N/A",
                        "imdb_genres": imdb_movie_data["genres"],
                        "imdb_runtime": imdb_movie_data["runtimeMinutes"]
                        if imdb_movie_data["runtimeMinutes"] != "\\N"
                        else "N/A",
                        "imdb_description": imdb_description,
                        "imdb_thumbnail_url": imdb_movie_thumbnail_url,
                        "imdb_poster_url": imdb_poster_url,
                    }

                    logging.info("Imdb's media data: %s" % results)
                    return results
        else:
            logging.warning("No results!")
            click.echo(Tcolors.WARNING + "No results!" + Tcolors.ENDC)


def rt_get_data(title, title_original, mtype, year):
    """This function uses RT semi-public search API to get information about a specific title (movie or series)."""

    movie_title = title
    movie_title_original = title_original
    media_type = mtype
    media_year = year
    rt_media_types = {
        "mov": "movies",
        "tv": "tvSeries",
        "tvmini": "tvSeries",
    }

    try:
        int(media_year)
        is_year_int = True
    except ValueError:
        is_year_int = False

    if not is_year_int:
        return

    def rt_json_fetcher(rt_movie_title):
        """This function uses RT semi-public search API to get a JSON response containing information about a specific title (movie or series)."""

        movie_title_rt = rt_movie_title
        query = urllib.parse.quote_plus(str(movie_title_rt))
        url = f"https://www.rottentomatoes.com/api/private/v2.0/search?q={query}"

        try:
            res = urlopen(url)
        except HTTPError as e:
            logging.critical("RT API server couldn't fulfill the request.")
            logging.debug("Error code: %s" % e.code)
            click.echo(
                Tcolors.FAIL
                + "RT API server couldn't fulfill the request."
                + Tcolors.ENDC
            )
        except URLError as e:
            logging.critical("We failed to reach RT API server.")
            click.echo(
                Tcolors.FAIL + "We failed to reach RT API server." + Tcolors.ENDC
            )
            if hasattr(e, "reason"):
                logging.debug("Reason: %s" % e.reason)
        else:
            data = json.loads(res.read().decode())
            media_list_json = data.get(rt_media_types[media_type])
            return media_list_json

    media_list = rt_json_fetcher(movie_title)

    if not media_list:
        rt_search_title = rt_search_media(movie_title, rt_media_types[media_type])
        if not rt_search_title:
            return
        else:
            media_list = rt_json_fetcher(rt_search_title)
            if not media_list:
                logging.warning("RT search returned no results!")
                click.echo(
                    Tcolors.WARNING + "RT search returned no results!" + Tcolors.ENDC
                )
                return

    results = {}
    for item in media_list:
        try:
            if rt_media_types[media_type] == "movies":
                rt_title = item["name"]
                rt_year = item["year"]
            else:
                rt_title = item["title"]
                rt_year = item["startYear"]

            rt_freshness = item["meterClass"]

        except KeyError as err:
            logging.critical("KeyError: {0}".format(err))
            click.echo(Tcolors.FAIL + "KeyError: %s" % err + Tcolors.ENDC)
            continue
        except NameError as err:
            logging.critical("NameError: {0}".format(err))
            click.echo(Tcolors.FAIL + "NameError: %s" % err + Tcolors.ENDC)
        except IndexError as err:
            logging.critical("IndexError: {0}".format(err))
            click.echo(Tcolors.FAIL + "IndexError: %s" % err + Tcolors.ENDC)
        except Exception as e:
            logging.critical("Unexpected error: {0}".format(e))
            click.echo(Tcolors.FAIL + "Unexpected error: %s" % e + Tcolors.ENDC)
            raise
        else:

            # Getting the similarity ratio between IMDb title and RT title
            similar_title_1 = SequenceMatcher(None, rt_title, movie_title).ratio()
            similar_title_2 = SequenceMatcher(
                None, rt_title, movie_title + " " + movie_title_original
            ).ratio()
            logging.debug(
                "Similar ratio 1: %s, similar ratio 2: %s"
                % (similar_title_1, similar_title_2)
            )

            # Sometimes the release year in RT is slightly different than that of IMDb.
            # In this case, it is usually off by 1 or 2 years).
            # Here, we use that difference and combine it with the similar ratio to get
            # the exact title we are looking for.
            # The code here is not bullet-proof and might provide inaccurate results,
            # but this is very rare according to my tests.
            # We can always modify the similarity threshold to increase the accuracy.
            if (
                rt_year == int(media_year)
                or rt_year in range(int(media_year) - 2, int(media_year) + 3)
            ) and max(similar_title_1, similar_title_2) >= 0.75:
                logging.debug("Matched year is: %s" % rt_year)

                rt_rating = item.get("meterScore")
                results = {
                    "rt_title": rt_title,
                    "rt_year": rt_year,
                    "rt_rating": rt_rating if rt_rating else "N/A",
                    "rt_freshness": rt_freshness,
                }

                logging.info("RT's media data: %s" % results)
                return results


def write_json_to_file(json_dict):
    """This functions writes a dictionary (input) to a JSON file."""

    dict_input = json_dict
    with open("results.json", "w") as json_file:
        json.dump(dict_input, json_file, indent=4)


if __name__ == "__main__":
    imdb_cli_init()
    # movie = rt_search_media("westworld", "tvSeries")
    # print("MOVIE", movie)
    # data = rt_get_data("American Horror Story", "American Horror Story", "tv", "2013")
    # print(data)
    # results = rt_parse_json()
    # print(results)
    # rt_construct_json()
    # year = rt_get_movie_year("/m/can_you_ever_forgive_me")
    # print(year)
    # imdb_get_data("arrows")
