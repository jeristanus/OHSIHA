from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

import requests
from requests_oauthlib import OAuth1
from textblob import TextBlob
import twitter

from .models import *

def index(request):
    # Index of the page
    template = loader.get_template('tweetsentiment/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


@login_required()
def TweetSentiment(request):
    # Let's see if we have a hashtag
    if 'hashtag' not in request.GET or request.GET['hashtag'] == "" or request.GET['hashtag'].find(" ") != -1:
        # No hashtag provided!
        template = loader.get_template('tweetsentiment/tweetsentiment.html')
        context = {
            'hashtag': "",
        }
        return HttpResponse(template.render(context, request))


    hashtag = request.GET['hashtag'].lower()
    # Let's remove the hashtag-sign from the beginning of the hashtag input
    if hashtag[0] == '#':
        hashtag = hashtag[1:]

    try:
        # Let's get tweets
        twitter_api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                                    consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                                    access_token_key=settings.TWITTER_ACCESS_TOKEN,
                                    access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
                                    tweet_mode='extended',
                                    cache=None)

        tweets = twitter_api.GetSearch(term="#"+hashtag, lang='en', result_type='recent')
    except:
        # Error fetching the tweets! Let's return an error message
        template = loader.get_template('tweetsentiment/tweetsentiment.html')
        context = {
            'hashtag': hashtag,
            'error_message': "Error when trying to get tweets!"
        }
        return HttpResponse(template.render(context, request))


    tweetdata = []
    # Let's run a sentiment analysis and compile a dataset for the template
    sensitivity = 0.2   # Sensitivity determines easily a positive/negative tweet will be
                        # shown with a green/red color

    for status in tweets:
        analysis = TextBlob(status.full_text)
        polarity_interpretation = 'positive' if analysis.sentiment.polarity > sensitivity else \
                                    'negative' if analysis.sentiment.polarity < -sensitivity else 'neutral'

        tweetdata.append({'tweet': status,
                          'sentiment': analysis.sentiment,
                          'polarity_interpretation': polarity_interpretation})

    template = loader.get_template('tweetsentiment/tweetsentiment.html')
    context = {
        'statuses': tweetdata,
        'hashtag': hashtag,
        'user': request.user,
    }
    return HttpResponse(template.render(context, request))
