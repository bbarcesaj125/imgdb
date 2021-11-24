from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tqdm import tqdm
from utils import Tcolors
import logging
import click


def imdb_download_poster(url, name=None, filepath=None):
    """ This function downloads a file from a given URL. """

    file_name = name
    if not filepath:
        poster_url = url
        url_test = "http://download.thinkbroadband.com/10MB.zip"
        ext = poster_url.split(".")[-1]
        file_name_with_ext = file_name.replace(" ", "_") + "." + ext
    else:
        file_name_with_ext = filepath

    try:
        r = urlopen(url)
    except HTTPError as e:
        logging.critical("Download server couldn't fulfill the request.")
        logging.debug("Error code: %s" % e.code)
        click.echo(Tcolors.fail +
                   "Download server couldn't fulfill the request." + Tcolors.endc)
    except URLError as e:
        if hasattr(e, "reason"):
            logging.critical("We failed to reach the download server.")
            logging.debug("Reason: %s" % e.reason)
            click.echo(Tcolors.fail +
                       "We failed to reach the download server." + Tcolors.endc)
        else:
            logging.critical("Error: %s" % e)
            click.echo(Tcolors.fail +
                       "Unexpected error: %s" % e + Tcolors.endc)
    else:
        try:
            file_size = int(r.getheader("Content-Length"))
        except (TypeError, ValueError):
            logging.critical("Filesize has to be an integer!")
            click.echo(Tcolors.fail +
                       "Filesize has to be an integer!" + Tcolors.endc)

        logging.info("Downloading: %s Size: %s KiB" %
                     (file_name, file_size / 1024))
        click.echo("Downloading: %s Size: %s KiB" %
                   (file_name, file_size / 1024))

        block_size = 1024
        progress_bar = tqdm(total=file_size, unit="iB", unit_scale=True)
        with open(file_name_with_ext, "wb") as f:
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
            click.echo(Tcolors.fail +
                       "It looks like something unexpected happened. Aborting!" + Tcolors.endc)


if __name__ == "__main__":
    imdb_download_poster(
        "https://m.media-amazon.com/images/M/MV5BNDU4Mzc3NzE5NV5BMl5BanBnXkFtZTgwMzE1NzI1NzM@._V1_FMjpg_UX1000_.jpg", name="Dunnu")
