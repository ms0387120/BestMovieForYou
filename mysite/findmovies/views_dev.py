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
    def gen_top_ten_movies(similarity_scores):
        output_number = 0
        for p in similarity_scores:
            try:
                yield dict([('id', p[0]), ('poster_path', db_movies_details[p[0]]['poster_path'])])
                output_number += 1
                if output_number == 10:
                    break
            except:
                pass
    top_ten_movies = list(gen_top_ten_movies(similarity_scores))
    
    return HttpResponse(json.dumps(top_ten_movies))


# ----------------------------------------------
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