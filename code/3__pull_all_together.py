import os
import pandas as pd
from multiprocessing import Pool

def grab_data(path):
    '''
    DOCSTRING: grab_data

    For specified path, return all files in path.

    Returns: List of file names as string
    '''
    return [i for i in os.listdir(path)]

def put_into_one_csv(path, paths, out):
    '''
    DOCSTRING: put_into_one_csv

    For path list (paths) and specified path to save, write to
    out file name.

    Returns: None
    '''
    fout=open("../data/"+out,"a")
    for line in open(path+paths[0]):
        fout.write(line)
    for num in xrange(1, len(paths)):
        f = open(path+paths[num])
        f.next() # skip the header data
        for line in f:
             fout.write(line)
        f.close()
    fout.close()


def pull_monthly_to_csv(data_type):
    '''
    DOCSTRING: pull_monthly_to_csv

    For the type of data (i.e. csvs, subsets, errors), read
    into a pandas dataframe and select common months.

    Save monthly dataframes into specified monthly data folders.

    Returns: None
    '''
    if data_type == 'csvs':
        data_path = '../data/total_parsed_data.csv'
    elif data_type == 'subsets':
        data_path = '../data/total_parsed_data_subset.csv'
    elif data_type == 'errors':
        data_path = '../data/total_errors.csv'
    else:
        return 0

    df = pd.read_csv(data_path)

    year_month = df.date.apply(lambda x: str(x)[:6])
    header =['doc_number', 'date', 'publication_type', 'patent_length',
            'title', 'abstract', 'description', 'claims']
    for ym in year_month.unique():
        df.to_csv('../data/'+data_type+'/monthly/'+ym+'.csv', header=header)

    return



def main():

    path = '../data/csvs/'
    paths = grab_data(path)
    put_into_one_csv(path, paths, "total_parsed_data")

    path = '../data/errors/'
    paths = grab_data(path)
    put_into_one_csv(path, paths, "total_errors")

    path = '../data/subsets/'
    paths = grab_data(path)
    put_into_one_csv(path, paths, "total_parsed_data_subset")

    p = Pool(2)
    type_list = ['subsets', 'csvs']
    results = p.map(pull_monthly_to_csv, type_list)


if __name__ == '__main__':
    main()
