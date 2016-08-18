import os
import pandas as pd
from multiprocessing import Pool
from init_sql import PatentDatabase
import string

def grab_data(path):
    '''
    DOCSTRING: grab_data(path)

    For specified path, return all files in path.

    Returns: List of file names as string
    '''
    return [i for i in os.listdir(path)]



def put_into_one_db(pdb, path, paths, out):
    '''
    DOCSTRING: put_into_one_db(path, paths, out)

    For path list (paths) and specified path to save, write to
    out table name.

    Returns: None
    '''
    # fout=open("../data/"+out,"a")
    # for line in open(path+paths[0]):
    #     fout.write(line)
    # for num in xrange(1, len(paths)):
    #     f = open(path+paths[num])
    #     f.next() # skip the header data
    #     for line in f:
    #          fout.write(line)
    #     f.close()
    # fout.close()
    if "errors" in path:
        for p in paths:
            df = pd.read_csv(path+p)
            pdb.write_to_sql(df, out)
        return

    else:

        for p in paths:
            df = pd.read_csv(path+p)
            df.fillna("", inplace=True)
            df['pruned_abst'] = [[y.lower().strip(string.punctuation) for y in w] for w in df.abstract.values]
	    df['pruned_abst_str'] = df.pruned_abst.apply(lambda x: "".join(x))
	    df['pruned_desc'] = [[y.lower().strip(string.punctuation) for y in w] for w in df.description.values]# if not w.isdigit()]
            df['pruned_desc_str'] = df.pruned_desc.apply(lambda x: "".join(x))
            df['flat_claims'] = [[e.strip(string.punctuation) for e in w.lower().split()] for w in df.claims.values]
            df['flat_claims_str'] = df.flat_claims.apply(lambda x: " ".join(x))
            df['total'] = df.pruned_abst_str + " " + df.pruned_desc_str + " " + df.flat_claims_str

            drop_cols = ['pruned_abst', 'pruned_abst_str', 'pruned_desc', 'pruned_desc_str', 'flat_claims', 'flat_claims_str']
            pdb.write_to_sql(df.drop(drop_cols, axis=1), out)

            #break #take this out when i run the full thing

        return



def pull_monthly_to_csv(data_type):
    '''
    DOCSTRING: pull_monthly_to_csv(data_type)

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


def create_index(table_name):

    s = '''
    CREATE SEQUENCE s{0};
    ALTER TABLE {0}
    ADD COLUMN new_idx int default nextval('s{0}');
    ALTER TABLE {0}
    DROP COLUMN index;
    ALTER TABLE {0}
    RENAME COLUMN new_idx TO index;
    '''.format(table_name)

    return s




def main(erase=False):

    pdb = PatentDatabase()
    erase=True
    if erase:
        try:
            pdb.engine.execute('DROP TABLE total_parsed_data;')
            pdb.engine.execute('DROP SEQUENCE stotal_parsed_data;')
        except:
            print "No total data table"
        try:
            pdb.engine.execute('DROP TABLE total_parsed_data_subset;')
            pdb.engine.execute('DROP SEQUENCE stotal_parsed_data_subset;')
        except:
            print "No subset data table"
        try:
            pdb.engine.execute('DROP TABLE total_errors;')
            pdb.engine.execute('DROP SEQUENCE stotal_errors;')
        except:
            print "No error data table"

    print "Pulling errors..."
    path = '../data/errors/'
    paths = grab_data(path)
    put_into_one_db(pdb, path, paths, "total_errors")
    pdb.engine.execute(create_index('total_errors'))

    print "Pulling subsets..."
    path = '../data/subsets/'
    paths = grab_data(path)
    put_into_one_db(pdb, path, paths, "total_parsed_data_subset")
    pdb.engine.execute(create_index('total_parsed_data_subset'))

    print "Pulling csvs..."
    path = '../data/csvs/'
    paths = grab_data(path)
    put_into_one_db(pdb, path, paths, "total_parsed_data")
    pdb.engine.execute(create_index('total_parsed_data'))



    # DON'T WORRY ABOUT MONTHLY FILE, I'LL JUST BE RUNNING ON TOTALS
    # p = Pool(2)
    # type_list = ['subsets', 'csvs']
    # results = p.map(pull_monthly_to_csv, type_list)


if __name__ == '__main__':
    main()
