# A collection of helper funcitons and data used in tweetsentiment
from django.conf import settings
import threading
import simplejson
import re
import googlemaps

# Max number of threads to use
MAXTHREADS = 20

# A lookup table for state acronyms
STATEABREVIATIONS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

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


## Threaded version of get_tweet_location(...) for making the geocoding faster
# list for keeping track of threads
threads = []

# The threaded tweet geocoding function
def get_tweet_location_threaded(tweet, save_to_list):
    global threads
    # Helper function to extract the location from the normal function, and put it to the list
    def tweet_location_to_list(tweet, save_to_list):
        save_to_list.append(get_tweet_location(tweet))

    # Let's first see, if we are already running the max number of threads
    if len(threads) >= MAXTHREADS:
        # Already running the max number of threads! Let's wait until ALL the threads are finished
        # (this is to limit the continuous bombarding of the geocode api)
        join_tweet_location_threads()

    print("[* ->] Spawning a thread no.", len(threads)+1)

    # Let's start a new thread
    t = threading.Thread(target=tweet_location_to_list, args=(tweet, save_to_list,))
    threads.append(t)
    t.start()

# Used to join the geolocating threads, so that that all the threads are finished before continuing
def join_tweet_location_threads():
    global threads
    # Let's join all the threads
    for i, thread in enumerate(threads):
        print("[* ->] Joining thread no.", i+1)
        thread.join()

    # All threads finished! Let's clear the threads -list
    threads = []


# Generates a json dataset of the average US state sentiment data, that can be passed to the ustate -graph
def create_US_state_average_sentiments(tweetdata, decimals=2):
    state_sentiments = {}

    # Let's get the state by state tweet sentiments
    for tweet in tweetdata:
        # Let's see if the current tweet is a tweet sent from an US state
        if tweet['location'][1] == "United States" and tweet['location'][0] in STATEABREVIATIONS:
            # Let's add the sentiment data to the list
            if STATEABREVIATIONS[tweet['location'][0]] in state_sentiments:
                state_sentiments[STATEABREVIATIONS[tweet['location'][0]]].append(tweet['sentiment'].polarity)
            else:
                state_sentiments[STATEABREVIATIONS[tweet['location'][0]]] = [tweet['sentiment'].polarity]

    # Let's init the final dataset
    state_sentiment_averages = {}
    for abreviation in STATEABREVIATIONS.values():
        state_sentiment_averages[abreviation] = {'average': 0, 'count': 0}

    # Let's get the average of the sentiment for each state
    for state_key in state_sentiments.keys():
        average_sentiment = round(sum(state_sentiments[state_key])/len(state_sentiments[state_key]), decimals)
        state_sentiment_averages[state_key] = {'average': average_sentiment, 'count': len(state_sentiments[state_key])}

    # Let's turn the dict into a json
    state_sentiment_averages = simplejson.dumps(state_sentiment_averages)

    return state_sentiment_averages
