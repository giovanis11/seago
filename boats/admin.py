from django.contrib import admin
from .models import Boat, BoatCategory, BoatImage, WishList

class BoatImageInline(admin.TabularInline):
    model = BoatImage
    extra = 3

class BoatAdmin(admin.ModelAdmin):
    inlines = [BoatImageInline]
    list_display = ("name", "category", "luxury_subcategory", "owner", "is_approved")
    list_filter = ("category", "luxury_subcategory", "is_approved", "is_available")

admin.site.register(Boat, BoatAdmin)
admin.site.register(BoatCategory)
admin.site.register(BoatImage)
admin.site.register(WishList)
