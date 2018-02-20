from django.urls import path

from . import views

app_name = "guestbook"

urlpatterns = [
    path('', views.guestbook, name='guestbook'),
    path('create_entry/', views.create_entry, name='create_entry')
]
