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



ZIP_PATH = '../code'
EXTRACT_DATA_PATH = '../data'
DATA_PATH = '../data/ipg160628.xml'

url = 'http://patents.reedtech.com/pgrbft.php'



def get_data(url):
    '''
    DOCSTRING: get_data

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

    download(soup.select('a'))

    return



def download(iterable, n_items=None):
    counter = 0
    for link in iterable:
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

                # move_to_s3(unzipped_fname)

                # os.remove(EXTRACT_DATA_PATH + '/' + unzipped_fname)

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

        if n_items:
            counter+=1
            if counter >= n_items:
                return

    return






def move_to_s3(filename):
    '''
    DOCSTRING: move_to_s3

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
