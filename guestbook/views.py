from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import *

# Create your views here.
def guestbook(request):
    # Let's get 50 newest guestbook entries and show the guestbook
    guestbook_entries = Guestbook.objects.order_by('-entry_datetime')[:50]
    template = loader.get_template('guestbook/guestbook.html')
    context = {
    'guestbook_entries': guestbook_entries,
    }
    return HttpResponse(template.render(context, request))


def get_ip_address(request):
    """ use requestobject to fetch client machine's IP Address """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')    ### Real IP address of client Machine
    return ip


def create_entry(request):
    guestbook_entries = Guestbook.objects.order_by('-entry_datetime')[:50]

    try:
        entry_text = request.POST['entry_text']
        writer_nickname = request.POST['writer_nickname']
        if entry_text == "" or writer_nickname == "":
            raise

    except:
        # Display guestbook with an error.
        return render(request, 'guestbook/guestbook.html', {
        'guestbook_entries': guestbook_entries,
        'error_message': "Error when adding an entry! "+entry_text+" "+writer_nickname,
        })
    else:
        entry = Guestbook(entry_text=entry_text, writer_nickname=writer_nickname, ipaddress=get_ip_address(request))
        entry.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('guestbook:guestbook'))
