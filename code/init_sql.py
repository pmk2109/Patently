from sqlalchemy import create_engine
import pandas as pd

class PatentDatabase:
   def __init__(self):
       self.engine = create_engine('postgresql://ubuntu:ubuntu@localhost/patent_db')

   def query_sql(self, SQL_statement):
       return pd.read_sql(SQL_statement,self.engine)

   def write_to_sql(self, df,table_name, drop_append = 'append'):
       df.to_sql(table_name, self.engine, if_exists=drop_append)
       print 'Succesfully wrote {} rows to the table {}'.format(df.shape[0], table_name)
