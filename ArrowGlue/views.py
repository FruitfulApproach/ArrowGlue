from django.contrib import messages
from django.shortcuts import HttpResponse, render

def messages(request):
    return render(request, 'messages.html')

def clear_messages(request):
    list(messages.get_messages(request))
    return HttpResponse('')