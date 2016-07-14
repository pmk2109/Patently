import pandas as pd
import numpy as np
import string
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import linear_kernel
import cPickle as pickle
import time
import msgpack
import gensim, logging
from nltk.corpus import stopwords

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


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


    df['flat_claims'] = [[e.strip(string.punctuation) for e in w.lower().split()] for w in df.claims.values]
    df['flat_claims_str'] = df.flat_claims.apply(lambda x: " ".join(x))
    df['total'] = df.abstract + " " + df.description + " " + df.flat_claims_str


    return df



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
    sorted_ind = ind[np.argsort(cs_array[ind])][::-1]
    scores = cs_array[sorted_ind]
    indices = sorted_ind


    return scores, indices




def main():

    tic = time.clock()
    try:
        path = sys.argv[1]
    except:
        print "ERROR: Specify data type [subset/total]"
        return

    try:
        pkl = sys.argv[2]
    except:
        print "ERROR: Specify pickle behavior [True/False]"
        return


    if pkl == 'True':
        try:
            print 'Loading data...'
            df = load_data(path)
            total_tfidf, tfidf = vectorize(df.total.values)

        except:
            print 'Error loading data!'
            return

        print 'Pickling data...'

        # think about writing a pickle function that loops
        # over a set of items passed in

        pickle.dump(total_tfidf, open('../data/total_tfidf.p', 'wb'))
        pickle.dump(tfidf, open('../data/tfidf.p', 'wb'))
        df.to_msgpack('../data/dataframe.p')
        print 'Finished pickling...'

    elif pkl == 'False':
        print 'Unpickling data...'
        total_tfidf = pickle.load(open('../data/total_tfidf.p', 'rb'))
        tfidf = pickle.load(open('../data/tfidf.p', 'rb'))
        df = pd.read_msgpack('../data/dataframe.p')
    else:
        print "Second argument to pickle must be [True/False]"
        return

    toc = time.clock()
    print 'User input (hardcoded)'
    text = 'Blood coagulation cold plasma device that kills bacteria'
    new_text_tfidf = vectorize([text], tfidf)

    print 'Getting similarity...'
    scores, indices = get_similarity(total_tfidf, new_text_tfidf, 5)

    '''
    [Index([u'doc_number', u'date', u'publication_type', u'patent_length', u'title',
       u'abstract', u'description', u'claims']
    '''
    df_results = df.loc[indices][['doc_number', 'date', 'title', 'abstract']]
    df_results['score'] = scores
    print df_results
    print time.clock() - tic








    return


if __name__ == '__main__':
    main()
