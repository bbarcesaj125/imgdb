import logging


def logger(loglevel="WARNING"):
    """ This function serves as a logger. """

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level, encoding='utf-8',
                        format="%(asctime)s - %(name)s - %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")


if __name__ == "__main__":
    logger()
