from django.conf import settings

import twitter
from textblob import TextBlob

from .tools import *

TWEETSENTIMENT_ERROR = -1

def get_and_sentimentanalyze_tweets(hashtag, sensitivity, count=100, getlocation=True, include_original_status=True):
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
        for _ in range(1):
            if last_tweet_id is None:
                new_tweets = twitter_api.GetSearch(term="#"+hashtag, lang='en', result_type='recent', count=count)
                last_tweet_id = new_tweets[-1].id
                tweets.extend(new_tweets)
            else:
                new_tweets = twitter_api.GetSearch(term="#"+hashtag, lang='en', max_id=last_tweet_id, result_type='recent', count=count)
                last_tweet_id = new_tweets[-1].id - 1
                tweets.extend(new_tweets)

    except:
        # Error fetching the tweets!
        return TWEETSENTIMENT_ERROR

    print("Tweets loaded:", len(tweets))

    tweetdata = []

    # Let's do the analysis
    for status in tweets:
        # Let's prepare the tweet for analysis and analyze it
        extended_tweet = get_extended_tweet_text(status)
        analysis = TextBlob(prepare_tweet_for_textblob(extended_tweet))
        polarity_interpretation = 'positive' if analysis.sentiment.polarity > sensitivity else \
                                    'negative' if analysis.sentiment.polarity < -sensitivity else 'neutral'


        # Let's get the location, if the user wants to
        if getlocation:
            location = get_tweet_location(status)
        else:
            location = None

        if include_original_status:
            tweetdata.append({'tweet': status,
                              'extended_tweet': extended_tweet,
                              'sentiment': analysis.sentiment,
                              'polarity_interpretation': polarity_interpretation,
                              'location': location})
        else:
            tweetdata.append({'extended_tweet': extended_tweet,
                              'sentiment': analysis.sentiment,
                              'polarity_interpretation': polarity_interpretation,
                              'location': location})


    return tweetdata
