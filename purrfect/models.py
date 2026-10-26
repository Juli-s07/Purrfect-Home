from django.db import models

class Breeder(models.Model):
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    city = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Breed(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Cat(models.Model):
    class Sex(models.TextChoices):
        MALE = "male"
        FEMALE = "female"

    class Status(models.TextChoices):
        AVAILABLE = "available"
        RESERVED = "reserved"
        SOLD = "sold"

    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=Sex.choices)
    breed = models.ForeignKey(Breed, on_delete=models.PROTECT, related_name="cats")
    breeder = models.ForeignKey(Breeder, on_delete=models.PROTECT, related_name="cats")
    birth_date = models.DateField()
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    photo_url = models.URLField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
