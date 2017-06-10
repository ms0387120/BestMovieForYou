import os
import json
import yaml
import requests
import itertools
from urllib.parse import urljoin

with open('config.yaml', 'r') as stream:
    config = yaml.load(stream)
    

# Data folder
data_folder = os.path.join('.', 'data')
os.system('mkdir data')



# Crawl movies
def crawl_movies_for_year(year):
    
    var = {
        'api_key': config['api_key'],
        'language': 'en-US',
        'sort_by': 'primary_release_date.asc',
        'include_adult': 'false',
        'include_video': 'false',
        'page': 1,
        'primary_release_year': year,
    }
    
    url_stem = 'https://api.themoviedb.org/3/discover/movie?'
    url_var = '&'.join(
        ['{}={{{}}}'.format(key, key) for key in list(variables.keys())])
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

for year in range(2011, 2017):
    print(year)
    movies = crawl_movies_for_year(year)
    data_file = os.path.join(data_folder, 'movies_{}.dat'.format(year))
    with open(data_file, 'w') as stream:
        json.dump(movies, stream)
        

        
# Extract movie id
def extract_movie_id(years):
    for year in years:
        data_file = os.path.join(data_folder, 'movies_{}.dat'.format(year))
        with open(data_file, 'r') as stream:
            movies = json.load(stream)
        yield (year, list(set([m['id'] for m in movies])))
movie_ids = dict(list(extract_movie_id(range(2011, 2017))))

data_file = os.path.join(data_folder, 'movie_ids.json')
with open(data_file, 'w') as stream:
        json.dump(movie_ids, stream)
        
        
        
# Crawl movie keywords
def crawl_movie_keywords(ID):
    var = {
        'api_key': config['api_key'],
        'movie_id': ID,
    }
    url = 'https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={api_key}'
    
    try:
        r = requests.get(url.format(**var))
        j = json.loads(r.content.decode("utf-8") )
        keywords = j['keywords']
        return keywords
    except Exception as e:
        print(ID)
        print(e)
        return []

data_file = os.path.join(data_folder, 'movie_ids.json')
with open(data_file, 'r') as stream:
    movie_ids = json.load(stream)

for year, ids in movie_ids.items():
    id_keywords = dict([(ID, crawl_movie_keywords(ID)) for ID in ids])
    data_file = os.path.join(data_folder, 'movie_keywords_{}.json'.format(year))
    with open(data_file, 'w') as stream:
        json.dump(id_keywords, stream)
        
        
        
# Crawl movie credits
def crawl_movie_credits(ID):
    var = {
        'api_key': config['api_key'],
        'movie_id': ID,
    }
    url = 'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}'
    
    try:
        r = requests.get(url.format(**var))
        j = json.loads(r.content.decode("utf-8") )
        credits = j['cast']
        return credits
    except Exception as e:
        print(ID)
        print(e)
        return []

data_file = os.path.join(data_folder, 'movie_ids.json')
with open(data_file, 'r') as stream:
    movie_ids = json.load(stream)

for year, ids in movie_ids.items():
    id_credits = dict([(ID, crawl_movie_credits(ID)) for ID in ids])
    data_file = os.path.join(data_folder, 'movie_credits_{}.json'.format(year))
    with open(data_file, 'w') as stream:
        json.dump(id_credits, stream)