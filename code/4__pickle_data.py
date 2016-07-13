import pandas as pd
import cPickle as pickle

def load_data(path=None):
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



def main():
    df, abstracts, descriptions, claims = load_data('subset')

    df.to_pickle('../data/loaded_data/dataframe.p')
    pickle.dump(abstracts, open('../data/loaded_data/abstracts.p', 'wb'))
    pickle.dump(descriptions, open('../data/loaded_data/descriptions.p', 'wb'))
    pickle.dump(claims, open('../data/loaded_data/claims.p', 'wb'))


if __name__ == '__main__':
    main()
