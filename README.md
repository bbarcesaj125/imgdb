# Imgdb - a command line IMDb search app
[![GitHub release](https://img.shields.io/github/v/release/bbarcesaj125/imgdb.svg)](https://github.com/bbarcesaj125/imgdb/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Repository Size](https://img.shields.io/github/repo-size/bbarcesaj125/imgdb)

<p align="center">
	<img width="200" src="/art/imgdb_logo.png" alt="Imgdb Logo">
</p>

This is a Python command line application that allows the user to get 
IMDb information about a particular title as well as downloading its
corresponding poster.

## Introduction
The idea behind `Imgdb` is to create a simple command line application that
fetches information about a specific title (e.g., movie or series) from IMDb
as well as RottenTomatoes.

The application makes use of the freely available **[IMDb datasets](https://www.imdb.com/interfaces/)**
to extract the required information (e.g., genres, title, rating, etc). 
To achieve that, `Imgdb` also uses `Google Custom Search API` to make
sure the entered title is exactly what the user is looking for.

`Imgdb` is also capable of doing some fancy stuff by using `ImageMagick` to
generate an image containing the movie's or series' ratings like so:

<p align="center">
	<img width="500" src="/art/Captain_America_Civil_War_by_imgdb.png" alt="Captain America: Civil War Poster">
</p>

## Requirements
### Python dependencies

- beautifulsoup4
- click
- pandas
- PyYAML
- tqdm
- Wand

### System dependencies

- ImageMagick

## Installation
The easiest way to install `Imgdb` is to use `Pip`:

    pip install imgdb

## Configuration
The application is configured using a `Yaml` configuration file that resides
in your `XDG_CONFIG_HOME` directory. After running the application for the first
time, it will create an initial configuration file (`imgdb.yaml`) in the
`$HOME/.config/imgdb` directory.

The `imgdb.yaml` file should have the following structure:

    general:
        download: true | false
        image editing: true | false
        font: <font name>
        log file path: <path/to/log/file.log>
        update frequency: daily | weekly | bi-weekly | 1d (for 1 day) | 1h (for 1 hour) | etc
    interface:
        api:
            google search api key: <google API key>
            imdb custom search id: <custom IMDb search engine ID>

You can refer to [`imgdb_config_template.yaml`](/imgdb_config_template.yaml) for an example 
configuration file.

## Usage

    Usage: imgdb [OPTIONS]

    Options:
        --mov TEXT      The title of the movie.
        --tv TEXT       The title of the series.
        --tvmini TEXT   The title of the mini series.
        --debug TEXT    The logging level of the application.
        --logfile TEXT  The path of the log file.
        --freq TEXT     The update frequency of the datasets.
        --font TEXT     The font used to generate the rating image.
        -d              Download the movie's poster image.
        -e              Save the edited image containing the movie's ratings.
        --help          Show this message and exit.

When you run the application for the first time, it will attempt to download
the required IMDb datasets from [imdb.com/interfaces/](https://www.imdb.com/interfaces/). 
You can think of them as daily snapshot of the huge IMDb database.
The application needs these datasets in order to extract and display information
about a specific movie or series.
I opted for this solution because almost all the information are extracted
from the datasets stored on the user's computer. 
This makes the application more reliable as opposed to scraping for example.

These datasets are updated on a weekly basis by default. However, you can
always change the update frequency by using the `--freq` option as documented above.
In most cases, you don't really need to update them very frequently. A `weekly` or
even a `bi-weekly` update interval should suffice. 
