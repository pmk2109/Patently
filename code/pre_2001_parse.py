import pandas as pd
from collections import defaultdict


#Define variable for parsing
section_headers = ['PATN','INVT','ASSG','PRIR',
                   'REIS','CLAS','RLAP','LREP',
                   'UREF','FREF','OREF','ABST',
                   'GOVT','PARN','DRWD','DETD',
                   'CLMS']

col_name_mapping = {'ECL': 'Exemplary Claim Numbers',
 'UREF': 'US Reference',
 'OCL': 'US Classifcation',
 'EXA': 'Assistant Examiner',
 'PARN': 'Parent Case',
 'ASSG': 'Assingee',
 'NUM': 'Claims Number',
 'CTY': 'City',
 'NAM': 'Inventor Name',
 'CLMS': 'Claims Information',
 'ATT': 'Att Name',
 'FSC': 'Field of Search Class',
 'XCL': 'Cross Ref',
 'EXP': 'Primary Examiner',
 'RLAP': 'Related Application Data',
 'AGT': 'Agent Name',
 'PAL': 'Paragraph Info',
 'REG': 'Reg Num',
 'ISD': 'Issue Date',
 'ABST': 'Abstract Info',
 'PTN': 'Patent Bibliographic Information',
 'DCL': 'Digest Ref',
 'PRIR': 'Foreign Priority',
 'DRWD': 'Drawing Description',
 'DCD': 'Disclaimer Date',
 'INVT': 'Inventor',
 'DETD': 'Detail Description',
 'FR2': 'Prin Attr Name',
 'PA.': 'Paragraph Info',
 'TTL': 'Title of Invention',
 'APN': 'Prior App Num',
 'UCL': 'Unofficial Ref',
 'CLAS': 'Classification',
 'NFG': 'Number of Figures',
 'SRC': 'Series Code', 'CNT':
 'Country',
 'TRM': 'Term of Patent',
 'STA': 'State',
 'ZIP': 'Zip Code',
 'LREP': 'Legal Rep Info',
 'STM': 'Claims Statement',
 'FREF': 'Foreign Reference',
 'FRM': 'Firm Name',
 'STR': 'Street',
 'GOVT': 'Government Interest',
 'PBL': 'Publication Level',
 'NDR': 'Number of Drawing Sheets',
 'ART': 'Art Unit',
 'AAT': 'Ass Att Name',
 'PNO': 'Patent Number',
 'ICL': 'International Class',
 'REIS': 'Reissue Info',
 'APT': 'Application Type',
 'R47': 'Rule 47 Indicator',
 'FSS': 'Field of Search sub-class',
 'NCL': 'Number of Claims',
 'NPS': 'Number of Pages of Specifications',
 'ITX': ' Inventory Desc test',
 'PSC': 'Pat Status Code',
 'EDF': 'Edition Field',
 'WKU': 'Patent Number',
 'OREF': 'Other Prior Art Ref',
 'APD': 'Prior App Date',
 'COD': 'Reissue Code'}

pat_struct = {'Patent Number':str(),
'PATN':defaultdict(list),
'INVT':defaultdict(list),
'ASSG':defaultdict(list),
'PRIR':defaultdict(list),
'REIS':defaultdict(list),
'CLAS':defaultdict(list),
'RLAP':defaultdict(list),
'LREP':defaultdict(list),
'UREF':defaultdict(list),
'FREF':defaultdict(list),
'OREF':defaultdict(list),
'ABST':defaultdict(list),
'GOVT':defaultdict(list),
'PARN':defaultdict(list),
'DRWD':defaultdict(list),
'DETD':defaultdict(list),
'CLMS':defaultdict(list)
}

class Pre2001PatentParse:
    def __init__(self, file_, sec_headers, col_name_mapping):
        self.file_ = file_
        self.section_headers = sec_headers
        self.col_name_mapping = col_name_mapping

    def read_file_data(self):
        with open(self.file_, 'r') as f:
            curr_section = str()
            curr_pat_num = None
            current_pat_info = None
            for line in f:
                temp_head = line[0:5].replace('\r','').rstrip().lstrip()
                temp_line_info = line[5:].replace('\r','').rstrip().lstrip()

                if temp_head in self.section_headers:
                    curr_section = temp_head

                    if temp_head == 'PATN':
                        if current_pat_info == None:
                            current_pat_info = self.new_patent_dict()
                        else:
                            self.add_to_elastic_search(current_pat_info)
                            self.add_to_psql(current_pat_info)
                            current_pat_info = self.new_patent_dict()

                elif temp_head in self.col_name_mapping and temp_head not in self.section_headers:
                    if temp_head == 'WKU':
                        current_pat_info['Patent Number'] = temp_line_info
                        current_pat_info['PATN']['WKU'].append(temp_line_info)
                    elif temp_head.startswith('PA'):
                        current_pat_info[curr_section]['DESC'].append(temp_line_info)
                    else:
                        current_pat_info[curr_section][temp_head].append(temp_line_info)

    def new_patent_dict(self):
        new_pat = {'Patent Number':str(),
                'PATN':defaultdict(list),
                'INVT':defaultdict(list),
                'ASSG':defaultdict(list),
                'PRIR':defaultdict(list),
                'REIS':defaultdict(list),
                'CLAS':defaultdict(list),
                'RLAP':defaultdict(list),
                'LREP':defaultdict(list),
                'UREF':defaultdict(list),
                'FREF':defaultdict(list),
                'OREF':defaultdict(list),
                'ABST':defaultdict(list),
                'GOVT':defaultdict(list),
                'PARN':defaultdict(list),
                'DRWD':defaultdict(list),
                'DETD':defaultdict(list),
                'CLMS':defaultdict(list)
                }
        return new_pat

    def add_to_elastic_search(self, pat_dict):
        #Need to import and write code to insert into elastic search DB
        pass

    def add_to_psql(self, pat_dict):
        """Need to write code to append abstract, description & claims info and
        and insert into psql for tf-idf
        """
        pass

if __name__ == '__main__':
    test_run = Pre2001PatentParse('pftaps19990413_wk15.txt', section_headers, col_name_mapping)
    test_run.read_file_data()
    print test_run.test_es
