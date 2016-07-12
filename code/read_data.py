#*************************************************#
#*************************************************#
#########         IGNORE ME                ########
#*************************************************#
#***************** always use pool ***************#



import re
import tinys3
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
import parmap



def define_data_path(filetype):
    # return [i for i in os.listdir('../data_'+filetype)]
    return [i for i in os.listdir('../data') if filetype in i]


def open_and_write(num_iters, filetype):
    DATA_PATH = define_data_path(filetype)
    print DATA_PATH
    header = ('doc_number', 'date', 'publication_type', 'patent_length',
            'title', 'abstract', 'description', 'claims')
    if num_iters == 'All':
        num_iters = len(DATA_PATH)
    if num_iters > 0 and len(DATA_PATH) >= num_iters:
        with open('../data/error_rates.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(('file', 'num_total', 'num_invalid', 'error_rate'))

        with open('../data/parsed_data.csv', 'w') as g:
            writer = csv.writer(g)
            writer.writerow(header)

            with open('../data/parsed_data_subset.csv', 'w') as k:
                writer_sub = csv.writer(k)
                writer_sub.writerow(header)

                for i in xrange(num_iters):
                    print "Loading data {}...".format(i+1)
                    data = open_files(DATA_PATH[i])
                    print "Writing data {}...".format(i+1)
                    write_data_to_csv(DATA_PATH[i], data, writer, writer_sub)

    else:
        print "ERROR: Number of files specified is 0 or greater" + \
                " than the number of files in path. --pk"



def open_files(path):

    #given the size of the list that is being created...
    #maybe i need to think about restructuring this so that
    #monthly csv's are stored...

    #read in file name, get the month, every file in that month
    #gets its own csv file... when i want to subset, i'll just
    #select fewer months .. otherwise something gets quite heavy
    #in my AWS instance


    #SECOND THOUGHT ---> run this so that each file gets opened,
    #and then appended into a csv such that the csv is opened,
    #files are iterated through

    endtag_regex = re.compile('^<!DOCTYPE (.*) SYSTEM')
    endtag = ''
    counter = 0
    doc_list = []

    # print "Opening file {}...".format(counter+1)
    # counter += 1
    with open('../data/'+path, 'r') as f:
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





def write_data_to_csv(path, data, writer, writer_sub):
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



        with open('../data/error_rates.csv', 'a') as h:
            writer_e = csv.writer(h)
            writer_e.writerow((path, str(total_counter), \
                            str(invalid_counter), \
                            str(invalid_counter/float(total_counter))))
        return 1
    except:
        return 0




def write_row(root):
    abstract = ""
    description = ""
    claims = []
    doc_number = ""
    date = ""
    publication_type = ""
    patent_length = ""
    title = ""

    for child in root:
        if child.tag == 'abstract':
            for c in child:
                try:
                    abstract = c.text.strip()
                except:
                    pass
                for e in c:
                    try:
                        abstract += " " + e.text.strip()
                    except:
                        pass

        elif child.tag == 'description':
            for c in child:
                try:
                    description = c.text.strip()
                except:
                    pass
        elif child.tag == 'claims':
            for c in child:
                # print c.tag, c.attrib
                for cs in c:
                    try:
                        holder = cs.text.strip()
                    except:
                        pass

                    for d in cs:
                        try:
                            holder += " " + d.text.strip()
                        except:
                            pass

                        for g in d:
                            try:
                                holder += " " + g.text.strip()
                            except:
                                pass
                    try:
                        claims.append(holder)
                    except:
                        pass


        for c in child:
            if c.tag == 'publication-reference':
                for e in c:
                    for a in e:
                        if a.tag == 'date':
                            try:
                                date = a.text.strip()
                            except:
                                pass
                        elif a.tag == 'doc-number':
                            try:
                                doc_number = a.text.strip()
                            except:
                                pass
                        elif a.tag == 'kind':
                            try:
                                publication_type = a.text.strip()
                            except:
                                pass
            if c.tag == 'us-term-of-grant':
                for e in c:
                    if e.tag == 'length-of-grant':
                        try:
                            patent_length = e.text.strip()
                        except:
                            pass

            elif c.tag == 'invention-title':
                try:
                    title = c.text.strip()
                except:
                    pass


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

    open_and_write(2, 'xml')

    # write_data_to_csv('All', 'xml')


if __name__ == '__main__':
    main()
