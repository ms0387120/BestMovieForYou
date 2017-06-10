import os
import json
import yaml
import itertools
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

with open('config.yaml', 'r') as stream:
    config = yaml.load(stream)
    
data_folder = os.path.join('.', 'data')


def crawl_popular_movies_id():
    
    var = {
        'api_key': config['api_key'],
        'language': 'en-US',
        'page': 1,
    }
    
    url_stem = 'https://api.themoviedb.org/3/movie/popular?'
    url_var = '&'.join(
        ['{}={{{}}}'.format(key, key) for key in list(var.keys())])
    url = url_stem + url_var
    
    r = requests.get(url.format(**var))
    j = json.loads(r.content.decode("utf-8") )
    total_pages = j['total_pages']
    
    def crawl_movies(total_pages):
        for page in range(1, total_pages+1):
            var['page'] = page
            r = requests.get(url.format(**var))
            j = json.loads(r.content.decode("utf-8") )
            yield j['results']
    
    movies = list(crawl_movies(total_pages))
    movies = list(itertools.chain.from_iterable(movies))
    
    return movies

movies = crawl_popular_movies_id()

# Save popular movies
data_file = os.path.join(data_folder, 'popular_movies.json')
with open(data_file, 'w') as stream:
    json.dump(movies, stream)

# Load popular movies and transform to dictionary
data_file = os.path.join(data_folder, 'popular_movies.json')
with open(data_file, 'r') as stream:
    movies_load = json.load(stream)
movies_load = dict([(d['id'], d) for d in movies_load])



def crawl_movies_detail(movie_id):
    
    var = {
        'movie_id': movie_id,
        'api_key': config['api_key'],
        'language': 'en-US',
    }
    
    url_stem = 'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language={language}'
    url = url_stem.format(**var)
    
    r = requests.get(url)
    j = json.loads(r.content.decode("utf-8"))
    
    return j
movies_detail = [crawl_movies_detail(movie_id) for movie_id in list(movies_load.keys())]
movies_detail = list(filter(lambda x: 'id' in x.keys(), movies_detail))

# Save popular movies details
data_file = os.path.join(data_folder, 'popular_movies_details.json')
with open(data_file, 'w') as stream:
    json.dump(movies_detail, stream)
    
# Load popular movies details and transform to dictionary
data_file = os.path.join(data_folder, 'popular_movies_details.json')
with open(data_file, 'r') as stream:
    movies_details_load = json.load(stream)
movies_details_load = list(filter(lambda x: 'id' in x.keys(), movies_details_load))



id_imdb_id = list([(movie['id'], movie['imdb_id']) for movie in movies_details_load])
id_imdb_id = list(filter(lambda x: x[1] != '', id_imdb_id))
id_imdb_id = list(filter(lambda x: x[1] != None, id_imdb_id))

def crawl_imdb_synopsis(imdb_id):
    
    url = 'http://www.imdb.com/title/{}/synopsis'.format(imdb_id)
    
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    node = soup.select('div#swiki.2.1')[0]
    
    return node.get_text()

def get_synopsis():
    for p in id_imdb_id:
        try:
            synopsis = crawl_imdb_synopsis(p[1])
            yield (p[0], synopsis)
        except:
            pass
        
synopsis = list(get_synopsis())
synopsis = list(filter(lambda x: x[1] != '\n', synopsis))

# Save popular movies synopsis
data_file = os.path.join(data_folder, 'popular_movies_synopsis.json')
with open(data_file, 'w') as stream:
    json.dump(synopsis, stream)