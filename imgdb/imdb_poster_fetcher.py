from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tqdm import tqdm
import logging
import click


def imdb_download_poster(url, name):
    poster_url = url
    url_test = "http://download.thinkbroadband.com/10MB.zip"
    ext = poster_url.split(".")[-1]
    movie_name = name
    file_name = movie_name.replace(" ", "_") + "." + ext

    try:
        r = urlopen(url)
    except HTTPError as e:
        logging.critical("Download server couldn't fulfill the request.")
        logging.debug("Error code: %s" % e.code)
    except URLError as e:
        if hasattr(e, "reason"):
            logging.critical("We failed to reach the download server.")
            logging.debug("Reason: %s" % e.reason)
        else:
            logging.critical("Error: %s" % e)
    else:
        try:
            file_size = int(r.getheader("Content-Length"))
        except (TypeError, ValueError):
            logging.critical("Filesize has to be an integer!")

        click.echo("Downloading: %s Size: %s KiB" %
                   (file_name, file_size / 1024))

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
            logging.critical(
                "It looks like something unexpected happened. Aborting!")


if __name__ == "__main__":
    imdb_download_poster(
        "https://m.media-amazon.com/images/M/MV5BMDE0NDM0N2EtZDE5MS00Mzk0LWE5MWMtMjliODJkOTI4Y2FkXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_FMjpg_UX1000_.jpg", "The Paper Tigers")
