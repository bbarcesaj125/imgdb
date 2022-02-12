# Imgdb - a command line IMDb front-end
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

The application make use of the freely available [IMDb datasets](https://www.imdb.com/interfaces/)**
to extract the required information (e.g, genres, title, rating etc). 
To achieve that, `Imgdb` also uses `Google Custom Search API` to make
sure the entered title is exactly what the user is looking for.