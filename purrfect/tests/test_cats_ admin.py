import pytest

from purrfect.models import Cat
from purrfect.tests.conftest import cat_payload

pytestmark = pytest.mark.django_db

def detail_url(id):
    return f"/api/cats/{id}/"

def test_admin_can_post_cat(admin_client, cat_payload):
    resp = admin_client.post("/api/cats/", cat_payload, format="json")
    assert resp.status_code == 201

@pytest.mark.parametrize("field, value", [
    ("price", -1),
    ("sex", "unknown"),
    ("breed_id", 99999),
    ("breeder_id",  99999),
    ("status", "unknown")
])
def test_admin_cannot_post_invalid_cat(admin_client, cat_payload, field, value):
    cat_payload[field] = value
    resp = admin_client.post("/api/cats/", cat_payload, format="json")

    assert resp.status_code == 400
    assert Cat.objects.count() == 0

def test_admin_can_update_cat(admin_client, cat):
    resp = admin_client.patch(detail_url(cat.id), {"price": 777}, format="json")

    assert resp.status_code == 200
    cat.refresh_from_db()
    assert cat.price == 777

def test_admin_cannot_update_invalid_cat(admin_client, cat):
    old_price = cat.price
    resp = admin_client.patch(detail_url(cat.id), {"price": -1}, format="json")

    assert resp.status_code == 400
    cat.refresh_from_db()
    assert cat.price == old_price

def test_admin_can_delete_cat(admin_client, cat):
    resp = admin_client.delete(detail_url(cat.id))

    assert resp.status_code == 204
    assert not Cat.objects.filter(id=cat.id).exists()

def test_admin_cannot_delete_not_found_cat(admin_client, cat):
    resp = admin_client.delete(detail_url(99999))

    assert resp.status_code == 404
