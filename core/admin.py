from django.contrib import admin
from .models import Resource
from .models import Reservation

admin.site.register(Resource)
admin.site.register(Reservation)