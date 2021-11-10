import json
from urllib.request import urlopen, Request
import urllib.parse
from bs4 import BeautifulSoup
from random import uniform, choice
from time import sleep
import re
from urllib.error import URLError, HTTPError
import os
from dotenv import load_dotenv
load_dotenv()

# Creating the final JSON file that contains a curated list of Rotten Tomatoes certified fresh movies


def rt_construct_json():
    """ This function creates a JSON file that contains a list of movies with their respective metadata. """

    data = rt_parse_json()
    final_data = []

    for item in data:
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
            print('RT server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach RT server.')
                print('Reason: ', e.reason)
        else:
            data = json.loads(res.read().decode())
            results = data["results"]
            full_results.extend(results)
    return full_results

# Extracting the movie's release year from RT website


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
        'User-Agent': choice(user_agents_list),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    req = Request(full_url, headers=headers)

    try:
        response = urlopen(req)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
    else:
        soup = BeautifulSoup(response.read(), 'html.parser')
        title = soup.find("meta", property="og:title")["content"]
        regex = r"\(([\d^\)]+)\)"
        year = re.search(regex, title).group(1) if title else ""
        print(f"The movie's release year is {year}")
    return year

# Getting movie data from IMDB (rating, poster url)


def imdb_get_data(title):
    """ This function use Google Custom Search API to extract the poster url of IMDB movies. """

    movie_title = title
    gcsearch_api_key = os.getenv("GSEARCH_API_KEY")
    imdb_custom_search_id = os.getenv("IMDB_GCUSTOM_SEARCH_ID")
    query = urllib.parse.quote_plus(movie_title)
    url = f"https://www.googleapis.com/customsearch/v1/siterestrict?key={gcsearch_api_key}&cx={imdb_custom_search_id}&num=10&q={query}"
    regex = r"(?<=UY1200)(.*?)(?=.(jpg|png|jpeg)\b)"

    try:
        res = urlopen(url)
    except HTTPError as e:
        print('Google Search server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach Google Search server.')
            print('Reason: ', e.reason)
    else:
        data = json.loads(res.read().decode())
        item_list = data.get("items")
        results = {}

        if item_list:
            for item in item_list:
                try:
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
                    imdb_poster_url_pattern = re.search(
                        regex, imdb_movie_cropped_poster_url)
                    imdb_poster_url = re.sub(
                        regex, "", imdb_movie_cropped_poster_url) if imdb_poster_url_pattern else imdb_movie_cropped_poster_url

                    print(
                        f"The IMDB cropped poster URL is {imdb_movie_cropped_poster_url}")
                    print(
                        f"The IMDB poster URL is {imdb_poster_url}")

                    # print(f"The URL pattern is: {imdb_poster_url_pattern.group(0)}")
                    # print(f"The movie's rating is {imdb_rating}, the thumbnail's url is {imdb_movie_thumbnail_url}")

                    # try:
                    #    float(imdb_rating)
                    #    is_rating_float = True
                    # except ValueError:
                    #    is_rating_float = False

                    results = {
                        # "imdbRating": float(imdb_rating) if is_rating_float else imdb_rating,
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
    with open('results.json', 'w') as json_file:
        json.dump(dict_input, json_file, indent=4)


if __name__ == "__main__":
    # rt_parse_json()
    # rt_construct_json()
    # rt_get_movie_year("/m/can_you_ever_forgive_me")
    imdb_get_data("Dunes")
