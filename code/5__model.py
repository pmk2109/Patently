import pandas as pd
import numpy as np
import string
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import linear_kernel
import cPickle as pickle


# def load_pickle():
#     df = pickle.load(open('../data/loaded_data/dataframe.p', 'rb'))
#     abstracts = pickle.load(open('../data/loaded_data/abstracts.p', 'rb'))
#     descriptions = pickle.load(open('../data/loaded_data/descriptions.p', 'rb'))
#     claims = pickle.load(open('../data/loaded_data/claims.p', 'rb'))
#
#     return df, abstracts, descriptions, claims


def load_data(path=None):
    '''
    DOCSTRING: load_data

    Given the 'subset' or 'total' parameter, find the respective .csv file,
    read into a csv, parse out relevant fields and pickle the relevant objects.

    Returns: Dataframe object, abstracts array, descriptions array, claims array
    '''
    if path == 'subset':
        path = '../data/total_parsed_data_subset.csv'
    elif path == 'total':
        path = '../data/total_parsed_data.csv'
    else:
        print "ERROR: pass a valid path to data as a parameter"
        return

    df = pd.read_csv(path)
    df.fillna("", inplace=True)


    abstracts = df.abstract.values
    descriptions = df.description.values
    claims = df.claims.values

    return df, abstracts, descriptions, claims




def vectorize(text, tfidf=None):
    '''
    DOCSTRING: vectorize

    Given raw text, and the optional tfidf parameter, use TfidfVectorizer
    to vectorize text.  If tfidf parameter is present, use its vocab
    for the input text for relevant comparison.

    Returns: (fit_transformed text, tfidf object), (transformed text, __)
    '''
    if tfidf:
        return tfidf.transform(text)
    elif tfidf is None:
        tfidf = TfidfVectorizer(stop_words='english')
        return tfidf.fit_transform(text), tfidf



def get_similarity(vocab, idea, n_items=5):
    '''
    DOCSTRING: get_similarity

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
    scores = cs_array[ind]
    indices = ind

    return scores, indices




def main():

    df, abstracts, descriptions, claims = load_data('subset')

    abstracts_tfidf, tfidf = vectorize(abstracts)

    text = ['Blood coagulation cold plasma device that kills bacteria']
    new_text_tfidf = vectorize(text, tfidf)

    scores, indices = get_similarity(abstracts_tfidf, new_text_tfidf, 5)

    '''
    [Index([u'doc_number', u'date', u'publication_type', u'patent_length', u'title',
           u'abstract', u'description', u'claims']
    '''
    print df.loc[indices][['doc_number', 'date', 'title', 'abstract']]



if __name__ == '__main__':
    main()
