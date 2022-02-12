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
to extract the required information (e.g, genres, title, rating, etc). 
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
time, it will create an initial configuration file (`imgdb.yaml`) in `$HOME/.config/imgdb`.



