from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from .tools import *
from .tweetsentiment import *

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

    # Let's get the tweetdata
    tweetdata = get_and_sentimentanalyze_tweets(hashtag, sensitivity)
    if tweetdata == TWEETSENTIMENT_ERROR:
        # Error fetching the tweets! Let's return an error message
        template = loader.get_template('tweetsentiment/tweetsentiment.html')
        context = {
            'hashtag': hashtag,
            'error_message': "Error when trying to get tweets!"
        }
        return HttpResponse(template.render(context, request))


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



###############################
# Views for the rest API access

# Returns the <count> number of latest tweets with the hashtag <hashtag>
@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def api_get_tweets(request, hashtag, count):
    # Let's get the user's polaritySensitivity
    polaritySensitivity = request.user.usersettings.polarity_interpretation_sensitivity
    print("PolaritySensitivity:", polaritySensitivity)

    # API is currently limited to max 100 tweet. If the user asks for more, let's return an error
    if count > 100:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Location data is omitted from API calls, as those take a lot of time
    tweetdata = get_and_sentimentanalyze_tweets(hashtag, sensitivity=polaritySensitivity, count=count, getlocation=False, include_original_status=False)
    return Response(tweetdata)


@api_view(['PUT'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def api_set_sensitivity(request, polaritySensitivity):
    # Let's set the user's polaritySensitivity
    try:
        polaritySensitivity = float(polaritySensitivity)
        # Let's check if the sensitivity is within the required interval
        if polaritySensitivity < 0 or 1 < polaritySensitivity:
            # The sensitivity is under 0 or over 1, which is not permitted
            Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        # Let's set the new sensitivity
        request.user.usersettings.polarity_interpretation_sensitivity = polaritySensitivity
        request.user.usersettings.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    except:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
