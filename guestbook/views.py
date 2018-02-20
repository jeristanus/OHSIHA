from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .models import *

# Create your views here.
def guestbook(request):
    # Let's get 50 newest guestbook entries and show the guestbook
    guestbook_entries = Guestbook.objects.order_by('-pub_date')[:50]
    print(guestbook_entries)
    template = loader.get_template('guestbook/guestbook.html')
    context = {
    'guestbook_entries': guestbook_entries,
    }
    return HttpResponse(template.render(context, request))
