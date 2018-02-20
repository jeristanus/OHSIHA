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

def create_entry(request):
    # Display guestbook with an error.
    guestbook_entries = Guestbook.objects.order_by('-entry_datetime')[:50]

    try:
        entry_text = request.POST['entry_text']
        writer_nickname = request.POST['writer_nickname']
        if entry_text == "" or writer_nickname == "":
            raise

    except:
        return render(request, 'guestbook/guestbook.html', {
        'guestbook_entries': guestbook_entries,
        'error_message': "Error when adding an entry! "+entry_text+" "+writer_nickname,
        })
    else:
        entry = Guestbook(entry_text=entry_text, writer_nickname=writer_nickname)
        entry.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('guestbook:guestbook'))
