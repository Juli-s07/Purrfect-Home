from django.utils import timezone

from rest_framework import serializers
from .models import Breed, Breeder, Cat

class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ["id", "name"]


class BreederShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breeder
        fields = ["id", "name", "country", "city"]

class CatQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False)
    breed_id = serializers.IntegerField(required=False)
    breeder_id = serializers.IntegerField(required=False)
    country = serializers.CharField(required=False)
    min_price = serializers.IntegerField(required=False, min_value=0)
    max_price = serializers.IntegerField(required=False, min_value=0)
    min_age = serializers.IntegerField(required=False, min_value=0)
    max_age = serializers.IntegerField(required=False, min_value=0)
    status = serializers.ChoiceField(choices=["available", "reserved", "sold"], required=False)
    sort_by = serializers.ChoiceField(choices=["price", "age", "created_at"], default="created_at")
    order = serializers.ChoiceField(choices=["asc", "desc"], default="desc")
    page = serializers.IntegerField(min_value=1, default=1)
    limit = serializers.IntegerField(min_value=1, max_value=100, default=10)

    def validate(self, attrs):
        if "min_price" in attrs and "max_price" in attrs and attrs["min_price"] > attrs["max_price"]:
            raise serializers.ValidationError("min_price cannot be greater than max_price")
        if "min_age" in attrs and "max_age" in attrs and attrs["min_age"] > attrs["max_age"]:
            raise serializers.ValidationError("min_age cannot be greater than max_age")
        return attrs

class CatSerializer(serializers.ModelSerializer):
    breed = BreedSerializer(read_only=True)
    breeder = BreederShortSerializer(read_only=True)
    breed_id = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(), source="breed", write_only=True)
    breeder_id = serializers.PrimaryKeyRelatedField(
        queryset=Breeder.objects.all(), source="breeder", write_only=True)
    class Meta:
        model = Cat
        fields = ["id", "name", "sex", "breed", "breeder", "breed_id", "breeder_id",
              "birth_date", "price", "description", "status", "photo_url", "created_at"]
        read_only_fields = ["created_at"]

    def validate_birth_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Birth date cannot be in the future")
        return value

class CatShortSerializer(serializers.ModelSerializer):
    breed = BreedSerializer(read_only=True)

    class Meta:
        model = Cat
        fields = ["id", "name", "sex", "breed", "price", "status", "photo_url"]

class BreederSerializer(serializers.ModelSerializer):
    cats = CatShortSerializer(many=True, read_only=True)
    class Meta:
        model = Breeder
        fields = ["id", "name", "country", "city", "phone", "email", "description", "cats"]
