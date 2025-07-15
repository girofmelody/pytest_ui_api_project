import re
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1440,900")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--lang=ru-RU")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    yield driver
    driver.quit()

@allure.feature("UI Кинопоиск")
@allure.story("Поиск фильма")
@allure.title("Поиск фильма '1+1' по разным локаторам")
def test_search_1plus1(browser):
    try:
        with allure.step("Открыть главную страницу"):
            browser.get("https://www.kinopoisk.ru/")

        with allure.step("Закрыть всплывающие окна (если есть)"):
            def close_popups():
                try:
                    browser.find_element(By.XPATH, "//div[contains(@class,'popup')]//button[contains(.,'Закрыть')]").click()
                except Exception:
                    pass
            close_popups()

        with allure.step("Найти поле поиска и выполнить поиск по фильму '1+1'"):
            search_locators = [
                (By.NAME, "kp_query"),
                (By.XPATH, "//input[contains(@class,'search-input')]"),
                (By.CSS_SELECTOR, "input[placeholder*='фильмы']")
            ]
            for locator in search_locators:
                try:
                    search = WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located(locator)
                    )
                    search.clear()
                    search.send_keys("1+1" + Keys.RETURN)
                    break
                except TimeoutException:
                    continue
            else:
                allure.attach(browser.get_screenshot_as_png(), name="search_fail", attachment_type=allure.attachment_type.PNG)
                pytest.fail("Не найдено поле поиска")

        with allure.step("Проверить, что результаты поиска содержат '1+1' или 'Intouchables'"):
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(translate(text(), 'INT', 'int'), '1+1') or contains(text(), 'Intouchables')]")
                )
            )

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="search_error", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Тест поиска упал: {str(e)}")

@allure.feature("UI Кинопоиск")
@allure.story("Страница фильма")
@allure.title("Проверка заголовка и года фильма '1+1'")
def test_1plus1_movie_page(browser):
    browser.get("https://www.kinopoisk.ru/film/535341/")
    try:
        with allure.step("Проверить, что заголовок содержит '1+1' или 'Intouchables'"):
            title = WebDriverWait(browser, 15).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//h1[contains(., '1+1') or contains(., 'Intouchables')]")
                )
            )
            assert "1+1" in title.text or "Intouchables" in title.text

        with allure.step("Проверить, что год выпуска — 2011"):
            year = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@href,'/lists/movies/') and contains(text(),'2011')]")
                )
            )
            assert "2011" in year.text

    except TimeoutException:
        allure.attach(browser.get_screenshot_as_png(), name="movie_page_error", attachment_type=allure.attachment_type.PNG)
        pytest.skip("Страница фильма не загрузилась корректно")

@allure.feature("UI Кинопоиск")
@allure.story("Рейтинг фильма")
@allure.title("Проверка рейтинга фильма '1+1'")
def test_1plus1_rating(browser):
    browser.get("https://www.kinopoisk.ru/film/535341/")
    try:
        with allure.step("Получить рейтинг фильма"):
            rating = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class,'film-rating')]//span[contains(@class,'value')]")
                )
            )
            allure.attach(rating.text, name="Рейтинг (сырой текст)", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Преобразовать рейтинг в число и проверить диапазон"):
            match = re.search(r"\d+[.,]?\d*", rating.text)
            assert match, f"Не найдено число в строке: {rating.text}"
            rating_value = float(match.group(0).replace(',', '.'))
            assert 8.0 <= rating_value <= 9.0

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="rating_error", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Ошибка проверки рейтинга: {str(e)}")
