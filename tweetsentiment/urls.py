from django.urls import path

from . import views

app_name = "tweetsentiment"

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.TweetSentiment, name='tweetsentiment'),
]
