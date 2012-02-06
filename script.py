import urllib
import random

def format_perseus_uri(i_string):
    prefix = "http://data.perseus.org/people/smith:"
    return "%s%s"%(prefix,i_string)

def get(url):
    print "...fetching  <%s>"%url
    return  urllib.urlopen(url).read()

try:
    f = open("./bios.txt","r")
    data = f.read().split("\n")
    random.shuffle(data)
    f.close()
    print "There are %i Smith IDs in the input list..."%len(data)
    print get(format_perseus_uri("caesar-1"))

    for n in range(10):
        print data[n]
        test_url = format_perseus_uri(data[n])
        print "<%s>"%get(test_url)

except IOError:
    print "this time didn't work"
