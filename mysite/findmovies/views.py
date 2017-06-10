from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import json
import requests
import itertools
from bs4 import BeautifulSoup

config = getattr(settings, "CONFIG", None)

# Create your views here.

def index(request):
    hello_world = 'Hello World!'
    
    context = {
        'hello_world': hello_world,
    }
    return render(request, 'index.html', context)



def search_movies(request):
    query = request.GET.get('query', '')
    page = request.GET.get('page', '1')
    results = search_movies_api(query, page)
    print(results)
    return HttpResponse(json.dumps(results))



def get_reference_movie_imdb_id(request):
    movie_id = request.GET.get('movie_id', '')
    imdb_id = crawl_movies_detail(movie_id)['imdb_id']
    
    try:
        synopsis = crawl_imdb_synopsis(imdb_id)

        if any(c.isalpha() for c in synopsis):
            return HttpResponse(json.dumps(imdb_id))
        else:
            return HttpResponse(json.dumps(-1))
    except:
        return HttpResponse(json.dumps(-1))


    
"""
def search_similar_movies(request):
    ref_imdb_id r =equest.GET.get('ref_imdb_id', '')
    movies_pool = request.GET.get('movies_pool', '')
    
    ref_synopsis = crawl_imdb_synopsis(ref_imdb_id)
    
    url = 'https://best-movie-for-you.firebaseio.com/{}_synopsis.json?print=pretty'.format(movies_pool)
    r = requests.get(url)
    db_movies_synopsis = json.loads(r.content.decode("utf-8") )
    
    url = 'https://best-movie-for-you.firebaseio.com/{}_details.json?print=pretty'.format(movies_pool)
    r = requests.get(url)
    db_movies_details = json.loads(r.content.decode("utf-8") )
    
    def gen_all_similarity_scores(ref_synopsis, db_movies_synopsis):
        for movie_id, tar_synopsis in db_movies_synopsis.items():
            yield (movie_id, cal_similarity(ref_synopsis, tar_synopsis))
    similarity_scores = list(gen_all_similarity_scores(ref_synopsis, db_movies_synopsis))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    top_ten_movies = [dict([('id', p[0]),
                            ('poster_path', db_movies_details[p[0]]['poster_path'])])
                      for p in similarity_scores[0:10]]
    
    return HttpResponse(json.dumps(top_ten_movies))
"""

def search_similar_movies(request):
    
    ref_imdb_id = request.GET.get('ref_imdb_id', '')
    movies_pool = request.GET.get('movies_pool', '')
    
    ref_synopsis = crawl_imdb_synopsis(ref_imdb_id)
    
    
    from multiprocessing import Pool
    N = 10 # number of threads
    
    
    url = 'https://best-movie-for-you.firebaseio.com/{}_synopsis.json?print=pretty'.format(movies_pool)
    r = requests.get(url)
    db_movies_synopsis = json.loads(r.content.decode("utf-8") )
    
    url = 'https://best-movie-for-you.firebaseio.com/{}_details.json?print=pretty'.format(movies_pool)
    r = requests.get(url)
    db_movies_details = json.loads(r.content.decode("utf-8") )
        
        
    p = Pool(N)
    similarity_scores = p.map(gen_all_similarity_scores, list(itertools.zip_longest([],
                              db_movies_synopsis.items(), fillvalue=ref_synopsis)))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    top_ten_movies = [dict([('id', p[0]),
                            ('poster_path', db_movies_details[p[0]]['poster_path'])])
                      for p in similarity_scores[0:10]]
    
    return HttpResponse(json.dumps(top_ten_movies))

# ----------------------------------------------
"""
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
"""

    
    
def search_movies_api(query, page):
    
    var = {
        'api_key': config['api_key'],
        'language': 'en-US',
        'query': query,
        'page': page,
        'include_adult': 'false',
    }
    
    url_stem = 'https://api.themoviedb.org/3/search/movie?'
    url_var = '&'.join(
        ['{}={{{}}}'.format(key, key) for key in list(var.keys())])
    url = url_stem + url_var
    
    r = requests.get(url.format(**var))
    j = json.loads(r.content.decode("utf-8") )
    total_pages = j['total_pages']
    results = j['results']
    results = [{'title': d['title'], 'poster_path': d['poster_path'], 'id': d['id']} for d in results]
    
    return {'query': query, 'results': results, 'total_pages': total_pages}



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



def crawl_imdb_synopsis(imdb_id):
    
    url = 'http://www.imdb.com/title/{}/synopsis'.format(imdb_id)
    
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    node = soup.select('div#swiki.2.1')[0]
    
    return node.get_text()



def parse_corpus(corpus):
    
    import nltk
    from nltk import wordpunct_tokenize
    from nltk.corpus import stopwords
    from nltk.stem.porter import PorterStemmer
    #from nltk.tag.stanford import StanfordNERTagger
    from nltk.tag import pos_tag
    import string
    import itertools
    
    """
    commonWords = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'I', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when'\
, 'your', 'can', 'said', 'there', 'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'mo\
re', 'write', 'go', 'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part']
    listOfCharToExclude = ['.', ',', ':', '"', '+', '!', '?', '/', "'", '*', '(', ')', '$', '@', '&', '*',']','[']
    """
    stopwords = set(stopwords.words('english'))
    stopwords.update(string.punctuation)
    stopwords.update([p[0] + p[1] for p in itertools.product(string.punctuation, string.punctuation)])
    #stopwords.update(commonWords)
    #stopwords.update(listOfCharToExclude)
    
    #st = StanfordNERTagger('/home/orange63/TextMining/Project2/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz',
    #                       '/home/orange63/TextMining/Project2/stanford-ner-2014-06-16/stanford-ner-3.4.jar')
    porter = PorterStemmer()
    
    corpus_token = wordpunct_tokenize(corpus)
    corpus_token = [word for word in corpus_token if word not in stopwords]
    #corpus_no_people = [p[0] for p in filter(lambda x: x[1] != 'PERSON', st.tag(corpus_token))]
    corpus_NN = [p[0] for p in filter(lambda x: (x[1] == 'NN') or (x[1] == 'NNP'), pos_tag(corpus_token))]
    corpus_stem = [porter.stem(word) for word in corpus_NN]
    
    return ' '.join(corpus_stem)



def cal_similarity(corpus1, corpus2):
    
    from sklearn.feature_extraction.text import CountVectorizer
    import scipy
    
    doc = [parse_corpus(corpus1), parse_corpus(corpus2)]
    
    count = CountVectorizer(ngram_range=(1, 1))
    count.fit(doc)
    
    doc_bag = count.transform(doc)
    
    dot_product = scipy.sparse.csr_matrix.multiply(doc_bag[0], doc_bag[1])
    
    len(count.vocabulary_) ** 2.0
    
    return scipy.sparse.csr_matrix.sum(dot_product) / (len(count.vocabulary_) ** 2)



# multithreads func
def gen_all_similarity_scores(task):
    ref_synopsis = task[0]
    tar_movie_id = task[1][0]
    tar_synopsis = task[1][1]
    return (tar_movie_id, cal_similarity(ref_synopsis, tar_synopsis))