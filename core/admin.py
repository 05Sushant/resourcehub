from django.contrib import admin
from .models import Resource
from .models import Reservation, Job

admin.site.register(Resource)
admin.site.register(Reservation)
admin.site.register(Job)