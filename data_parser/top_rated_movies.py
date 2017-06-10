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


def parse_corpus(corpus):
    
    import nltk
    from nltk import wordpunct_tokenize
    from nltk.corpus import stopwords
    from nltk.stem.porter import PorterStemmer
    #from nltk.tag.stanford import StanfordNERTagger
    from nltk.tag import pos_tag
    import string
    import itertools
    
    
    commonWords = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'I', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when'\
, 'your', 'can', 'said', 'there', 'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'mo\
re', 'write', 'go', 'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part']
    listOfCharToExclude = ['.', ',', ':', '"', '+', '!', '?', '/', "'", '*', '(', ')', '$', '@', '&', '*',']','[']
    
    stopwords = set(stopwords.words('english'))
    stopwords.update(string.punctuation)
    stopwords.update([p[0] + p[1] for p in itertools.product(string.punctuation, string.punctuation)])
    stopwords.update(commonWords)
    stopwords.update(listOfCharToExclude)
    
    #st = StanfordNERTagger('/home/orange63/TextMining/Project2/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz',
    #                       '/home/orange63/TextMining/Project2/stanford-ner-2014-06-16/stanford-ner-3.4.jar')
    porter = PorterStemmer()
    
    corpus_token = wordpunct_tokenize(corpus)
    corpus_token = [word for word in corpus_token if word not in stopwords]
    #corpus_no_people = [p[0] for p in filter(lambda x: x[1] != 'PERSON', st.tag(corpus_token))]
    corpus_NN = [p[0] for p in filter(lambda x: (x[1] == 'NN') or (x[1] == 'NNP'), pos_tag(corpus_token))]
    corpus_stem = [porter.stem(word) for word in corpus_NN]
    
    return ' '.join(corpus_stem)



def crawl_top_rated_movies_id():
    
    var = {
        'api_key': config['api_key'],
        'language': 'en-US',
        'page': 1,
    }
    
    url_stem = 'https://api.themoviedb.org/3/movie/top_rated?'
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

movies = crawl_top_rated_movies_id()

# Save top_rated movies
data_file = os.path.join(data_folder, 'top_rated_movies.json')
with open(data_file, 'w') as stream:
    json.dump(movies, stream)

# Load top_rated movies and transform to dictionary
data_file = os.path.join(data_folder, 'top_rated_movies.json')
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

# Save top_rated movies details
data_file = os.path.join(data_folder, 'top_rated_movies_details.json')
with open(data_file, 'w') as stream:
    json.dump(movies_detail, stream)
    
# Load top_rated movies details and transform to dictionary
data_file = os.path.join(data_folder, 'top_rated_movies_details.json')
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

# Save top_rated movies synopsis
data_file = os.path.join(data_folder, 'top_rated_movies_synopsis.json')
with open(data_file, 'w') as stream:
    json.dump(synopsis, stream)
    
    
    
# Load top_rated movies synopsis
data_file = os.path.join(data_folder, 'top_rated_movies_synopsis.json')
with open(data_file, 'r') as stream:
    movies_synopsis_load = json.load(stream)
    
movies_synopsis_parsed = [(p[0], parse_corpus(p[1]))
                          for p in movies_synopsis_load]

# Save top_rated movies synopsis parsed
data_file = os.path.join(data_folder, 'top_rated_movies_synopsis_parsed.json')
with open(data_file, 'w') as stream:
    json.dump(movies_synopsis_parsed, stream)