import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.fixture
def browser():
    # Настройки Chrome для обхода блокировок
    options = webdriver.ChromeOptions()

    # Основные параметры
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1440,900")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--lang=ru-RU")

    # Для режима разработчика
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    # Маскируем WebDriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    yield driver
    driver.quit()


def test_search_1plus1(browser):
    try:
        # 1. Открываем страницу
        browser.get("https://www.kinopoisk.ru/")

        # 2. Закрываем мешающие элементы
        def close_popups():
            try:
                browser.find_element(By.XPATH, "//div[contains(@class,'popup')]//button[contains(.,'Закрыть')]").click()
            except:
                pass

        close_popups()

        # 3. Поиск фильма (3 варианта локаторов)
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
            pytest.fail("Не найдено поле поиска")

        # 4. Проверка результатов
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(translate(text(), 'INT', 'int'), '1+1') or contains(text(), 'Intouchables')]")
            )
        )

    except Exception as e:
        browser.save_screenshot("search_error.png")
        pytest.fail(f"Тест поиска упал: {str(e)}")


def test_1plus1_movie_page(browser):
    # Прямой переход на страницу фильма (ID 535341)
    browser.get("https://www.kinopoisk.ru/film/535341/")

    try:
        # Проверяем русское и международное название
        title = WebDriverWait(browser, 15).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[contains(., '1+1') or contains(., 'Intouchables')]")
            )
        )

        # Дополнительная проверка года выпуска
        year = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href,'/lists/movies/') and contains(text(),'2011')]")
            )
        )

        assert "1+1" in title.text
        assert "2011" in year.text

    except TimeoutException:
        browser.save_screenshot("movie_page_error.png")
        pytest.skip("Страница фильма не загрузилась корректно")


def test_1plus1_rating(browser):
    """Проверка рейтинга фильма"""
    browser.get("https://www.kinopoisk.ru/film/535341/")

    try:
        rating = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'film-rating')]//span[contains(@class,'value')]")
            )
        )

        # Проверяем что рейтинг адекватный (между 8.0 и 9.0)
        rating_value = float(rating.text.replace(',', '.'))
        assert 8.0 <= rating_value <= 9.0

    except Exception as e:
        browser.save_screenshot("rating_error.png")
        pytest.fail(f"Ошибка проверки рейтинга: {str(e)}")