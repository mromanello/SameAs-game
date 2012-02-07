import urllib
import random
from xml.etree.ElementTree import ElementTree,fromstring
from lxml import etree
try:
	from gensim import corpora, models, similarities
except ImportError:
	print 'gensim library not found: try sudo easy_install gensim\n'
	gensim = None
	raise ImportError
	
"""
author: Matteo Romanello, <matteo.romanello@kcl.ac.uk>
"""

global input_file
input_file = "bios.txt"

def do_lookup(seed,query_limit = 5):
	"""
	Do a DBPedia lookup via its API.
	"""
	results = []
	lookup_url = "http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryString=%s&MaxHits=%i"%(seed,query_limit)
	return get(lookup_url)
	
def format_perseus_uri(i_string):
	"""
	Given an input ID, creates a URI compliant with the scheme defined by Perseus
	"""
	prefix = "http://data.perseus.org/people/smith:"
	return "%s%s"%(prefix,i_string)

def get(uri):
	"""
	Retrieves the URI and returns its content as a string
	"""
	print "...fetching  <%s>"%uri
	handle = urllib.urlopen(uri)
	result = handle.read()
	handle.close()
	return result

def transform_tei(tei_input):
	"""
	Get information from the TEI by applying an XSLT transformation.
	Parse the TEI/XML and keep just the information that is relevant in this context (= automatic  salignment of Perseus' URIs with DBPedia's).
	"""
	dumb_xml = ""
	xslt_root  = etree.parse("transform.xsl")
	transform = etree.XSLT(xslt_root)
	doc = etree.XML(tei_input)
	dumb_xml = transform(doc)
	return dumb_xml
	
def parse_lookup_reply(xml):
	results = []
	result = {"label":None,"uri":None,"desc":None,}
	doc = etree.XML(xml)
	res = list(doc.findall(".//{%s}Result"%"http://lookup.dbpedia.org/"))
	print "Found %i results via DBPedia lookup"%len(res)
	for r in res:
		result["label"] = r.find("{%s}Label"%"http://lookup.dbpedia.org/").text
		result["uri"] = r.find("{%s}URI"%"http://lookup.dbpedia.org/").text
		result["desc"] = r.find("{%s}Description"%"http://lookup.dbpedia.org/").text
		results.append(result)
		result = {"label":None,"uri":None,"desc":None,}
	return results

def parse_xml(etree_input):
	"""
	TBD
	"""
	res = {"names":[],"desc":None}
	names = etree_input.findall(".//name")
	desc = etree_input.findall(".//desc")
	el = names + desc
	for i,item in enumerate(list(el)):
		if(item.tag == "name"):
			res["names"].append(item.text)
		else:
			res["desc"] = item.text
	return res
	
try:
    f = open(input_file,"r")
    data = f.read().split("\n")
    random.shuffle(data)
    f.close()
    print "There are %i Smith IDs in the input list..."%len(data)
    
    for n in range(len(data)):
        if(n<10):
            print "\n##### %s #####"%data[n]
            test_url = format_perseus_uri(data[n])
            xml = get(test_url)
            #print parse_xml(xml)
            """
            file = open("%s.xml"%data[n],"w")
            file.write(xml)
            file.close()
            """
            temp = transform_tei(xml)
            names = set(parse_xml(temp)["names"])
            desc = parse_xml(temp)["desc"]
            for n in names:
                #for t in n.split():
                res= do_lookup(n)
                print parse_lookup_reply(res)
                print desc
        else:
            break
	
except IOError:
    print "this time didn't work"
