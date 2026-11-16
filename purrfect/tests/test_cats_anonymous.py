import pytest

from purrfect.models import Cat
from purrfect.tests.conftest import cat_payload

pytestmark = pytest.mark.django_db

def detail_url(id):
    return f"/api/cats/{id}/"

def test_anonymous_can_get_list_cats(api_client, cats):
    resp = api_client.get("/api/cats/")

    assert resp.status_code == 200
    assert resp.data["total"] == 5

def test_anonymous_can_get_detail_cat(api_client, cat):
    resp = api_client.get(detail_url(cat.pk))

    assert resp.status_code == 200
    assert resp.data["name"] == cat.name

def test_anonymous_can_get_not_found(api_client, cat):
    resp = api_client.get(detail_url(99999))

    assert resp.status_code == 404

def test_anonymous_cannot_post_cat(api_client, cat_payload):
    resp = api_client.post("/api/cats/", cat_payload, format="json")

    assert resp.status_code == 401
    assert Cat.objects.count() == 0

def test_anonymous_cannot_update_cat(api_client, cat):
    old_name = cat.name
    resp = api_client.patch(detail_url(cat.pk), {"name": "Murzik"}, format="json")

    assert resp.status_code == 401
    cat.refresh_from_db()
    assert cat.name == old_name

def test_anonymous_cannot_delete_cat(api_client, cat):
    resp = api_client.delete(detail_url(cat.id), format="json")

    assert resp.status_code == 401
    assert Cat.objects.filter(id=cat.id).exists()
