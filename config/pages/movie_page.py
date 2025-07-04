from .base_page import BasePage
from selenium.webdriver.common.by import By
import allure

class MoviePage(BasePage):
    # Локаторы
    AWARDS_TAB = (By.CSS_SELECTOR, 'a[href*="/awards"]')
    REVIEWS_TAB = (By.CSS_SELECTOR, 'a[href*="/reviews"]')
    AWARDS_HEADER = (By.CSS_SELECTOR, 'h1 > a[href="/awards/"]')
    ADD_REVIEW_BUTTON = (By.CSS_SELECTOR, "a.formReviewAncor:nth-of-type(2)")

    @allure.step("Открыть вкладку 'Награды'")
    def open_awards_tab(self):
        self.click_element(self.AWARDS_TAB)
        return self

    @allure.step("Открыть вкладку 'Рецензии'")
    def open_reviews_tab(self):
        self.click_element(self.REVIEWS_TAB)
        return self

    @allure.step("Проверить заголовок 'Награды'")
    def verify_awards_header(self):
        assert "Награды" in self.get_element_text(self.AWARDS_HEADER)

    @allure.step("Проверить кнопку 'Добавить рецензию'")
    def verify_review_button(self):
        assert "Добавить рецензию" in self.get_element_text(self.ADD_REVIEW_BUTTON)