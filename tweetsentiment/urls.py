from django.urls import path

from . import views

app_name = "tweetsentiment"

urlpatterns = [
    path('', views.TweetSentiment, name='tweetsentiment'),
]
