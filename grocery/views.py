from django.shortcuts import render


def index(request):
    """Display all grocery items"""
    return render(request, 'grocery/index.html')