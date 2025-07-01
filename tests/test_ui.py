import pytest
import requests
import allure
from typing import Dict, Any

# Конфигурация
BASE_URL = "https://api.kinopoisk.dev/v1.4"
TOKEN = "7ZNT1K6-KY343HV-QJQG6T0-TK2CH15"
HEADERS = {"X-API-Key": TOKEN}

# Фильмы для тестирования
TEST_MOVIES = {
    "forrest_gump": {"id": 448, "name": "Форрест Гамп", "year": 1994, "min_rating": 8.8},
    "green_mile": {"id": 435, "name": "Зеленая миля", "year": 1999, "min_rating": 8.9},
    "inception": {"id": 447301, "name": "Начало", "year": 2010, "min_rating": 8.7}
}


@pytest.fixture(scope="module")
def api_client():
    return KinopoiskAPI()


class KinopoiskAPI:
    @staticmethod
    def search_movie(query: str, params: Dict[str, Any] = None):
        """Поиск фильмов с обработкой ошибок"""
        params = params or {}
        params.update({"query": query, "limit": 5})
        response = requests.get(
            f"{BASE_URL}/movie/search",
            headers=HEADERS,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_movie_by_id(movie_id: int):
        """Получение фильма по ID"""
        response = requests.get(
            f"{BASE_URL}/movie/{movie_id}",
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        return response.json()


@allure.feature("Позитивные тесты API Kinopoisk")
class TestKinopoiskMovies:
    @allure.title("Поиск фильма 'Форрест Гамп'")
    def test_search_forrest_gump(self, api_client):
        movie = TEST_MOVIES["forrest_gump"]
        with allure.step(f"Поиск фильма '{movie['name']}'"):
            data = api_client.search_movie(movie["name"])

        with allure.step("Проверка результатов"):
            assert len(data["docs"]) > 0
            assert any(
                movie["name"].lower() in result["name"].lower()
                for result in data["docs"]
            ), f"Фильм не найден. Результаты: {[m['name'] for m in data['docs']]}"

    @allure.title("Проверка данных фильма 'Зеленая миля'")
    def test_get_green_mile(self, api_client):
        movie = TEST_MOVIES["green_mile"]
        with allure.step(f"Запрос фильма по ID {movie['id']}"):
            result = api_client.get_movie_by_id(movie["id"])

        with allure.step("Проверка данных"):
            assert result["name"] == movie["name"]
            assert result["year"] == movie["year"]
            assert result["rating"]["kp"] >= movie["min_rating"]

    @allure.title("Поиск фильма 'Начало' (Inception)")
    def test_search_inception(self, api_client):
        movie = TEST_MOVIES["inception"]
        with allure.step("Поиск по русскому и английскому названию"):
            data_ru = api_client.search_movie(movie["name"])
            data_en = api_client.search_movie("Inception")

        with allure.step("Проверка результатов"):
            for data in [data_ru, data_en]:
                assert len(data["docs"]) > 0
                assert any(
                    movie["name"].lower() in result["name"].lower() or
                    "inception" in result["name"].lower()
                    for result in data["docs"]
                ), f"Фильм не найден в результатах: {[m['name'] for m in data['docs']]}"


@allure.feature("Негативные тесты")
class TestNegativeCases:
    @allure.title("Поиск несуществующего фильма")
    def test_search_nonexistent_movie(self, api_client):
        with allure.step("Поиск случайной строки"):
            data = api_client.search_movie("RandomMovie12345!@#$")

        with allure.step("Проверка пустых результатов"):
            assert len(data["docs"]) == 0

    @allure.title("Запрос с неверным токеном")
    def test_invalid_token(self):
        with allure.step("Запрос с невалидным токеном"):
            response = requests.get(
                f"{BASE_URL}/movie/search",
                headers={"X-API-Key": "invalid_token_123"},
                params={"query": "Зеленая миля"},
                timeout=10
            )

        with allure.step("Проверка ошибки авторизации"):
            assert response.status_code == 401
            assert "Unauthorized" in response.text

    @allure.title("Запрос невалидного ID фильма")
    def test_invalid_movie_id(self):
        with allure.step("Запрос несуществующего ID"):
            response = requests.get(
                f"{BASE_URL}/movie/999999999",
                headers=HEADERS,
                timeout=10
            )

        with allure.step("Проверка ошибки"):
            # API возвращает 400 для невалидных ID, а не 404
            assert response.status_code == 400
            assert "Bad Request" in response.text