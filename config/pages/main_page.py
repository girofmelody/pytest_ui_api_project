from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage
import allure

class MainPage(BasePage):
    SEARCH_INPUT = (By.NAME, "kp_query")
    SEARCH_RESULTS = (By.CSS_SELECTOR, '[data-tid="d504712e"]')

    @allure.step("Поиск фильма '{query}'")
    def search_movie(self, query):
        search = self.find_visible_element(self.SEARCH_INPUT)
        search.clear()
        search.send_keys(query)
        search.send_keys(Keys.RETURN)
        return self