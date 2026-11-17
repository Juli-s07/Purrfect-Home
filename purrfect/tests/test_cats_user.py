import pytest

from purrfect.models import Cat
from purrfect.tests.conftest import cat_payload

pytestmark = pytest.mark.django_db

def detail_url(id):
    return f"/api/cats/{id}/"

def test_user_cannot_post_cat(user_client, cat_payload):
    resp = user_client.post("/api/cats/", cat_payload, format="json")

    assert resp.status_code == 403
    assert Cat.objects.count() == 0

def test_user_cannot_update_cat(user_client, cat):
    old_name = cat.name
    resp = user_client.patch(detail_url(cat.pk), {"name": "Murzik"}, format="json")

    assert resp.status_code == 403
    cat.refresh_from_db()
    assert cat.name == old_name

def test_user_cannot_delete_cat(user_client, cat):
    resp = user_client.delete(detail_url(cat.id), format="json")

    assert resp.status_code == 403
    assert Cat.objects.filter(id=cat.id).exists()
