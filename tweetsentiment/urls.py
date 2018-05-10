from django.urls import path

from . import views

app_name = "tweetsentiment"

urlpatterns = [
    path('', views.TweetSentiment, name='tweetsentiment'),
    path('api/search/<hashtag>/<int:count>', views.api_get_tweets),
    path('api/set_sensitivity/<polaritySensitivity>', views.api_set_sensitivity),
]
