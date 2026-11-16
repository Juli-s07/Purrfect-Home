import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from purrfect.models import Cat, Breed, Breeder
import datetime

User = get_user_model()

@pytest.fixture
def api_client() -> APIClient: # анонім
    return APIClient()

@pytest.fixture
def user(db) -> User: #користувач
    return User.objects.create_user(
        username = "test_user",
        password = "bAC78bge",
        email = "test@gmail.com",
    )

@pytest.fixture
def admin(db) -> User: #адмін is_staff
    return User.objects.create_user(
        username = "admin",
        password = "1234",
        email = "admin@gmail.com",
        is_staff = True,
    )

@pytest.fixture
def user_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def admin_client(admin) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def breed(db) -> Breed:
    return Breed.objects.create(name="Scottish fold")

@pytest.fixture
def breeder(db) -> Breeder:
    return Breeder.objects.create(
        name="Julia",
        country="Ukraine",
        phone="+380950028011",
        email="julia@gmail.com",)

@pytest.fixture
def another_breeder(db) -> Breeder:
    return Breeder.objects.create(
        name="Jan",
        country="Poland",
        phone="+48123456789",
        email="jan@gmail.com",
    )

@pytest.fixture
def cat(db, breed, breeder) -> Cat:
    return Cat.objects.create(
        name="Murka",
        sex = Cat.Sex.FEMALE,
        breed=breed,
        breeder=breeder,
        birth_date=datetime.date(2025, 1, 1),
        price=15000,
        photo_url="https://example.com/murka.jpg",
    )

@pytest.fixture
def cats(db, breed, breeder) -> list[Cat]:
    statuses = [Cat.Status.AVAILABLE, Cat.Status.AVAILABLE, Cat.Status.RESERVED,
                Cat.Status.SOLD, Cat.Status.AVAILABLE]
    return [
        Cat.objects.create(
            name=f"Cat{i}",
            sex=Cat.Sex.MALE,
            breed=breed,
            breeder=breeder,
            birth_date=datetime.date(2024, 1, i),
            price=i * 100,
            photo_url=f"https://example.com/{i}.jpg",
            status=statuses[i - 1],
        )
        for i in range(1, 6)
    ]

@pytest.fixture
def cat_payload(breed, breeder) -> dict: # заповнений словник для POST
    return {
        "name": "Barsik",
        "sex": "male",
        "breed_id": breed.id,
        "breeder_id": breeder.id,
        "birth_date": "2024-03-10",
        "price": 200,
        "photo_url": "https://example.com/barsik.jpg",
    }
