from django.contrib import admin

# Register your models here.
from .models import Guestbook

admin.site.register(Guestbook)
