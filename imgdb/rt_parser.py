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
from imdb_data_handler import imdb_get_data_from_datasets, merge_tsv_files, datasets_updater
from imdb_poster_fetcher import imdb_download_poster
import click
from utils import *
from exceptions import InputError
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


@click.command()
@click.option("--mov", help="The title of the movie.")
@click.option("--tv", help="The title of the series.")
@click.option("--tvmini", help="The title of the mini series.")
@click.option("--debug", default="debug", help="The logging level of the application.")
@click.option("--freq", default="weekly", help="The update frequency of the datasets.")
@click.option("-d", is_flag=True, default=False, help="Download the movie's poster image.")
def imdb_cli_init(mov, tv, tvmini, debug, freq, d):
    """ Imdb CLI search """

    # Setting up a logger
    logger(debug)

    # Updating the datasets
    base_path = Path("./imdb_datasets/").resolve()
    logging.debug("The base path is: %s" % base_path)
    datasets_updater(freq, base_path)

    # Creating a dictionary containing a list of all mutually exclusive options
    options = {
        "mov": mov,
        "tv": tv,
        "tvmini": tvmini
    }

    used_options = []

    # Retrieving all used options and storing them in a list
    for key, value in options.items():
        if options[key] != None:
            used_options.append(options[key])
    try:
        if len(used_options) == 0:
            raise InputError
    except InputError as e:
        logging.warning("Please specify the media type argument!")
        logging.debug("Error: %s" % e.name)
        click.echo(
            Tcolors.warning + "Please specify the media type argument!" + Tcolors.endc)
    else:
        # Here, this code only executes when the user has specified only one option from the mutually exclusive options
        if len(used_options) == 1:
            media_name = used_options[0]
            media_type = list(options.keys())[list(
                options.values()).index(media_name)]

            logging.debug("Media title: %s" % media_name)
            logging.debug("Media type: %s" % media_type)

            click.echo(Tcolors.ok_green +
                       "Fetching data ..." + Tcolors.endc)
            imdb_data = imdb_get_data(media_name, media_type)
            if imdb_data:
                click.echo(
                    "Title: %s" % imdb_data["imdbTitle"] +
                    "\nGenres: %s" % ", ".join(map(str, imdb_data["imdbGenres"])) +
                    "\nYear: %s" % imdb_data["imdbYear"] +
                    "\nRuntime: %s min" % imdb_data["imdbRuntime"] +
                    "\nRating: %s" % imdb_data["imdbRating"] +
                    "\nDescription: %s" % replace_every_nth(50, " ", "\n", imdb_data["imdbDescription"]))

                if d:
                    imdb_download_poster(
                        imdb_data["imdbPosterUrl"], imdb_data["imdbTitle"])

        else:
            # The user has specified at least two mutually exclusive options
            mut_exclusive_options = [
                ex for ex in options.keys() if options[ex] is not None]
            click.echo(Tcolors.warning + " and ".join(mut_exclusive_options) +
                       " are conflicting options. Please use only one option at a time!" + Tcolors.endc)
            logging.warning(" and ".join(mut_exclusive_options) +
                            " are conflicting options. Please use only one option at a time!")


def rt_construct_json():
    """ This function creates a JSON file that contains a list of movies with their respective metadata. """

    data = rt_parse_json()
    final_data = []

    for item in data:
        logging.info("Here we go! The movie's title is: %s" % item['title'])
        # Random wait to avoid rate limits
        sleep(uniform(1, 2.5))
        imdb_results = imdb_get_data(item["title"])

        movie_data = {
            "tomatoTitle": item["title"],
            "tomatoScore": item["tomatoScore"],
            "imdbRating": imdb_results["imdbRating"],
            "dvdReleaseDate": item.get("dvdReleaseDate") if item.get("dvdReleaseDate") else "N/A",
            "year": rt_get_movie_year(item["url"]),
            "runtime": item.get("runtime") if item.get("runtime") else "N/A",
            "mpaaRating": item.get("mpaaRating") if item.get("mpaaRating") else "N/A",
            "thumbnailUrl": imdb_results["imdbThumbUrl"],
            "posterUrl": imdb_results["imdbPosterUrl"]
        }

        final_data.append(movie_data.copy())

    # Writing the resulting dictionary to a JSON file
    write_json_to_file(final_data)


