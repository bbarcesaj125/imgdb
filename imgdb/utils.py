import logging
import pickle
import gzip


def logger(loglevel="warning"):
    """ This function serves as a logger. """

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
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

    with gzip.open(filepath_input, "rb") as gz_in:
        with open(filepath_output, "wb") as tsv_out:
            shutil.copyfileobj(gz_in, tsv_out)
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


def pickler(save_pickle_path, save_pickle_input=None):
    """ This function uses the pickle library to serialize or de-serialize an input dictionary. """

    if save_pickle_input:
        with open(save_pickle_path, "wb") as handle:
            pickle.dump(save_pickle_input, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
    else:
        with open(save_pickle_path, "rb") as read_pickle:
            unpickled_output = pickle.load(read_pickle)
            return unpickled_output


if __name__ == "__main__":
    logger()
