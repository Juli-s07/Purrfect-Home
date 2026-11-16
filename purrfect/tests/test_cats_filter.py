import pytest

from purrfect.models import Cat
from purrfect.tests.conftest import cat_payload

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize("params, expected", [
    ({"min_price": 300}, 3),
    ({"max_price": 200}, 2),
    ({"status": "reserved"}, 1),
    ({"search": "cat3"}, 1)
])
def test_filter_cats(api_client, cats, params, expected):
    resp = api_client.get("/api/cats/", params)

    assert resp.status_code == 200
    assert resp.data["total"] == expected

@pytest.mark.parametrize("params", [
    {"min_price": "abc"},
    {"page": 0},
    {"sort_by": "unknown"},
])
def test_invalid_filter_cats(api_client, cats, params):
    resp = api_client.get("/api/cats/", params)

    assert resp.status_code == 400

def test_pagination_cats(api_client, cats):
    resp = api_client.get("/api/cats/", {"page": 1, "limit": 2})

    assert len(resp.data["items"]) == 2
    assert resp.data["total"] == 5

def test_sort_cats_by_price_asc(api_client, cats):
    resp = api_client.get("/api/cats/", {"sort_by": "price", "order": "asc"})
    prices = [item["price"] for item in resp.data["items"]]

    assert prices == sorted(prices)
