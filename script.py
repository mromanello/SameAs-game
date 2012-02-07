import urllib
import random
from xml.etree.ElementTree import ElementTree,fromstring

global input_file
input_file = "bios.txt"

def format_perseus_uri(i_string):
    prefix = "http://data.perseus.org/people/smith:"
    return "%s%s"%(prefix,i_string)

def get(url):
    print "...fetching  <%s>"%url
    return  urllib.urlopen(url).read()
    
def parse_xml(input):
	tree = fromstring(input)
	el = tree.find(".//head//persName")
	print list(el.iter("surname"))[0].text	
	
try:
    f = open(input_file,"r")
    data = f.read().split("\n")
    random.shuffle(data)
    f.close()
    print "There are %i Smith IDs in the input list..."%len(data)
    
    for n in range(1):
        print data[n]
        test_url = format_perseus_uri(data[n])
        xml = get(test_url)
        print parse_xml(xml)

except IOError:
    print "this time didn't work"
