import os
import pandas as pd



def grab_data(path):
    return [i for i in os.listdir(path)]



def pull_monthly_to_csv(data_type):

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

    data_paths = grab_data(data_path)

    pull_monthly_to_csv('subsets')
    pull_monthly_to_csv('csvs')
    pull_monthly_to_csv('errors')



if __name__ == '__main__':
    main()
