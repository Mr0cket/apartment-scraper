from selenium import webdriver

from sites.pararius import ParariusSite
import json

## Configuration for Pararius
with open("config/pararius.json") as f:
    config = json.load(f)

config["message"] = open("config/friendly_english").read()
browser = webdriver.Chrome()  # Replace with the path to your chromedriver executable
print("loading the search page")

pararius = ParariusSite(**config)

pararius.start(browser)
