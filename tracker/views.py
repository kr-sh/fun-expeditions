from django.shortcuts import render
from django.http import HttpResponse

from .models import Person

# Create your views here.

def index(request):
    person = Person.objects.all()[0]
    output = person.first_name
    return HttpResponse(output)
