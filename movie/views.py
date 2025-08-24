from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

from .models import Movie

#Create your views here
def home(request):
    #return HttpResponse('<h1>Welcome to Home Page!</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html', {'name': 'Valentina Zapata'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': movies})

def about(request):
    #return HttpResponse('<h1>Welcome to About Page!</h1>')
     return render(request, 'about.html', {'name': 'Valentina Zapata'})
 
def get_graph():
    """Convierte el gráfico de matplotlib a base64 para mostrar en HTML"""
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    return base64.b64encode(image_png).decode('utf-8')


def statistics(request):
    all_movies = Movie.objects.all()

    # ========================
    # 1. Gráfico por AÑO
    # ========================
    movie_counts_by_year = {}
    for movie in all_movies:
        year = str(movie.year) if movie.year else "None"
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    plt.figure(figsize=(8, 5))
    plt.bar(movie_counts_by_year.keys(), movie_counts_by_year.values(), width=0.5)
    plt.title('Movies per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.xticks(rotation=90)
    graphic_year = get_graph()

    # ========================
    # 2. Gráfico por GÉNERO
    # ========================
    movie_counts_by_genre = {}
    for movie in all_movies:
            if movie.genre:
                # Tomar solo el primer género (antes de la coma)
                first_genre = str(movie.genre).split(",")[0].strip()
            else:
                first_genre = "None"

            movie_counts_by_genre[first_genre] = movie_counts_by_genre.get(first_genre, 0) + 1

    plt.figure(figsize=(8, 5))
    plt.bar(movie_counts_by_genre.keys(), movie_counts_by_genre.values(), width=0.5, color='orange')
    plt.title('Movies per Genre (first only)')
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.xticks(rotation=45)
    graphic_genre = get_graph()

    return render(request, 'statistics.html', {
            'graphic_year': graphic_year,
            'graphic_genre': graphic_genre
        })