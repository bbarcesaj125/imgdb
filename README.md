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

`Imgdb` is a play on the **IMDb** acronym. Since the application can also
download movie posters, I added the **g** to **IMDb** to get a name that is
both closer to **IMDb** while also representing one of the main application's 
functionalities at the same time.
The idea behind `Imgdb` is to create a simple command line application that
fetches information about a specific title (e.g., a movie or series) from IMDb
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

In order to use the image editing option, you should have `ImageMagick` installed on you system.
Please, use your distribution's package manager to install it.

## Installation
The easiest way to install `Imgdb` is to use `pip`:

    pip install imgdb

## Configuration
The application is configured using a `yaml` configuration file that resides
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
the required IMDb datasets from [imdb.com/interfaces](https://www.imdb.com/interfaces/). 
You can think of them as daily snapshot of the huge IMDb database.
The application needs these datasets in order to extract and display information
about a specific movie or series.
I opted for this solution because it allows `Imgdb` to fetch almost all the information
from the datasets that are stored on the user's computer. 
This makes the application more reliable as opposed to scraping for example.

These datasets are updated on a weekly basis by default. However, you can
always change the update frequency by using the `--freq` option as documented above.
In most cases, you don't really need to update them very frequently. A `weekly` or
even a `bi-weekly` update interval should suffice. 

To use the application, you also need a Google API key as well as an IMDb custom search
ID.
You can refer to the relevant [Google documentation](https://cloud.google.com/docs/authentication/api-keys)
for more information on how to get and use an API key.
For creating an IMDb custom search engine, you can refer to this
[link](https://developers.google.com/custom-search/docs/tutorial/creatingcse).

Once you have set up the application properly, you can invoke it like so:

    imgdb --mov "The Dark Knight" -de

The above command will display the following information in your terminal:

    Title: The Dark Knight
    Genres: Action, Crime, Drama
    Year: 2008
    Runtime: 152 min
    IMDb Rating: 9.0
    RottenTomatoes Rating: 94
    Description: The Dark Knight: Directed by Christopher Nolan. With 
                Christian Bale, Heath Ledger, Aaron Eckhart, Michael 
                Caine. When the menace known as the Joker wreaks havoc 
                and chaos on the people of Gotham, Batman must accept 
                one of the greatest psychological and physical tests 
                of his ability to fight injustice.
    ➜ Downloading: The_Dark_Knight.jpg - Size: 274 KiB

    100%|██████████████████████████████████| 281k/281k [00:00<00:00, 3.15MiB/s]
    Edited image saved as: The_Dark_Knight_by_imgdb.png

It will also download the movie's poster (`The_Dark_Knight.jpg`) and save it in the current directory.
The `The_Dark_Knight_by_imgdb.png` saved image will look something like this:

<p align="center">
	<img width="500" src="/art/The_Dark_Knight_by_imgdb.png" alt="Imgdb Logo">
</p>

For optimal results, you should use a good design font like **Maler** which is
the default font of the application used in the image above.

## TODO

- [ ] Add multi-result search option
- [ ] Add API-less search option