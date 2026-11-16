from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ConflictError
from .models import Cat, Breed, Breeder
from .serializers import CatSerializer, CatShortSerializer, CatListResponseSerializer, BreedSerializer, BreederSerializer, BreederShortSerializer, \
    CatQuerySerializer

from .permissions import IsAdminOrReadOnly

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


def is_duplicate(errors, field):
    return any(error.code == "unique" for error in errors.get(field, []))

class CatListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        tags=["Cats"],
        summary="Get a list of cats",
        description="Public endpoint. Return cats with filtering, sorting, pagination.",
        parameters=[CatQuerySerializer],
        responses={
            200: CatListResponseSerializer,
            400: OpenApiResponse(description="Invalid data"),
        },
    )
    def get(self, request):
        query = CatQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        p = query.validated_data

        cats = Cat.objects.all()

        if "search" in p:
            cats = cats.filter(name__icontains=p["search"])
        if "breed_id" in p:
            cats = cats.filter(breed_id=p["breed_id"])
        if "breeder_id" in p:
            cats = cats.filter(breeder_id=p["breeder_id"])
        if "country" in p:
            cats = cats.filter(breeder__country__iexact=p["country"])
        if "min_price" in p:
            cats = cats.filter(price__gte=p["min_price"])
        if "max_price" in p:
            cats = cats.filter(price__lte=p["max_price"])
        if "status" in p:
            cats = cats.filter(status=p["status"])

        sort_fields = {"price": "price", "created_at": "created_at"}
        field = sort_fields[p["sort_by"]]
        descending = p["order"] == "desc"
        cats = cats.order_by(f"-{field}" if descending else field, "id")

        total = cats.count()
        offset = (p["page"] - 1) * p["limit"]
        page_items = cats[offset:offset + p["limit"]]

        return Response({
            "items": CatShortSerializer(page_items, many=True).data,
            "page": p["page"],
            "limit": p["limit"],
            "total": total,
        })

    @extend_schema(
        tags=["Cats"],
        summary="Create a cat",
        description="Admin only",
        responses={
            201: CatSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Not authenticated"),
            403: OpenApiResponse(description="Permission denied"),
        },
        request = CatSerializer,
        examples=[
            OpenApiExample(
                "New cat",
                value={
                    "name": "Barsik",
                    "sex": "male",
                    "breed_id": 1,
                    "breeder_id": 1,
                    "birth_date": "2024-03-10",
                    "price": 200,
                    "photo_url": "https://example.com/barsik.jpg",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = CatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CatDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        tags=["Cats"],
        summary="Get details for a cat",
        description="Public endpoint. Returns a cat by id.",
        responses={
            200: CatSerializer,
            404: OpenApiResponse(description="Cat is not found"),
        },
    )
    def get(self, request, pk):
        cat = get_object_or_404(Cat, pk=pk)
        serializer = CatSerializer(cat)
        return Response(serializer.data)

    @extend_schema(
        tags=["Cats"],
        summary="Update a cat",
        description="Partial update. Admin only.",
        request = CatSerializer,
        responses={
            200: CatSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Not authenticated"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Cat is not found"),
        },
    )
    def patch(self, request, pk):
        cat = get_object_or_404(Cat, pk=pk)
        serializer = CatSerializer(cat, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        tags=["Cats"],
        summary="Delete a cat",
        description="Complete deletion. Admin only.",
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Not authenticated"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Cat is not found"),
        },
    )
    def delete(self, request, pk):
        cat = get_object_or_404(Cat, pk=pk)
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BreederListView(APIView):
    def get(self, request):
        breeders = Breeder.objects.all()
        serializer = BreederShortSerializer(breeders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BreederSerializer(data=request.data)
        if not serializer.is_valid():
            if is_duplicate(serializer.errors, "email"):
                raise ConflictError("Breeder with this email already exists")
            raise ValidationError(serializer.errors)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BreederDetailView(APIView):
    def get(self, request, pk):
        breeder = get_object_or_404(Breeder, pk=pk)
        serializer = BreederSerializer(breeder)
        return Response(serializer.data)

    def patch(self, request, pk):
        breeder = get_object_or_404(Breeder, pk=pk)
        serializer = BreederSerializer(breeder, data=request.data, partial=True)
        if not serializer.is_valid():
            if is_duplicate(serializer.errors, "email"):
                raise ConflictError("Breeder with this email already exists")
            raise ValidationError(serializer.errors)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        breeder = get_object_or_404(Breeder, pk=pk)
        try:
            breeder.delete()
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete breeder: there are cats attached to this breeder",
                    }, status=status.HTTP_409_CONFLICT
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class BreedListView(APIView):
    def get(self, request):
        breeds = Breed.objects.all()
        serializer = BreedSerializer(breeds, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BreedSerializer(data=request.data)
        if not serializer.is_valid():
            if is_duplicate(serializer.errors, "name"):
                raise ConflictError("Breeder with this email already exists")
            raise ValidationError(serializer.errors)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BreedDetailView(APIView):
    def patch(self, request, pk):
        breed = get_object_or_404(Breed, pk=pk)
        serializer = BreedSerializer(breed, data=request.data, partial=True)
        if not serializer.is_valid():
            if is_duplicate(serializer.errors, "name"):
                raise ConflictError("Breed with this name already exists")
            raise ValidationError(serializer.errors)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        breed = get_object_or_404(Breed, pk=pk)
        try:
            breed.delete()
        except ProtectedError:
            raise ConflictError("Cannot delete breed: there are cats attached to this breed")
        return Response(status=status.HTTP_204_NO_CONTENT)
