import logging


def logger(loglevel="warning"):
    """ This function serves as a logger. """

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(
        level=numeric_level, format="%(asctime)s - %(name)s - %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    print("Num level: ", numeric_level)


if __name__ == "__main__":
    logger()
