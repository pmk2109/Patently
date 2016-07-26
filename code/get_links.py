

for elem in d.values():
    for item in elem:
        # print item
        item['link'] = "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&Sect2=HITOFF&d=PALL&p=1&u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&r=1&f=G&l=50&s1={0}.PN.&OS=PN/{0}&RS=PN/{0}".format(item['doc_number'][1:])
