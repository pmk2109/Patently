from  elasticsearch import Elasticsearch
from init_sql import PatentDatabase
import pandas as pd

class PatentlyElasticSearch():
    def __init__(self, index_name = 'patents', doc_types = 'patent_corpus'):
        self.index_name = index_name
        self.doc_types = doc_types
        self.pdb = PatentDatabase()
        self.es = Elasticsearch()

    def test_index(self):
        test_lines = 10
        for line in range(test_lines):
            test_query = "SELECT * FROM total_parsed_data OFFSET {} LIMIT 1;".format(line)
            test_df = self.pdb.query_sql(test_query)
            df_to_json = test_df.to_dict(orient='records')
            print df_to_json[0]
            self.es.index(index = self.index_name, 
                                  doc_type = self.doc_types, 
                                  id=df_to_json[0]['doc_number'], 
                                  body=df_to_json[0])

    def full_index_build_from_psql(self, chunk_size = 1000):
        patent_count = self.pdb.query_sql('SELECT COUNT(*) FROM total_parsed_data;')
        #iterate through database to pull in patent info in chunks
        for line in range(0, patent_count+1, 1000):
            index_query = """SELECT * FROM total_parsed_data OFFSET {} LIMIT {};""".format(line, chunk_size)
            patent_df = self.pdb.query_sql(index_query)
            dict_pat_df = patent_df.to_dict(orient='records')

            #iterate through chunks and add to the index
            for num, item in enumerate(dict_pat_df):
                self.es.index(index = self.index_name, 
                              doc_type= self.doc_types, 
                              id=item['doc_number'], 
                              body=item)

    def retrieve_all_patent_info(self):
        return self.es.search(index = self.index_name)
    
    def search_specific_patents(self, patent_number):
        return self.es.get(index = self.index_name, id = patent_number)

if __name__ == '__main__':
    pat_es = PatentlyElasticSearch()
    #pat_es.test_index()
    #print pat_es.retrieve_all_patent_info()
    for pat in ['D0472363','D0472364']:
        print pat_es.search_specific_patents(pat)
