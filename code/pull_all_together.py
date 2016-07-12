import os


def grab_data(path):
    return [i for i in os.listdir(path)]

def put_into_one_csv(path, paths, out):
    fout=open("../data/"+out,"a")
    # first file:
    for line in open(path+paths[0]):
        fout.write(line)
    # now the rest:
    for num in xrange(1, len(paths)):
        f = open(path+paths[num])
        f.next() # skip the header
        for line in f:
             fout.write(line)
        f.close() # not really needed
    fout.close()

def main():

    path = '../data/csvs/'
    paths = grab_data(path)
    put_into_one_csv(path, paths, "total_parsed_data")

    path = '../data/errors/'
    paths = grab_data(path)
    put_into_one_csv(path, paths, "total_errors")

    path = '../data/subsets/'
    paths = grab_data(path)
    put_into_one_csv(path, paths, "total_parsed_data_subset")




if __name__ == '__main__':
    main()
