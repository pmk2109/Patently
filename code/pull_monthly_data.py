import os
import pandas as pd



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

    pull_monthly_to_csv('subsets')
    pull_monthly_to_csv('csvs')
    pull_monthly_to_csv('errors')



if __name__ == '__main__':
    main()
