from django.contrib import admin

from django.contrib import admin
from .models import Cat, Breeder, Breed

@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ("name", "breed", "breeder", "price", "status")
    list_filter = ("status", "breed")
    search_fields = ("name",)
    list_editable = ("status",)

admin.site.register(Breeder)
admin.site.register(Breed)
