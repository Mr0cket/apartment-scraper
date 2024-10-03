from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from dataclasses import dataclass

import os, time


class ParariusApartment:
    def __init__(self, item, location):
        title_element = item.find_element(By.CLASS_NAME, "listing-search-item__link--title")

        link = title_element.get_attribute("href")
        self.details_page = link

        self.ID = str(os.path.basename(os.path.dirname(link)))
        self.street = str(os.path.basename(link)).replace("-", " ").capitalize()
        self.title = title_element.text
        self.apply_page = "https://www.pararius.com/contact/" + self.ID + "/" + location + "/hausing/plan-a-viewing"
        # self.subtitle = item.find_element(By.CLASS_NAME, "listing-search-item__sub-title").text
        self.price = item.find_element(By.CLASS_NAME, "listing-search-item__price").text


class ParariusSite:
    url: str
    description: str
    location: str
    first_name: str
    last_name: str
    email: str
    phone: str

    def __init__(
        self,
        location,
        min_rent,
        max_rent,
        first_name,
        last_name,
        email,
        phone,
    ):

        self.url = "https://www.pararius.com/apartments/" + location + f"/{min_rent}-{max_rent}"
        self.location = location
        self.min_rent = min_rent
        self.max_rent = max_rent
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone

    def start(self, browser):
        browser.get(self.url)

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-list")))
        print(f"loaded page: {browser.title}")

        list_items = browser.find_elements(By.CLASS_NAME, "search-list__item--listing")
        properties_list = []
        for item in list_items:
            # Fetch the details of the application
            property = ParariusApartment(item, self.location)
            properties_list.append(property)

        for property in properties_list:
            print(property.title)
            print(property.details_page)
            print(property.ID)

            # Ignore properties which have already been applied to
            # if property.ID in apartments_applied:
            #     print(f"{property.ID} has already been applied to")
            #     continue

            # Navigate to apply page
            print(f"navigating to: {property.apply_page}")
            browser.get(property.apply_page)

            # Fill in application form with generic template

            # Apply to the page

            # Fill in the description
            print("Filling in the description...")
            time.sleep(10)
            element = browser.find_element(By.CLASS_NAME, "text-control__control")
            element.send_keys(Keys.TAB)
            element.send_keys(
                self.description.replace("{STREET}", property.street).replace("[CITY]", self.location.capitalize())
            )

            # check all check-boxes
            print("checking all boxes...")
            elements = browser.find_elements(By.CLASS_NAME, "checkbox-control__control")
            action = ActionChains(browser)

            for e in elements:
                action.move_to_element(e)
                browser.execute_script("arguments[0].click();", e)

            # Fill in personal information
            print("Filling in personal information...")
            element = browser.find_element(By.NAME, "listing_contact_agent_form[first_name]")
            element.send_keys(self.first_name)

            element = browser.find_element(By.NAME, "listing_contact_agent_form[last_name]")
            element.send_keys(self.last_name)

            element = browser.find_element(By.NAME, "listing_contact_agent_form[email]")
            element.send_keys(self.email)

            element = browser.find_element(By.NAME, "listing_contact_agent_form[phone]")
            element.send_keys(self.phone)
            time.sleep(2)

            # Click apply button
            print("clicking send...")
            apply_btn = browser.find_element(By.CLASS_NAME, "form__button--submit")
            if apply_btn is not None:
                print("Apply button exists & is clickable")
                time.sleep(2)
            apply_btn.click()
            print(f"Applied for apartment on {property.street}")
            # apartments_file.write("\n" + property.ID)
            time.sleep(5)
