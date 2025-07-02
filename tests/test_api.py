import requests
import allure
from config.config import BASE_URL, HEADERS

# Позитивные тесты
@allure.feature("Позитивные тесты")
def test_cyrillic_search():
    """Поиск фильма на кириллице"""
    response = requests.get(
        f"{BASE_URL}/search",
        headers=HEADERS,
        params={
            "query": "Головоломка",
            "limit": 3,
            "selectFields": ["name", "alternativeName"]
        }
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data["docs"]) > 0
    assert any(
        "головоломка" in movie["name"].lower() or
        (movie.get("alternativeName") and
         "puzzle" in movie["alternativeName"].lower())
        for movie in data["docs"]
    ), f"Не найдено в результатах: {[m['name'] for m in data['docs']]}"


def test_latin_search():
    """Поиск фильма на латинице с учетом локализации"""
    response = requests.get(
        f"{BASE_URL}/search",
        headers=HEADERS,
        params={
            "query": "Inception",
            "limit": 5,
            "selectFields": ["name", "alternativeName"]
        }
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data["docs"]) > 0

    found = any(
        ("inception" in movie["name"].lower() or
         (movie.get("alternativeName") and
          "inception" in movie["alternativeName"].lower()))
        for movie in data["docs"]
    )

    assert found, (
        f"Не найдено 'Inception' ни в названии, ни в альтернативном. "
        f"Результаты: {[{m['name']: m.get('alternativeName')} for m in data['docs']]}"
    )


def test_numeric_search():
    """Поиск фильма с цифрами в названии"""
    response = requests.get(
        f"{BASE_URL}/search",
        headers=HEADERS,
        params={
            "query": "1+1",
            "limit": 3,
            "selectFields": ["name"]
        }
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data["docs"]) > 0
    assert any(
        movie["name"] in ["1+1", "Один плюс один", "Intouchables"]
        for movie in data["docs"]
    ), f"Не найдено в результатах: {[m['name'] for m in data['docs']]}"


# Негативные тесты
@allure.feature("Негативные тесты")
def test_no_token():
    """Попытка поиска без токена"""
    response = requests.get(
        f"{BASE_URL}/search",
        params={"query": "Титаник"}
    )
    assert response.status_code == 401
    assert "Unauthorized" in response.text


def test_invalid_token():
    """Попытка поиска с неверным токеном"""
    response = requests.get(
        f"{BASE_URL}/search",
        headers={"X-API-Key": "invalid_token_123"},
        params={"query": "Матрица"}
    )
    assert response.status_code == 401


def test_wrong_method():
    """Использование неверного типа запроса"""
    response = requests.put(
        f"{BASE_URL}/search",
        headers=HEADERS
    )
    assert response.status_code == 404