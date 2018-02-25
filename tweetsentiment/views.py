from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import requests
from requests_oauthlib import OAuth1
from django.conf import settings
from textblob import TextBlob

from .models import *

def index(request):
    # Index of the page
    template = loader.get_template('tweetsentiment/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


# Create your views here.
def TweetSentiment(request):
    # Let's see if we got a hashtag
    if 'hashtag' not in request.GET or request.GET['hashtag'].find(" ") != -1:
        # No hashtag provided! Let's return to the index Page
        return render(request, 'tweetsentiment/index.html')

    hashtag = request.GET['hashtag'].lower()
    # Let's remove the hashtag-sign from the beginning of the hashtag input
    if hashtag[0] == '#':
        hashtag = hashtag[1:]

    # Let's get tweets
    tweets = requests.get(url='https://api.twitter.com/1.1/search/tweets.json?q=%23'+hashtag+'&count=100',
                        auth=OAuth1(settings.TWITTER_CONSUMER_KEY,
                                    client_secret=settings.TWITTER_CONSUMER_SECRET,
                                    resource_owner_key=settings.TWITTER_ACCESS_TOKEN,
                                    resource_owner_secret=settings.TWITTER_ACCESS_TOKEN_SECRET))

    tweetdata = []
    # Let's run a sentiment analysis and compile a dataset for the template
    sensitivity = 0.2   # Sensitivity determines easily a positive/negative tweet will be
                        # shown with a green/red color

    for tweet in tweets.json()['statuses']:
        analysis = TextBlob(tweet['text'])
        polarity_interpretation = 'positive' if analysis.sentiment.polarity > sensitivity else 'negative' if analysis.sentiment.polarity < -sensitivity else 'neutral'

        tweetdata.append({'created_at': tweet['created_at'],
                          'screen_name': tweet['user']['screen_name'],
                          'text': tweet['text'],
                          'sentiment': analysis.sentiment,
                          'polarity_interpretation': polarity_interpretation})

    template = loader.get_template('tweetsentiment/tweetsentiment.html')
    context = {
        'statuses': tweetdata,
    }
    return HttpResponse(template.render(context, request))
