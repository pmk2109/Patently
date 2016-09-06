import pandas as pd
import numpy as np
import string
import sys
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer, TfidfTransformer
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import linear_kernel
import cPickle as pickle
import time
import msgpack
import os
from sklearn.pipeline import make_pipeline


def vectorize(text, tfidf=None):
    '''
    DOCSTRING: vectorize(text, tfidf=None)

    Given raw text, and the optional tfidf parameter, use TfidfVectorizer
    to vectorize text.  If tfidf parameter is present, use its vocab
    for the input text for relevant comparison.

    Returns: (fit_transformed text, tfidf object), (transformed text, __)
    '''
    #stemmer = SnowballStemmer('english')

    #processed_text = [" ".join([stemmer.stem(word) for word in words.split()]) for words in text]

    if tfidf:
        return tfidf.transform(text)
    elif tfidf is None:
        hasher = HashingVectorizer(stop_words='english', norm=None, non_negative=True)
        tfidf = make_pipeline(hasher, TfidfTransformer())
        return tfidf.fit_transform(text), tfidf



def get_similarity(vocab, idea, n_items=5):
    '''
    DOCSTRING: get_similarity(vocab, idea, n_items=5)

    For given vocab as tfidf sparse matrix and an input idea to test,
    check to make sure the sparse matrix column space is equal and
    use cosine similarity and n_items parameter to return the
    relevant cosine similarity scores and indices

    Returns: cosine similarity scores, indices
    '''
    if vocab.shape[1] == idea.shape[1]:
        pass
    else:
        print 'ERROR: shape mismatch'
        return

    cosine_similarity = vocab * idea.T
    cs_dense = np.array(cosine_similarity.todense())
    cs_array = np.array([float(i) for i in cs_dense])

    #indicate how many results to return... currently 10
    ind = np.argpartition(cs_array, -n_items)[-n_items:]

    #this prints out the top results (unsorted).. these are to be
    #transormed into scores

    sorted_ind = ind[np.argsort(cs_array[ind])][::-1]
    scores = cs_array[sorted_ind]
    indices = sorted_ind
    indices = np.array(indices)+1
    return scores, tuple(indices)




def unpickle():
    '''
    DOCSTRING: unpickle()

    Unpickle tfidf model, [abstract/total] tfidf matrix and unpack
    dataframe object.

    Returns: dataframe, [abstract/total] tfidf matrix, tfidf model
    '''
    path = os.path.dirname(__file__)
    total_tfidf = pickle.load(open(path+'/../data/total_tfidf.p', 'rb'))
    tfidf = pickle.load(open(path+'/../data/tfidf.p', 'rb'))
    # df = pd.read_msgpack(path+'/../data/dataframe.p')

    return total_tfidf, tfidf





def assemble_results(pdb, user_text, num_results, tfidf, matrix):
    '''
    DOCSTRING: assemble_results(user_text, num_results, tfidf, matrix, dataframe)

    For a given user text as a list of one element of type string,
    transform the text using the provided tfidf model and call the
    get_similarity function using the matrix, transformed user_text,
    and the number of results requested.

    Returns: results in a dictionary format
    '''
    new_text_tfidf = vectorize(user_text, tfidf)
    scores, indices = get_similarity(matrix, new_text_tfidf, num_results)

    '''
    [Index([u'doc_number', u'date', u'publication_type', u'patent_length', u'title',
       u'abstract', u'description', u'claims']
    '''

    s = '''
    SELECT index, doc_number, date, title, abstract FROM total_parsed_data
    WHERE index in {} ORDER BY index LIMIT 1000000;
    '''.format(indices)

    df = pdb.query_sql(s)
    df_scores = pd.DataFrame(zip(indices, scores), columns=['index', 'score'])

    df_joined = pd.merge(df, df_scores, how='inner', on='index')
    df_joined.drop(['index'], axis=1, inplace=True)
    df_sorted = df_joined.sort_values(by='score', axis=0, ascending=False)
    df_sorted.drop_duplicates(subset='title', keep='first', inplace=True)
    return df_sorted.to_dict(orient='records')
