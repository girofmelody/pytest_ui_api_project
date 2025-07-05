import requests

from config.config import TOKEN, BASE_URL

HEADERS = {"X-API-Key": TOKEN}


def search_movie(query, headers=HEADERS, limit=3, select_fields=None, raise_for_status=True):
    """Универсальная функция для отправки поискового запроса к API."""

    params = {"query": query, "limit": limit}
    if select_fields:
        params["selectFields"] = select_fields

    response = requests.get(
        f"{BASE_URL}/search",
        headers=headers,
        params=params
    )

    if raise_for_status:
        response.raise_for_status()
        return response.json()
    else:
        return response