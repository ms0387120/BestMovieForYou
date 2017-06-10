from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search_movies/$', views.search_movies, name='search_movies'),
    url(r'^get_reference_movie_imdb_id', views.get_reference_movie_imdb_id, name='get_reference_movie_imdb_id'),
    url(r'^search_similar_movies', views.search_similar_movies, name='search_similar_movies'),
]
