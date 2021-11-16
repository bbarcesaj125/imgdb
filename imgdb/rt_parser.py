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
from imdb_data_handler import imdb_get_data_from_datasets
import click
from dotenv import load_dotenv
load_dotenv()

# Creating the final JSON file that contains a curated list of Rotten Tomatoes certified fresh movies


def rt_construct_json():
    """ This function creates a JSON file that contains a list of movies with their respective metadata. """

    data = rt_parse_json()
    final_data = []

    for item in data:
        print(f"Here we go!!!! {item['title']}")
        # Random wait to avoid rate limits
        sleep(uniform(1, 2.5))
        imdb_results = imdb_get_data(item["title"])

        movie_data = {
            "title": item["title"],
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

# Fetching JSON data and parsing it


def rt_parse_json():
    """ This is a function that fetches and parses JSON data from a url (RottenTomatoes semi-public API). """

    api_urls = ["https://www.rottentomatoes.com/api/private/v2.0/browse?minTomato=70&maxTomato=100&maxPopcorn=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified=true&sortBy=release&type=cf-dvd-streaming-all",
                "https://www.rottentomatoes.com/api/private/v2.0/browse?maxTomato=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified&sortBy=release&type=cf-dvd-streaming-all&page=2"]
    full_results = []

    for url in api_urls:
        try:
            res = urlopen(url)
        except HTTPError as e:
            print("RT server couldn't fulfill the request.")
            print("Error code: ", e.code)
        except URLError as e:
            print("We failed to reach RT server.")
            if hasattr(e, 'reason'):
                print("Reason: ", e.reason)
            else:
                print("Error: ", e)
        else:
            data = json.loads(res.read().decode())
            results = data["results"]
            full_results.extend(results)
    return full_results

# Extracting the movie's release year from RT website **Obsolete**


def rt_get_movie_year(rurl):
    """ This is a function that takes in the relative url of a RT movie and return its release year. """

    base_url = "https://www.rottentomatoes.com"
    relative_url = rurl
    full_url = base_url + relative_url
    print(full_url)

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
        print("RT server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except URLError as e:
        if hasattr(e, "reason"):
            print("We failed to reach RT server.")
            print("Reason: ", e.reason)
        else:
            print("Error: ", e)
    else:
        soup = BeautifulSoup(response.read(), 'html.parser')
        try:
            date = soup.find("time")["datetime"]
        except Exception as e:
            print("We couldn't retrieve the movie's release year from RT.")
            print("Error: ", e)
            year = datetime.datetime.now().year
        else:
            print("From rt_get_movie_year(): ", date)
            try:
                date_year = datetime.datetime.strptime(date, "%b %d, %Y").year
                is_date_year_valid = True
                print(
                    "From rt_get_movie_year(), the movie's release year is:", date_year)
            except Exception as e:
                is_date_year_valid = False

            # regex = r"\(([\d^\)]+)\)"
            # year = re.search(regex, title).group(1) if title else ""
            # print(f"The movie's release year is {year}")

            year = date_year if is_date_year_valid else datetime.datetime.now().year
            print("The movie's year is: ", year)
        return year

# Getting movie data from IMDB (rating, poster url)


def imdb_get_data(title):
    """ This function use Google Custom Search API to fetch the poster url and other data related to Imdb movies from Google Search JSON API. """

    movie_title = title
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
        print("Google Search server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except URLError as e:
        print("We failed to reach Google Search server.")
        if hasattr(e, "reason"):
            print("Reason: ", e.reason)
        else:
            print("Error: ", e)
    else:
        data = json.loads(res.read().decode())
        item_list = data.get("items")
        results = {}

        if item_list:
            for item in item_list:
                try:
                    imdb_title = item["title"]
                    # imdb_rating = item["pagemap"]["aggregaterating"][0]["ratingvalue"]
                    imdb_movie_thumbnail_url = item["pagemap"]["cse_thumbnail"][0]["src"]
                    imdb_movie_cropped_poster_url = item["pagemap"]["metatags"][0]["og:image"]
                except KeyError as err:
                    print("KeyError error: {0}".format(err))
                    continue
                except NameError as err:
                    print("NameError error: {0}".format(err))
                except IndexError as err:
                    print("IndexError error: {0}".format(err))
                except Exception as e:
                    print("Unexpected error: {0}".format(e))
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

                    print(
                        f"The IMDB cropped poster URL is {imdb_movie_cropped_poster_url}")
                    print(
                        f"The IMDB poster URL is {imdb_poster_url}")
                    print(
                        f"Imdb extracted title without parentheses is: {imdb_title_without_parentheses} and test is: {imdb_title_without_parentheses_test}")

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

                    imdb_search_criteria = {
                        "movie_title": imdb_title_without_parentheses,
                        "media_type": "tvMiniSeries",
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
                        print(
                            "Either the requested title doesn't exit or that the media type was incorrectly specified!")
                        return

                    try:
                        float(imdb_movie_data["averageRating"])
                        is_rating_float = True
                    except (ValueError, TypeError) as e:
                        is_rating_float = False

                    print(
                        f"IMDB rating is: ", imdb_movie_data['averageRating'] if is_rating_float else "N/A")

                    results = {
                        "imdbYear": imdb_year_parentheses if is_year_int else imdb_year_from_string,
                        "imdbRating": imdb_movie_data["averageRating"] if is_rating_float else "N/A",
                        "imdbGenres": [imdb_movie_data["genres"]],
                        "imdbThumbUrl": imdb_movie_thumbnail_url,
                        "imdbPosterUrl": imdb_poster_url
                    }
                    print(results)
                    return results
                break
        else:
            print(
                "No results!")

# Writing JSON to a file


def write_json_to_file(json_dict):
    """ This functions writes a dictionary (input) to a JSON file. """

    dict_input = json_dict
    with open("results.json", "w") as json_file:
        json.dump(dict_input, json_file, indent=4)


if __name__ == "__main__":
    #results = rt_parse_json()
    # print(results)
    # rt_construct_json()
    # year = rt_get_movie_year("/m/can_you_ever_forgive_me")
    # print(year)
    imdb_get_data("Planet Earth")
