import re
import xml.etree.ElementTree as ET
from urllib import urlopen, urlretrieve, quote
from urlparse import urljoin
from bs4 import BeautifulSoup
import zipfile
import csv
import boto3
import ftplib
import gzip
import io
import zipfile
import os
from datetime import datetime
import cPickle as pickle
from multiprocessing import Pool
import time



def define_data_path(filetype):
    '''
    DOCSTRING: define_data_path(filetype)

    For specified filetype, return all files in 'data/' path.

    Returns: List of file names as string
    '''
    return [i for i in os.listdir('../data_'+filetype)]


def open_and_write_xml(path):
    '''
    DOCSTRING: open_and_write_xml(path)

    Establish error, subset and total data csvs.
    Call open_files_xml function and write_xml_data_to_csv function.

    Returns: None
    '''
    header = ('doc_number', 'date', 'publication_type', 'patent_length',
            'title', 'abstract', 'description', 'claims')

    with open('../data/errors/error_rate_'+path[:-4]+'.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('file', 'num_total', 'num_invalid', 'error_rate'))

    with open('../data/csvs/parsed_data_'+path[:-4]+'.csv', 'w') as g:
        writer = csv.writer(g)
        writer.writerow(header)

        with open('../data/subsets/parsed_data_subset_'+path[:-4]+'.csv', 'w') as k:
            writer_sub = csv.writer(k)
            writer_sub.writerow(header)


            print "Loading data xml {}...".format(path)
            data = open_files_xml(path)
            print "Writing data xml {}...".format(path)
            write_xml_data_to_csv(path, data, writer, writer_sub)




def open_and_write_pg(path):
    '''
    DOCSTRING: open_and_write_pg(path)

    Establish error, subset and total data csvs.
    Call open_files_pg function and write_pg_data_to_csv function.

    Returns: None
    '''
    header = ('doc_number', 'date', 'publication_type', 'patent_length',
            'title', 'abstract', 'description', 'claims')

    with open('../data/errors/error_rate_'+path[:-4]+'.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('file', 'num_total', 'num_invalid', 'error_rate'))

    with open('../data/csvs/parsed_data_'+path[:-4]+'.csv', 'w') as g:
        writer = csv.writer(g)
        writer.writerow(header)

        with open('../data/subsets/parsed_data_subset_'+path[:-4]+'.csv', 'w') as k:
            writer_sub = csv.writer(k)
            writer_sub.writerow(header)

            print "Loading data pg {}...".format(path)
            data = open_files_pg(path)
            print "Writing data pg {}...".format(path)
            write_pg_data_to_csv(path, data, writer, writer_sub)





def open_files_xml(path):
    '''
    DOCSTRING: open_files_xml(path)

    For specified path, use regex to parse .xml files within
    the total collection of xml files per file in path.

    Returns: List of xml docs.
    '''
    endtag_regex = re.compile('^<!DOCTYPE (.*) SYSTEM')
    endtag = ''
    counter = 0
    doc_list = []

    with open('../data_xml/'+path, 'r') as f:
        doc = []  # (re)initialize current XML doc to empty string
        for line in f:
            doc.append(line)
            endtag = endtag_regex.findall(line) if not endtag else endtag
            if not endtag:
                continue
            terminate = re.compile('^</{0}>'.format(endtag[0]))
            if terminate.findall(line):
                doc_list.append(doc)
                doc = []

        return doc_list






def open_files_pg(path):
    '''
    DOCSTRING: open_files_pg(path)

    For specified path, use regex to parse .xml files within
    the total collection of xml files per file in path.

    Returns: List of xml docs.
    '''
    endtag_regex = re.compile('^<!DOCTYPE (.*) SYSTEM')
    endtag = ''
    counter = 0
    doc_list = []

    with open('../data_pg/'+path, 'r') as f:
        doc = []  # (re)initialize current XML doc to empty string
        for line in f:
            doc.append(line)
            endtag = endtag_regex.findall(line) if not endtag else endtag
            if not endtag:
                continue
            terminate = re.compile('^</{0}>'.format(endtag[0]))
            if terminate.findall(line):
                doc_list.append(doc)
                doc = []

        return doc_list





def write_pg_data_to_csv(path, data, writer, writer_sub):
    '''
    DOCSTRING: write_pg_data_to_csv(path, data, writer, writer_sub)

    Take data from open_files_xml result and iterate over
    xml docs, converting to string and using BeautifulSoup to
    establish a parsing element.  Hunt for relevant information through
    loops and retain data in variables.

    Make sure encoding is valid and count how mant invalid xml
    docs there are.  Write to the error, csvs and subset csv files.
    Subset is every 14th item.

    Returns: 1 if successful, 0 if failure.
    '''
    try:
        total_counter, invalid_counter = 0, 0
        for d in data:
            total_counter += 1
            data_as_string = "".join(data[i])
            try:
                soup = BeautifulSoup(data_as_string)
            except:
                counter += 1
                soup = None

            if soup is not None:
                row = write_row_pg(soup)
                writer.writerow(row)

                if total_counter % 14 == 0:
                    writer_sub.writerow(row)



        with open('../data/errors/error_rate_'+path[:-4]+'.csv', 'a') as h:
            writer_e = csv.writer(h)
            writer_e.writerow((path, str(total_counter), \
                            str(invalid_counter), \
                            str(invalid_counter/float(total_counter))))
        return 1
    except:
        return 0






def write_row_pg(soup):
    '''
    DOCSTRING: write_row_pg(soup)

    For specified root, hunt for particular data in the patent space.

    Returns: row of data as tuple
    '''
    abstract = ""
    description = ""
    claims = []
    doc_number = ""
    date = ""
    publication_type = ""
    patent_length = ""
    title = ""


    doc_number = soup.find('b110').text
    date = soup.find('b140').text
    publication_type = soup.find('b130').text

    if soup.find('sdoab') is not None:
        abstract = " ".join(soup.find('btext').text.split('\n'))
    else:
        abstract = ""

    if soup.find('sdode') is not None:
        for elem in soup('sdode'):
            description += " ".join(elem.text.split('\n'))
    else:
        description = ""

    title = soup.find('b540').text

    if soup.find('sdocl') is not None:
        for elem in soup('sdocl'):
            claims.append(" ".join(elem.text.split('\n')))
    else:
        claims = []


    row = doc_number, date, publication_type, patent_length, \
        title, abstract, description, claims

    new_row = []
    claim_elem = []

    for elem in row[:-1]:
        new_elem = elem.encode('ascii', 'ignore')
        new_row.append(new_elem)

    for elem in claims:
        new_elem = elem.encode('ascii', 'ignore')
        claim_elem.append(new_elem)
    new_row.append(claim_elem)

    return tuple(new_row)








def write_xml_data_to_csv(path, data, writer, writer_sub):
    '''
    DOCSTRING: write_xml_data_to_csv(path, data, writer, writer_sub)

    Take data from open_files_xml result and iterate over
    xml docs, converting to string and using ElementTree to
    establish a root node.  Hunt for relevant information through
    loops and retain data in variables.

    Make sure encoding is valid and count how mant invalid xml
    docs there are.  Write to the error, csvs and subset csv files.
    Subset is every 14th item.

    Returns: 1 if successful, 0 if failure.
    '''
    try:
        total_counter, invalid_counter = 0, 0
        for d in data:
            total_counter += 1
            data_as_string = "".join(d)
            try:
                root = ET.fromstring(data_as_string)
            except:
                invalid_counter += 1
                root = None

            if root is not None:
                row = write_row(root)
                writer.writerow(row)

                if total_counter % 14 == 0:
                    writer_sub.writerow(row)



        with open('../data/errors/error_rate_'+path[:-4]+'.csv', 'a') as h:
            writer_e = csv.writer(h)
            writer_e.writerow((path, str(total_counter), \
                            str(invalid_counter), \
                            str(invalid_counter/float(total_counter))))
        return 1
    except:
        return 0




def write_row(root):
    '''
    DOCSTRING: write_row(root)

    For specified root, hunt for particular data in the patent space.

    Returns: row of data as tuple
    '''
    abstract = ""
    description = ""
    claims = ""
    doc_number = ""
    date = ""
    publication_type = ""
    patent_length = ""
    title = ""

    for child in root:
        if child.tag == 'abstract':
            for c in child:
                abstract = "".join([x for x in c.itertext()])
        elif child.tag == 'description':
            for c in child:
                description = "".join([x for x in c.itertext()])
        elif child.tag == 'claims':
            for c in child:
                claims = "".join([x for x in c.itertext()])


        for c in child:
            if c.tag == 'publication-reference':
                for e in c:
                    for a in e:
                        if a.tag == 'date':
                            date = a.text.strip()
                        elif a.tag == 'doc-number':
                            doc_number = a.text.strip()
                        elif a.tag == 'kind':
                            publication_type = a.text.strip()


            if c.tag == 'us-term-of-grant':
                for e in c:
                    if e.tag == 'length-of-grant':
                        patent_length = e.text.strip()
            elif c.tag == 'invention-title':
                title = "".join([x for x in c.itertext()])




    row = doc_number, date, publication_type, patent_length, \
            title, abstract, description, claims

    new_row = []
    claim_elem = []


    for elem in row[:-1]:
        new_elem = elem.encode('ascii', 'ignore')
        new_row.append(new_elem)

    for elem in claims:
        new_elem = elem.encode('ascii', 'ignore')
        claim_elem.append(new_elem)
    new_row.append(claim_elem)

    return tuple(new_row)





def main():

    filetype = 'xml'
    DATA_PATH = define_data_path(filetype)
    num_iters = 'All'
    if num_iters == 'All':
        num_iters = len(DATA_PATH)
    if num_iters > 0 and len(DATA_PATH) >= num_iters:

        tic = time.clock()
        p = Pool(40) #change cores depending on machine being used
        results = p.map(open_and_write_xml, DATA_PATH[:num_iters])
        print "Pooled: ", time.clock()-tic



if __name__ == '__main__':
    main()
