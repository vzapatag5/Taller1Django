from django.shortcuts import render
from .models import News

def news(request):
    newss = News.objects.all().order_by('-headline')
    return render(request, 'news.html', {'newss': newss})
