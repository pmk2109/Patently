import multiprocessing
import re
import zipfile
import csv
import boto3
import io
import zipfile
import os
from datetime import datetime
from urllib import urlopen, urlretrieve, quote
from urlparse import urljoin
from bs4 import BeautifulSoup
from multiprocessing import Pool

#assign paths to global variables
ZIP_PATH = '../code'
EXTRACT_DATA_PATH = '../data'
DATA_PATH = '../data/ipg160628.xml'

#this is the current repo of all available patents (1976-present)
url = 'http://patents.reedtech.com/pgrbft.php'


def get_data(url):
    '''
    DOCSTRING: get_data(url)

    Collect data from provided url (in this case Reed Tech) in the form
    of .zip files, extract and move to S3 Bucket named 'patentgrants'

    Returns: None
    '''

    with open('get_data_logfile.csv', 'wb') as csvfile:
        logwriter = csv.writer(csvfile, delimiter=',')
        logwriter.writerow(['filename', 'success', 'timestamp'])


    u = urlopen(url)
    try:
        html = u.read().decode('utf-8')
    finally:
        u.close()

    soup = BeautifulSoup(html)
    # p = Pool(40)
    # results = p.map(download, soup.select('a'))

    for link in soup.select('a'):
        download(link)
    #this works ... but keep in mind, this will be contrained by
    #network speeds rather than CPUs... so run on
    return



def download(link):
    '''
    DOCSTRING: download(link)

    For a given BeautifulSoup link, find .zip files
    on the Reed Tech site, retrieve them, extract them,
    and remove the original zip file from the HD.

    Store log data in a csv so that particular undownloaded /
    unextracted data can be targeted.

    Number of items to download can be specified.

    Returns: None
    '''

    counter = 0
    if link.text[-4:] == '.zip':
        href = link.get('href')
        filename = href.rsplit('/', 1)[-1]
        href = urljoin(url, quote(href))
        try:
            urlretrieve(href, filename)
            zip_ref = zipfile.ZipFile(ZIP_PATH+'/'+filename, 'r')
            zip_ref.extractall(EXTRACT_DATA_PATH)
            zip_ref.close()

            os.remove(filename)
            unzipped_fname = filename.split('.')[0] + '.xml'

            #write to csv if it succeeded
            log = open('get_data_logfile.csv','a')
            log.write(','.join([unzipped_fname, '1', str(datetime.now())+'\n']))
            log.close()

        except:
            print 'failed to download: {} @ {}'.format(filename,
                                                    datetime.now())
            log = open('get_data_logfile.csv','a')
            log.write(','.join([unzipped_fname, '0', str(datetime.now())+'\n']))
            log.close()

    return






def move_to_s3(filename):
    '''
    DOCSTRING: move_to_s3(filename)

    Move .zip files to S3.  Print to csv: timestamp, filename, success(1/0)

    Returns: None
    '''

    tmp_dir = '../data/'
    tmp_fname = filename

    target_bucket = 'patentgrants'
    s3 = boto3.resource('s3')

    try:
        s3.Object(target_bucket, tmp_fname).put(Body=open(tmp_dir + tmp_fname, 'rb'))
    except Exception as e:
        print e
    finally:
        return






def main():
    get_data(url)



if __name__ == '__main__':
    main()
