from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver

import requests

import os, time

rental_types = {"room": 'flat', "apartment": "apartment", "house": "house"}
login_page = "https://www.pararius.com/login-email"

required_cookies = ["PHPSESSID", "ujt_id"]

HEADERS = {
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ApapleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.pararius.com",
}

# open a file with a list of apartments
apartments_file = open("apartments_pararius.csv", "r+")
apartments_applied = apartments_file.read().splitlines()


class ParariusApartment:
    def __init__(self, item):
        title_element = item.find_element(By.CLASS_NAME, "listing-search-item__link--title")
        link = title_element.get_attribute("href")
        self.details_page = title_element.get_attribute("src")

        apartment_img_element = item.find_element(By.CSS_SELECTOR, ".picture__image")
        img_source = apartment_img_element.get_attribute("src")
        self.ID = str(os.path.basename(os.path.dirname(img_source)))

        self.street: str = str(os.path.basename(link)).replace("-", " ").capitalize()
        self.title = title_element.text
        self.apply_page = "https://www.pararius.com/contact/" + self.ID
        self.price = item.find_element(By.CLASS_NAME, "listing-search-item__price").text


class ParariusSite:
    url: str
    location: str
    first_name: str
    last_name: str
    email: str
    phone: str
    message: str

    def __init__(
        self, location, min_rent, max_rent, first_name, last_name, phone, message, email, password, birth_date
    ):

        self.url = "https://www.pararius.com/apartments/" + location + f"/{min_rent}-{max_rent}"
        self.location = location
        self.min_rent = min_rent
        self.max_rent = max_rent
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone = phone
        self.message = message
        self.birth_date = birth_date

    def start(self, browser: webdriver.Chrome):
        cookies = self.login_and_get_cookies(browser)
        properties = self.list_properties(browser)
        self.token = self.retrieve_token(browser, properties[0])

        for property in properties:
            print(f"Applying to property {property.title} on {property.street}...")
            res = requests.post(
                property.apply_page,
                data=self.generate_form_data(property),
                headers=HEADERS,
                cookies=cookies,
                allow_redirects=False,
            )

            if res.status_code == 302:
                print(f"Applied for apartment on {property.street}")
            else:
                print(f"Failed to apply for apartment on {property.street}")

            apartments_file.write("\n" + property.ID)

    ##### Helping methods #####

    def login_and_get_cookies(self, browser):
        required_cookies = ["PHPSESSID", "pararius_session"]

        login_page = "https://www.pararius.com/login-email"
        print(f"navigating to: {login_page}")
        browser.get(login_page)
        element = browser.find_element(By.NAME, "email")
        element.send_keys(self.email)
        element = browser.find_element(By.NAME, "password")
        element.send_keys(self.password)
        element = browser.find_element(By.CLASS_NAME, "button--primary")
        element.click()
        print("logged in")

        cookies = dict()
        for cookie in browser.get_cookies():
            if cookie['name'] in required_cookies:
                cookies[cookie['name']] = cookie['value']

        return cookies

    def retrieve_token(self, browser, apply_page):
        print(f"navigating to: {apply_page} to fetch a token")
        browser.get(apply_page)
        print("Fetching the token...")
        time.sleep(1)
        element = browser.find_element(By.NAME, "contact_agent_huurprofiel_form[_token]")
        return element.get_attribute("value")

    def generate_form_data(self, property):
        message = self.message.replace("{STREET}", property.street).replace("[CITY]", self.location.capitalize())
        return {
            "contact_agent_huurprofiel_form[_token]": self.token,
            "contact_agent_huurprofiel_form[motivation]": message,
            "contact_agent_huurprofiel_form[salutation]": "0",
            "contact_agent_huurprofiel_form[first_name]": self.first_name,
            "contact_agent_huurprofiel_form[last_name]": self.last_name,
            "contact_agent_huurprofiel_form[phone_number]": self.phone,
            "contact_agent_huurprofiel_form[date_of_birth]": self.birth_date,
            "contact_agent_huurprofiel_form[work_situation]": "",
            "contact_agent_huurprofiel_form[gross_annual_household_income]": "",
            "contact_agent_huurprofiel_form[guarantor]": "",
            "contact_agent_huurprofiel_form[preferred_living_situation]": "",
            "contact_agent_huurprofiel_form[number_of_tenants]": "",
            "contact_agent_huurprofiel_form[rent_start_date]": "",
            "contact_agent_huurprofiel_form[preferred_contract_period]": "",
            "contact_agent_huurprofiel_form[current_housing_situation]": "",
        }

    def list_properties(self, browser):
        browser.get(self.url)

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-list")))
        print(f"loaded page: {browser.title}")
        list_items = browser.find_elements(By.CLASS_NAME, "search-list__item--listing")
        properties_list = []
        for item in list_items:
            browser.execute_script("arguments[0].scrollIntoView();", item)
            property = ParariusApartment(item)
            if property.ID in apartments_applied:
                print(f"Already applied to {property.title} on {property.street}")
                continue

            properties_list.append(property)
