from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tqdm import tqdm
import logging


def imdb_download_poster(url, name):
    poster_url = url
    url_test = "http://download.thinkbroadband.com/10MB.zip"
    ext = poster_url.split(".")[-1]
    movie_name = name
    file_name = movie_name.replace(" ", "_") + "." + ext

    try:
        r = urlopen(url)
    except HTTPError as e:
        print("Download server couldn't fulfill the request.")
        print("Error code: %s" % e.code)
        logging.critical("Download server couldn't fulfill the request.")
        logging.debug("Error code: %s" % e.code)
    except URLError as e:
        if hasattr(e, "reason"):
            print("We failed to reach the download server.")
            print("Reason: %s" % e.reason)
            logging.critical("We failed to reach the download server.")
            logging.debug("Reason: %s" % e.reason)
        else:
            print("Error: ", e)
            logging.critical("Error: %s" % e)
    else:

        file_size = int(r.getheader("Content-Length"))
        print("Downloading: %s Size: %s" % (file_name, file_size))

        block_size = 1024
        progress_bar = tqdm(total=file_size, unit="iB", unit_scale=True)
        with open(file_name, "wb") as f:
            while True:
                buffer = r.read(block_size)
                if not buffer:
                    break

                f.write(buffer)
                progress_bar.update(len(buffer))
        progress_bar.close()
        if file_size != 0 and progress_bar.n != file_size:
            print("It looks like something unexpected happened. Aborting!")


if __name__ == "__main__":
    imdb_download_poster(
        "https://m.media-amazon.com/images/M/MV5BMDE0NDM0N2EtZDE5MS00Mzk0LWE5MWMtMjliODJkOTI4Y2FkXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_FMjpg_UX1000_.jpg", "The Paper Tigers")
