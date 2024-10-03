import csv, requests, os, time
from bs4 import BeautifulSoup
from selenium import webdriver

from sites.pararius import ParariusSite

## Configuration for Pararius
config = {
    "location": "utrecht",
    "min_rent": 1200,
    "max_rent": 1900,
    # "min_rooms": 2,
    # "max_rooms": 3,
    "first_name": "Milo",
    "last_name": "Silva",
    "email": "milo.silva234@gmail.com",
    "phone": "0613867911",
}

# open a file with a list of apartments
apartments_file = open("apartments_pararius.csv", "r+")
apartments_applied = apartments_file.read().splitlines()


# Find the creation date for the listing


browser = webdriver.Chrome()  # Replace with the path to your chromedriver executable
print("loading the search page")

pararius = ParariusSite(**config)

pararius.start(browser)
