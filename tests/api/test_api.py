import allure
import requests

from config.api_client import search_movie, BASE_URL, HEADERS


@allure.feature("Позитивные тесты")
def test_cyrillic_search():
    """Поиск фильма на кириллице"""
    data = search_movie("Головоломка", limit=3, select_fields=["name", "alternativeName"])

    assert len(data["docs"]) > 0
    assert any(
        "головоломка" in movie["name"].lower() or
        (movie.get("alternativeName") and "puzzle" in movie["alternativeName"].lower())
        for movie in data["docs"]
    ), f"Не найдено в результатах: {[m['name'] for m in data['docs']]}"


def test_latin_search():
    """Поиск фильма на латинице с учетом локализации"""
    data = search_movie("Inception", limit=5, select_fields=["name", "alternativeName"])

    assert len(data["docs"]) > 0
    found = any(
        "inception" in movie.get("name", "").lower() or
        (movie.get("alternativeName") and "inception" in movie["alternativeName"].lower())
        for movie in data["docs"]
    )
    assert found, (
        f"Не найдено 'Inception' ни в названии, ни в альтернативном. "
        f"Результаты: {[{m['name']: m.get('alternativeName')} for m in data['docs']]}"
    )


def test_numeric_search():
    """Поиск фильма с цифрами в названии"""
    data = search_movie("1+1", limit=3, select_fields=["name"])

    assert len(data["docs"]) > 0
    assert any(
        movie["name"] in ["1+1", "Один плюс один", "Intouchables"]
        for movie in data["docs"]
    ), f"Не найдено в результатах: {[m['name'] for m in data['docs']]}"


@allure.feature("Негативные тесты")
def test_no_token():
    """Попытка поиска без токена"""
    response = search_movie("Титаник", headers={}, raise_for_status=False)

    assert response.status_code == 401
    assert "Unauthorized" in response.text


def test_invalid_token():
    """Попытка поиска с неверным токеном"""
    response = search_movie(
        "Матрица",
        headers={"X-API-Key": "invalid_token_123"},
        raise_for_status=False
    )
    assert response.status_code == 401


def test_wrong_method():
    """Использование неверного типа запроса (PUT вместо GET)"""
    response = requests.put(
        f"{BASE_URL}/search",
        headers=HEADERS
    )
    assert response.status_code == 404