def rt_parse_json():
    """ This is a function that fetches and parses JSON data from a url (RottenTomatoes semi-public API). """

    api_urls = ["https://www.rottentomatoes.com/api/private/v2.0/browse?minTomato=70&maxTomato=100&maxPopcorn=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified=true&sortBy=release&type=cf-dvd-streaming-all",
                "https://www.rottentomatoes.com/api/private/v2.0/browse?maxTomato=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified&sortBy=release&type=cf-dvd-streaming-all&page=2"]
    full_results = []

    for url in api_urls:
        try:
            res = urlopen(url)
        except HTTPError as e:
            logging.critical("RT server couldn't fulfill the request.")
            logging.debug("Error code: %s" % e.code)
            click.echo(Tcolors.fail +
                       "RT server couldn't fulfill the request." + Tcolors.endc)
        except URLError as e:
            logging.critical("We failed to reach RT server.")
            click.echo(Tcolors.fail +
                       "We failed to reach RT server." + Tcolors.endc)
            if hasattr(e, 'reason'):
                logging.debug("Reason: %s" % e.reason)

        else:
            data = json.loads(res.read().decode())
            results = data["results"]
            full_results.extend(results)
    return full_results


def rt_get_movie_year(rurl):
    """ This is a function that takes in the relative url of a RT movie and return its release year. """

    base_url = "https://www.rottentomatoes.com"
    relative_url = rurl
    full_url = base_url + relative_url
    logging.info("The RT's full URL is: %s" % full_url)

    # Implementing a random wait timer to avoid some anti-scraping detection methods (not sure if it works but gonna keep it anyway).
    sleep(uniform(0.05, 0.1))

    # Creating a list of user agents to use with urllib
    user_agents_list = ["Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)", "CheckMarkNetwork/1.0 (+http://www.checkmarknetwork.com/spider.html)", "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone11,8;FBMD/iPhone;FBSN/iOS;FBSV/13.3.1;FBSS/2;FBID/phone;FBLC/en_US;FBOP/5;FBCR/]", "Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36", "Mozilla/5.0 (Linux; Android 7.1.2; AFTMM Build/NS6265; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36"]

    # Picking up a random user agents each time we make a connection to the server
    headers = {
        "User-Agent": choice(user_agents_list),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    req = Request(full_url, headers=headers)

    try:
        response = urlopen(req)
    except HTTPError as e:
        logging.critical("RT server couldn't fulfill the request.")
        logging.debug("Error code: %s" % e.code)
        click.echo(Tcolors.fail +
                   "RT server couldn't fulfill the request." + Tcolors.endc)
    except URLError as e:
        logging.critical("We failed to reach RT server.")
        click.echo(Tcolors.fail +
                   "We failed to reach RT server." + Tcolors.endc)
        if hasattr(e, "reason"):
            logging.debug("Reason: %s" % e.reason)

    else:
        soup = BeautifulSoup(response.read(), 'html.parser')
        try:
            date = soup.find("time")["datetime"]
        except Exception as e:
            logging.critical(
                "We couldn't retrieve the movie's release year from RT.")
            logging.debug("Error: %s" % e)
            click.echo(Tcolors.fail +
                       "We couldn't retrieve the movie's release year from RT." + Tcolors.endc)
            year = datetime.datetime.now().year
        else:
            logging.debug("The scrapped date is: %s" % date)
            try:
                date_year = datetime.datetime.strptime(date, "%b %d, %Y").year
                is_date_year_valid = True
                logging.info("The movie's release year is: %s" % date_year)
            except Exception as e:
                is_date_year_valid = False

            year = date_year if is_date_year_valid else datetime.datetime.now().year
            logging.info("The movie's release year is: %s" % year)
        return year


def imdb_get_data(title, mtype):
    """ This function fetches the poster url and other data related to Imdb movies from Google Custom Search JSON API. """

    movie_title = title
    media_type = mtype
    gcsearch_api_key = os.getenv("GSEARCH_API_KEY")
    imdb_custom_search_id = os.getenv("IMDB_GCUSTOM_SEARCH_ID")
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
        click.echo(Tcolors.fail +
                   "Google Search server couldn't fulfill the request." + Tcolors.endc)
    except URLError as e:
        logging.critical("We failed to reach Google Search server.")
        click.echo(Tcolors.fail +
                   "We failed to reach Google Search server." + Tcolors.endc)
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
                    imdb_movie_thumbnail_url = item["pagemap"]["cse_thumbnail"][0]["src"]
                    imdb_movie_cropped_poster_url = item["pagemap"]["metatags"][0]["og:image"]
                except KeyError as err:
                    logging.critical("KeyError: {0}".format(err))
                    click.echo(Tcolors.fail +
                               "KeyError: %s" % err + Tcolors.endc)
                    continue
                except NameError as err:
                    logging.critical("NameError: {0}".format(err))
                    click.echo(Tcolors.fail +
                               "NameError: %s" % err + Tcolors.endc)
                except IndexError as err:
                    logging.critical("IndexError: {0}".format(err))
                    click.echo(Tcolors.fail +
                               "IndexError: %s" % err + Tcolors.endc)
                except Exception as e:
                    logging.critical("Unexpected error: {0}".format(e))
                    click.echo(Tcolors.fail +
                               "Unexpected error: %s" % e + Tcolors.endc)
                    raise
                else:
                    # Google custom search engine changed their JSON response. Now, there is no need to process the imdb_movie_cropped_poster_url.
                    # The imdb_movie_cropped_poster_url which we get directly from the JSON results already contains the desired image size.
                    # Thus, there is no need to use regex substitutions on imdb_movie_cropped_poster_url.
                    # But I will leave the part that deals with substitutions intact as Google can change their API anytime they want.

                    imdb_poster_url_pattern = re.search(
                        regex_url, imdb_movie_cropped_poster_url)
                    imdb_poster_url = re.sub(
                        regex_url, "", imdb_movie_cropped_poster_url) if imdb_poster_url_pattern else imdb_movie_cropped_poster_url

                    imdb_year_parentheses_test = re.search(
                        regex_year_parentheses, imdb_title)
                    imdb_year_parentheses = re.findall(
                        regex_year_parentheses, imdb_title)[0] if imdb_year_parentheses_test else "N/A"

                    imdb_title_without_parentheses_test = re.search(
                        regex_title, imdb_title)
                    imdb_title_without_parentheses = re.findall(
                        regex_title, imdb_title)[0] if imdb_title_without_parentheses_test else imdb_title

                    logging.debug("The IMDB raw poster URL is: %s" %
                                  imdb_movie_cropped_poster_url)
                    logging.debug("The IMDB poster URL is: %s" %
                                  imdb_poster_url)
                    logging.debug(
                        "Imdb extracted title without parentheses is: %s" % imdb_title_without_parentheses)

                    try:
                        int(imdb_year_parentheses)
                        is_year_int = True
                    except ValueError:
                        is_year_int = False

                    # If the value between the parentheses is not an integer, then we extract the first year value from the text inside the parentheses.
                    if not is_year_int:
                        imdb_year_string_test = re.search(
                            regex_year, imdb_year_parentheses)
                        if imdb_year_string_test:
                            imdb_year_from_string = re.findall(
                                regex_year, imdb_year_parentheses)[0]
                        else:
                            imdb_year_from_string = "N/A"

                    imdb_media_types = {
                        "mov": "movie",
                        "tv": "tvSeries",
                        "tvmini": "tvMiniSeries"
                    }

                    imdb_search_criteria = {
                        "movie_title": imdb_title_without_parentheses,
                        "media_type": imdb_media_types[media_type],
                        "movie_year": imdb_year_parentheses if is_year_int else imdb_year_from_string
                    }

                    imdb_movie_data = imdb_get_data_from_datasets(
                        imdb_search_criteria)

                    # If imdb_get_data_from_datasets() function doesn't return anything, then we assume that either the requested
                    # movie doesn't exist on the dataset or that the media type was incorrect (e.g., specifying "tvSeries" instead of "movie" for a movie).
                    try:
                        if imdb_movie_data == None:
                            raise TypeError
                    except TypeError:
                        click.echo(
                            Tcolors.fail + "Either the requested title doesn't exist or that the media type was incorrectly specified!" + Tcolors.endc)
                        logging.warning(
                            "Either the requested title doesn't exist or that the media type was incorrectly specified!")
                        return

                    try:
                        float(imdb_movie_data["averageRating"])
                        is_rating_float = True
                    except (ValueError, TypeError) as e:
                        is_rating_float = False

                    results = {
                        "imdbTitle": imdb_movie_data["primaryTitle"],
                        "imdbYear": imdb_year_parentheses if is_year_int else imdb_year_from_string,
                        "imdbRating": imdb_movie_data["averageRating"] if is_rating_float else "N/A",
                        "imdbGenres": imdb_movie_data["genres"],
                        "imdbRuntime": imdb_movie_data["runtimeMinutes"] if imdb_movie_data["runtimeMinutes"] != "\\N" else "N/A",
                        "imdbDescription": imdb_description,
                        "imdbThumbUrl": imdb_movie_thumbnail_url,
                        "imdbPosterUrl": imdb_poster_url
                    }

                    logging.info("Imdb's movie data: %s" % results)
                    return results
        else:
            logging.warning("No results!")
            click.echo(Tcolors.warning + "No results!" + Tcolors.endc)


def write_json_to_file(json_dict):
    """ This functions writes a dictionary (input) to a JSON file. """

    dict_input = json_dict
    with open("results.json", "w") as json_file:
        json.dump(dict_input, json_file, indent=4)


if __name__ == "__main__":
    imdb_cli_init()
    # results = rt_parse_json()
    # print(results)
    # rt_construct_json()
    # year = rt_get_movie_year("/m/can_you_ever_forgive_me")
    # print(year)
    # imdb_get_data("arrows")
