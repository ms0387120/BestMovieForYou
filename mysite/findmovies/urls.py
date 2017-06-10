from django.conf.urls import url

from . import views
from . import views_dev

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search_movies/$', views.search_movies, name='search_movies'),
    url(r'^get_reference_movie_imdb_id/$', views.get_reference_movie_imdb_id, name='get_reference_movie_imdb_id'),
    url(r'^search_similar_movies/$', views.search_similar_movies, name='search_similar_movies'),
    url(r'^search_similar_movies_dev/$', views_dev.search_similar_movies, name='search_similar_movies_dev'),
]
