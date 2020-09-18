from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

# Create your views here.

@login_required
def home(request):
    return render(request, 'home.template.html')


