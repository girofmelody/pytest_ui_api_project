import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.config import INTOUCH_URL, UP_URL
import allure

@allure.feature("UI Тесты Кинопоиска")
class TestKinopoiskUI:
    @allure.title("Проверка заголовка страницы")
    def test_title_contains_kinopoisk(self, main_page):
        assert "Кинопоиск" in main_page.browser.title

    @allure.title("Поиск фильма 'Головоломка'")
    def test_search_movie(self, main_page):
        (main_page
         .search_movie("Головоломка")
         .verify_search_results_contain("Головоломка"))

    @allure.title("Проверка вкладки 'Награды'")
    def test_open_awards_tab(self, movie_page):
        movie_page.open(INTOUCH_URL)
        (movie_page
         .open_awards_tab()
         .verify_awards_header())

    @allure.title("Проверка вкладки 'Рецензии'")
    def test_open_reviews_page(self, movie_page):
        movie_page.open(UP_URL)
        (movie_page
         .open_reviews_tab()
         .verify_review_button())