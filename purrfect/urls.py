from django.urls import path

from . import views

urlpatterns = [
    path("cats/", views.CatListView.as_view()),
    path("cats/<int:pk>/", views.CatDetailView.as_view()),
    path("breeders/", views.BreederListView.as_view()),
    path("breeders/<int:pk>/", views.BreederDetailView.as_view()),
    path("breeds/", views.BreedListView.as_view()),
    path("breeds/<int:pk>/", views.BreedDetailView.as_view()),
]
