from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import allure

class BasePage:
    def __init__(self, browser, timeout=10):
        self.browser = browser
        self.wait = WebDriverWait(browser, timeout)

    @allure.step("Открыть страницу {url}")
    def open(self, url):
        self.browser.get(url)

    @allure.step("Найти видимый элемент {locator}")
    def find_visible_element(self, locator):
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            self._take_screenshot(f"element_not_found_{locator[1]}")
            raise AssertionError(f"Элемент не найден: {locator}")

    @allure.step("Получить текст элемента {locator}")
    def get_element_text(self, locator):
        return self.find_visible_element(locator).text

    @allure.step("Кликнуть по элементу {locator}")
    def click_element(self, locator):
        self.find_visible_element(locator).click()

    def _take_screenshot(self, name):
        allure.attach(
            self.browser.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        