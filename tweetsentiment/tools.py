# A collection of helper funcitons used in tweetsentiment
from django.conf import settings
import re
import googlemaps

# Removes retweet text ("RT @XXXX:") from the beginning of the tweet, and removes hashtag-chars
def prepare_tweet_for_textblob(full_text):
    # Let's see if a tweet is a retweet
    if len(full_text)>4 and full_text[:4] == "RT @":
        full_text = full_text[(full_text.find(": ")+2):]

    # Let's remove the hashtags and asperands
    full_text = full_text.replace("#", "").replace("@", "")

    # Let's remove links. Thanks Ωmega
    # https://stackoverflow.com/questions/11331982/how-to-remove-any-url-within-a-string-in-python
    full_text = re.sub(r"http\S+", "", full_text)

    return full_text


# Get's the extended retweet, if twitter has shortened the default representation
def get_extended_tweet_text(status):
    # Let's see if a tweet is a retweet, and is shortened
    if len(status.full_text)>4 and status.full_text[:4] == "RT @" and status.retweeted_status is not None:
        retweet_head = status.full_text[:(status.full_text.find(": ")+2)]

        # Let's reconstruct the extended retweet
        return(retweet_head+status.retweeted_status.full_text)

    else:
        return status.full_text


# Get's the country and state of the user who posted the tweet
def get_tweet_location(tweet):
    google_maps_api = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)

    if tweet.user.location.strip() != "":
        coordinates = google_maps_api.geocode(tweet.user.location)
        if len(coordinates) != 0:
            # We got a match with geocode!
            if len(coordinates[0]['address_components'])>=2:
                # We got both the state and the country!
                return (coordinates[0]['address_components'][-2]['long_name'], coordinates[0]['address_components'][-1]['long_name'])
            else:
                # We only got the top level location
                return (None, coordinates[0]['address_components'][-1]['long_name'])

    return (None, None)
