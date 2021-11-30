import logging
import pickle
import gzip
import shutil
import click
import sys


def logger(loglevel="warning"):
    """ This function serves as a logger. """

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        click.echo(Tcolors.warning + "Invalid log level: %s. Using 'warning' as a fallback!" %
                   loglevel + Tcolors.endc)
        numeric_level = 30
    logging.basicConfig(
        level=numeric_level, format="%(asctime)s - %(name)s - %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")


class Tcolors:
    """ A set of ANSI colors. """

    header = "\033[95m"
    ok_blue = "\033[94m"
    ok_cyan = "\033[96m"
    ok_green = "\033[92m"
    warning = "\033[93m"
    fail = "\033[91m"
    endc = "\033[0m"
    bold = "\033[1m"
    underline = "\033[4m"


def unzip(filepath_input, filepath_output):
    """ This function uses gzip to unpack a gzipped file. """

    try:
        with gzip.open(filepath_input, "rb") as gz_in:
            with open(filepath_output, "wb") as tsv_out:
                shutil.copyfileobj(gz_in, tsv_out)
    except Exception as e:
        logging.critical(
            "Something went wrong while trying to open the gzipped files!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.fail +
                   "Something went wrong while trying to open the gzipped files!" + Tcolors.endc)
        sys.exit()

    try:
        filepath_input.unlink()
    except FileNotFoundError:
        logging.warning(
            "Couldn't delete %s: The file doesn't exist!" % filepath_input)
    except Exception as e:
        logging.critical(
            "Something went wrong while trying to delete the gzipped files!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.fail +
                   "Something went wrong while trying to delete the gzipped files!" + Tcolors.endc)
        sys.exit()


def pickler(save_pickle_path, save_pickle_input=None):
    """ This function uses the pickle library to serialize or de-serialize an input dictionary. """

    if save_pickle_input:
        try:
            with open(save_pickle_path, "wb") as handle:
                pickle.dump(save_pickle_input, handle,
                            protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logging.critical(
                "Something went wrong while trying to save the program's state!")
            logging.debug("Error: %s" % e)
            click.echo(Tcolors.fail +
                       "Something went wrong while trying to save the program's state!" + Tcolors.endc)
    else:
        try:
            with open(save_pickle_path, "rb") as read_pickle:
                unpickled_output = pickle.load(read_pickle)
                return unpickled_output
        except Exception as e:
            logging.critical(
                "Something went wrong while trying to read the program's state!")
            logging.debug("Error: %s" % e)
            click.echo(Tcolors.fail +
                       "Something went wrong while trying to read the program's state!" + Tcolors.endc)
            sys.exit()


def replace_every_nth(nth, pattern, drop, string):
    """ This function replaces every nth character in a string with a pre-defined text or character (drop). """

    string_to_list = list(string)
    cursor = 0
    for idx in range(len(string_to_list)):
        if string_to_list[idx] == pattern:
            if len(string_to_list[cursor:idx]) >= nth:
                string_to_list.insert(idx+1, drop + "             ")
                cursor = idx

    list_to_string = "".join(string_to_list)
    return list_to_string


if __name__ == "__main__":
    string = "True Detective: Created by Nic Pizzolatto. With Matthew McConaughey, Colin Farrell, Mahershala Ali, Woody Harrelson. Seasonal anthology series in which police investigations unearth the personal and professional secrets of those involved, both within and outside the law."
    s = replace_every_nth(50, " ", "\n", string)
    print(s)
