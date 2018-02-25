from django.contrib import admin

# Register your models here.
from .models import Guestbook

class GuestbookAdmin(admin.ModelAdmin):
    list_display = ['entry_text', 'writer_nickname', 'entry_datetime']

admin.site.register(Guestbook, GuestbookAdmin)
