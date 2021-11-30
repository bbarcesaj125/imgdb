from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tqdm import tqdm
from utils import Tcolors, logger
import logging
import click
import re
import sys
logger("debug")


def imdb_download_poster(url, name=None, filepath=None):
    """ This function downloads a file from a given URL. """

    file_url = url
    url_test = "http://download.thinkbroadband.com/10MB.zip"
    if not filepath:
        naked_file_name = name
        ext = file_url.split(".")[-1]

        special_letters = "àáâäæãåāăąçćčđďèéêëēėęěğǵḧîïíīįìıİłḿñńǹňôöòóœøōõőṕŕřßśšşșťțûüùúūǘůűųẃẍÿýžźż"
        normal_letters = "aaaaaaaaaacccddeeeeeeeegghiiiiiiiilmnnnnoooooooooprrsssssttuuuuuuuuuwxyyzzz"
        regex_special_letters = r"|".join(list(special_letters))
        regex_special_characters = r"[\\~#%&*{}\/:,;<>?!|\"-.\s]{1,}"
        regex_special_letters_test = re.search(
            regex_special_letters, naked_file_name)

        if regex_special_letters_test:
            name_no_special_letters = re.sub(regex_special_letters, lambda reg: list(
                normal_letters)[list(special_letters).index(reg.group())], naked_file_name)
        else:
            name_no_special_letters = naked_file_name

        name_no_special_characters = re.sub(
            regex_special_characters, "_", name_no_special_letters)
        print("No special letters: %s" % name_no_special_letters)
        print("No special chars: %s" % name_no_special_characters)

        file_name = name_no_special_characters + "." + ext
        file_path = file_name
    else:
        file_path = filepath
        file_name = file_url.split("/")[-1]

    try:
        r = urlopen(url)
    except HTTPError as e:
        logging.critical("Download server couldn't fulfill the request.")
        logging.debug("Error code: %s" % e.code)
        click.echo(Tcolors.fail +
                   "Download server couldn't fulfill the request." + Tcolors.endc)
        sys.exit()
    except URLError as e:
        logging.critical("We failed to reach the download server.")
        click.echo(Tcolors.fail +
                   "We failed to reach the download server." + Tcolors.endc)
        if hasattr(e, "reason"):
            logging.debug("Reason: %s" % e.reason)
        sys.exit()

    else:
        try:
            file_size = int(r.getheader("Content-Length"))
        except (TypeError, ValueError):
            logging.critical("Filesize has to be an integer!")
            click.echo(Tcolors.fail +
                       "Filesize has to be an integer!" + Tcolors.endc)
            sys.exit()

        logging.info("Downloading: %s Size: %s KiB" %
                     (file_name, file_size // 1024))
        click.echo(Tcolors.ok_green + "\n➜ Downloading: %s Size: %s KiB\n" %
                   (file_name, file_size // 1024) + Tcolors.endc)

        block_size = 1024
        progress_bar = tqdm(total=file_size, unit="iB", unit_scale=True)
        with open(file_path, "wb") as f:
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
            sys.exit()


if __name__ == "__main__":
    f = imdb_download_poster(
        "https://m.media-amazon.com/images/M/MV5BYjc1ZTFiNGItMzQyYy00OTFlLThjOGYtNzA2NWY1M2E4MTAzXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_FMjpg_UX1000_.jpg", name="Dunnu éla#dopeáj ffrg")
    print(f)
