from django.contrib import admin
from .models import Boat, BoatCategory, BoatImage, WishList

admin.site.register(Boat)
admin.site.register(BoatCategory)
admin.site.register(BoatImage)
admin.site.register(WishList)

