from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
import os
import numpy as np
from django.shortcuts import render
from dotenv import load_dotenv
from openai import OpenAI
from .models import Movie

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
    
    # Cargar API Key desde openAI.env o variables de entorno
load_dotenv("openAI.env")
client = OpenAI(api_key=os.environ.get("openai_apikey"))

def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # Evita divisiones por cero
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0.0 or nb == 0.0:
        return -1.0
    return float(np.dot(a, b) / (na * nb))

def recommend_view(request):
    context = {"query": "", "result": None, "similarity": None, "error": None}
    if request.method == "POST":
        query = request.POST.get("q", "").strip()
        context["query"] = query
        if not query:
            context["error"] = "Escribe un prompt de búsqueda."
            return render(request, "movie/recommend.html", context)

        try:
            # 1) Generar embedding del prompt
            resp = client.embeddings.create(
                input=[query],
                model="text-embedding-3-small"
            )
            prompt_emb = np.array(resp.data[0].embedding, dtype=np.float32)

            # 2) Recorrer películas con embedding y calcular similitud
            best = None
            best_sim = -1.0

            for m in Movie.objects.exclude(emb__isnull=True):
                movie_emb = np.frombuffer(m.emb, dtype=np.float32)
                sim = _cosine_similarity(prompt_emb, movie_emb)
                if sim > best_sim:
                    best_sim = sim
                    best = m

            if best is None:
                context["error"] = "No hay embeddings en la base de datos. Genera embeddings primero."
            else:
                context["result"] = best
                context["similarity"] = round(best_sim, 4)

        except Exception as e:
            context["error"] = f"Fallo al recomendar: {e}"

    return render(request, "recommend.html", context)