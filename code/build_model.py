import pandas as pd
import numpy as np
import string
import sys
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer, TfidfTransformer
from sklearn.pipeline import make_pipeline
from collections import defaultdict, Counter
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import linear_kernel
import cPickle as pickle
import time
import msgpack
from nltk.corpus import stopwords
from init_sql import PatentDatabase

def load_data_sql():
    pdb = PatentDatabase()
    return pdb





def load_data(path=None):
    '''
    DOCSTRING: load_data(path=None)

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

    df['pruned_desc'] = [w.lower().strip(string.punctuation) for w in df.description.values]# if not w.isdigit()]
    df['pruned_desc_str'] = df.pruned_desc.apply(lambda x: " ".join(x))
    df['flat_claims'] = [[e.strip(string.punctuation) for e in w.lower().split()] for w in df.claims.values]
    df['flat_claims_str'] = df.flat_claims.apply(lambda x: " ".join(x))
    df['total'] = df.abstract + " " + df.pruned_desc_str + " " + df.flat_claims_str


    return df



def vectorize(text, tfidf=None, vocabulary=None):
    '''
    DOCSTRING: vectorize(text, tfidf=None)

    Given raw text, and the optional tfidf parameter, use TfidfVectorizer
    to vectorize text.  If tfidf parameter is present, use its vocab
    for the input text for relevant comparison.

    Returns: (fit_transformed text, tfidf object), (transformed text, __)
    '''


    print "Set up vectorizer..."
    #stemmer = SnowballStemmer('english')
    #processed_text = [" ".join([stemmer.stem(word) for word in words.split()]) for words in text]

    if tfidf:
        return tfidf.transform(text)
    elif tfidf is None:
	tfidf = TfidfVectorizer(stop_words='english', vocabulary=vocabulary)#,
                #ngram_range=(1,2))
        #print tfidf
        #hasher = HashingVectorizer(stop_words='english', norm=None, non_negative=True)
        #tfidf = make_pipeline(hasher, TfidfTransformer())

        print "Get into vectorizer..."
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
    #print indices
    indices = np.array(indices)+1
    #print indices

    return scores, tuple(indices)




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

	print 'Loading data...'
        # df = load_data(path)
        # pdb = load_data_sql()

        pdb = PatentDatabase()
        print "Getting from DB"
        df = pdb.query_sql('''SELECT total FROM total_parsed_data;''')
        print "Length of df...{}".format(len(df.total.values))

        print "Build vocab..."
        d = defaultdict(int)
        dummy = 0
        for words in df.total.values:
            dummy += 1
            if dummy % 10000 == 0:
                print "Length of vocab at total {}: {}".format(dummy, len(d))
            for word in words.split():
                d[word] += 1

        c = Counter(d)
        vocab_list = []
        for item in c.most_common(600000):
            vocab_list.append(item[0])


        #Remove dupes
        #try getting a set for df.total.values... this ought to trim exact dupes
        #another method may be getting titles and their respective indices,
        #   then running a set on that and grabbing the resulting indices from
        #   the total, rather than the full SELECT total...
        


        print "Putting in vectorizer..."
        total_tfidf, tfidf = vectorize(df.total.values, vocabulary=vocab_list)



        print 'Pickling data...'

        pickle.dump(total_tfidf, open('../data/total_tfidf.p', 'wb'))
        pickle.dump(tfidf, open('../data/tfidf.p', 'wb'))
        # df.to_msgpack('../data/dataframe.p')
        print 'Finished pickling...'

    elif pkl == 'False':
        pdb = PatentDatabase()
        print 'Unpickling data...'
        total_tfidf = pickle.load(open('../data/total_tfidf.p', 'rb'))
        tfidf = pickle.load(open('../data/tfidf.p', 'rb'))
        # df = pd.read_msgpack('../data/dataframe.p')
    else:
        print "Second argument to pickle must be [True/False]"
        return

    print 'User input (hardcoded)'
    text = 'Blood coagulation cold plasma device that kills bacteria'
    new_text_tfidf = vectorize([text], tfidf)

    print 'Getting similarity...'
    scores, indices = get_similarity(total_tfidf, new_text_tfidf, 5)

    '''
    [Index([u'doc_number', u'date', u'publication_type', u'patent_length', u'title',
       u'abstract', u'description', u'claims']
    '''
    # df_results = df.loc[indices][['doc_number', 'date', 'title', 'abstract']]
    # df_results['score'] = scores
    # print df_results


    #takes subset 5min to get to pickling..
    #takes subset 8min to finish

    #by this measure this should be 5*14=70min to get to pickling
    #and 8*14=113min to finish
    s = '''
    SELECT index, doc_number, date, title, abstract FROM total_parsed_data
    WHERE index in {};
    '''.format(indices)
    #print indices
    df = pdb.query_sql(s)
    #print df.title.values
    df_scores = pd.DataFrame(zip(indices, scores), columns=['index', 'score'])

    df_joined = pd.merge(df, df_scores, how='inner', on='index')
    df_joined.drop(['index'], axis=1, inplace=True)
    print df_joined.sort_values(by='score', axis=0, ascending=False)




if __name__ == '__main__':
    main()
