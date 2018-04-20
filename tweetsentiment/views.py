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
from .tools import *

def index(request):
    # Index of the page
    template = loader.get_template('tweetsentiment/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


@login_required
def TweetSentiment(request):
    # Let's see if we have a hashtag
    if 'hashtag' not in request.GET or request.GET['hashtag'] == "" or request.GET['hashtag'].find(" ") != -1:
        # No hashtag provided!
        template = loader.get_template('tweetsentiment/tweetsentiment.html')
        context = {
            'hashtag': request.user.usersettings.last_hashtag_searched,
            'user': request.user,
        }
        return HttpResponse(template.render(context, request))


    hashtag = request.GET['hashtag'].lower()
    # Let's remove the hashtag-sign from the beginning of the hashtag input
    if hashtag[0] == '#':
        hashtag = hashtag[1:]

    try:
        # Let's get apis
        twitter_api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                                    consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                                    access_token_key=settings.TWITTER_ACCESS_TOKEN,
                                    access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
                                    tweet_mode='extended',
                                    cache=None)

        # Let's get the tweets
        tweets = []
        last_tweet_id = None
        for _ in range(2):
            if last_tweet_id is None:
                new_tweets = twitter_api.GetSearch(term="#"+hashtag, lang='en', result_type='recent', count=100)
                last_tweet_id = new_tweets[-1].id
                tweets.extend(new_tweets)
            else:
                new_tweets = twitter_api.GetSearch(term="#"+hashtag, lang='en', max_id=last_tweet_id, result_type='recent', count=100)
                last_tweet_id = new_tweets[-1].id - 1
                tweets.extend(new_tweets)

    except:
        # Error fetching the tweets! Let's return an error message
        template = loader.get_template('tweetsentiment/tweetsentiment.html')
        context = {
            'hashtag': hashtag,
            'error_message': "Error when trying to get tweets!"
        }
        return HttpResponse(template.render(context, request))

    print("Tweets loaded:", len(tweets))

    tweetdata = []

    #** Let's run a sentiment analysis and compile a dataset for the template **
    # The sensitivity determines easily a positive/negative tweet will be shown with a green/red color
    # Let's save a a new sensitivity the user gave, or use the previous value
    try:
        sensitivity = float(request.GET['polaritySensitivity'])
        request.user.usersettings.polarity_interpretation_sensitivity = sensitivity
        request.user.usersettings.last_hashtag_searched = hashtag
        request.user.usersettings.save()
    except:
        sensitivity = request.user.usersettings.polarity_interpretation_sensitivity

    # Let's do the analysis
    for status in tweets:
        # Let's prepare the tweet for analysis and analyze it
        extended_tweet = get_extended_tweet_text(status)
        analysis = TextBlob(prepare_tweet_for_textblob(extended_tweet))
        polarity_interpretation = 'positive' if analysis.sentiment.polarity > sensitivity else \
                                    'negative' if analysis.sentiment.polarity < -sensitivity else 'neutral'


        location = get_tweet_location(status)
        #get_tweet_location_threaded(status, location)

        tweetdata.append({'tweet': status,
                          'extended_tweet': extended_tweet,
                          'sentiment': analysis.sentiment,
                          'polarity_interpretation': polarity_interpretation,
                          'location': location})

    # Let's wait for all the threads to finish
    # join_tweet_location_threads()

    # Let's "unlist" all the location data
    # for i in range(0, len(tweetdata)):
    #    tweetdata[i]['location'] = tweetdata[i]['location'][0]

    # Let's get the uState passable dataset of the US sentiments
    uState_data = create_US_state_average_sentiments(tweetdata)

    template = loader.get_template('tweetsentiment/tweetsentiment.html')
    context = {
        'statuses': tweetdata,
        'hashtag': hashtag,
        'user': request.user,
        'uState_data': uState_data,
    }
    return HttpResponse(template.render(context, request))
