import urllib
import logging
import argparse
import random
from xml.etree.ElementTree import ElementTree,fromstring
from lxml import etree
from nltk.corpus import stopwords # NLTK is needed for the English stopword list
try:
	from gensim import corpora, models, similarities # gensim provides an handy implementation of, among other things, LSI and topic models
except ImportError:
	print 'gensim library not found: try sudo easy_install gensim\n'
	gensim = None
	raise ImportError
	
"""
author: Matteo Romanello, <matteo.romanello@kcl.ac.uk>
"""

global input_file,logger
input_file = "zbios.txt"
logger = None

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
	logger.info("fetching resource <%s>"%uri)
	handle = urllib.urlopen(uri)
	result = ''
	while (1):
		next = handle.read()
		if not next: 
			break
		result += next
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
	"""
	TBD
	"""
	results = []
	result = {"label":None,"uri":None,"desc":None,}
	doc = etree.XML(xml)
	res = list(doc.findall(".//{%s}Result"%"http://lookup.dbpedia.org/"))
	logger.info("Found %i results via DBPedia lookup"%len(res))
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

def suggest_matching(docs,query):
	"""
	The idea is to suggest the document among docs which is most matching the query (query).
	The suggestion is based on gensim's implementation of Latent Semantic Indexing, with tfidf as similarity measure.
	"""
	# stopword list comes from NLTK
	# we might want to consider removing pucntuation
	stoplist = stopwords.words('english')
	texts = [[word for word in document[1].lower().split() if word not in stoplist] for document in docs]
	"""
	# this removes the words with lowest frequency: check if enabling it improves the results
	all_tokens = sum(texts, [])
	tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
	texts = [[word for word in text if word not in tokens_once] for text in texts]
	"""
	dictionary = corpora.Dictionary(texts)
	dictionary.save('test.dict')
	#print dictionary
	#print dictionary.token2id
	corpus = [dictionary.doc2bow(text) for text in texts]
	logger.debug(corpus)	
	tfidf = models.TfidfModel(corpus)
	index = similarities.SparseMatrixSimilarity(tfidf[corpus])
	vec_bow = dictionary.doc2bow(query.lower().split())
	vec_tfidf = tfidf[vec_bow] # convert the query to TFIDF space
	sims = index[vec_tfidf] # perform a similarity query against the corpus
	sims = sorted(enumerate(sims), key=lambda item: -item[1])
	#print list(enumerate(sims))
	res = [(docs[sims[i][0]],str(sims[i][1]),docs[i][0]) for i in range(len(sims))]
	return res

def init_logger(verbose=False, log_file=None):
	"""
	Initialise a logger.
	"""
	import logging
	l_logger = logging.getLogger("script")
	if(verbose):
		l_logger.setLevel(logging.DEBUG)
	else:
		l_logger.setLevel(logging.INFO)
	if(log_file is None):
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s"))
		l_logger.addHandler(ch)
		l_logger.info("Logger initialised.")
	else:
		pass # I should actually complete this  function as initialise a logger which writes to a file
	return l_logger

def run(limit=5):
	"""
	Go through an input list of Smith IDs for entities, and for each of them
	try to find a matching entry in DBpedia.
	"""
	try:
		f = open(input_file,"r")
		data = f.read().split("\n")
		random.shuffle(data)
		f.close()
		logger.info("There are %i Smith IDs in the input list"%len(data))
		for n in range(len(data)):
			if(n < limit):
				match_entity(data[n])
			else:
				break
	except IOError:
	    print "this time didn't work"

def match_entity(id):
	logger.debug("%s"%id)
	test_url = format_perseus_uri(id)
	xml = get(test_url)
	temp = transform_tei(xml)
	names = set(parse_xml(temp)["names"])
	desc = parse_xml(temp)["desc"] # this is the Smith's entry
	for n in names:
		#for t in n.split():
		max_res = 10
		
		lookup_results = parse_lookup_reply(do_lookup(n,max_res))
		while(len(lookup_results) == max_res):
			lookup_results = parse_lookup_reply(do_lookup(n,max_res*max_res))
			if(len(lookup_results)==max_res):
				break
	
		documents = [(r["uri"],r["desc"]) for r in lookup_results if r["desc"] is not None]
		logger.debug(documents)
		if(len(documents)>1):
			"""
			there is > 1 result from dbpedia.
			will try to disambiguate using TFIDF-based LSI
			"""
			results = suggest_matching(documents,query=desc)
			for n,r in enumerate(results):
				logger.debug("##%i## (%s) %s"%(n,r[1],r[0]))
			
			print "\n%s\n"%desc
			print "Highest ranked (TFIDF): \"%s\" with TFIDF value %s\n"%(results[0][0][1],results[0][1])
			print "%s sameAs %s?\n"%(test_url,results[0][2])
			return True
		elif(len(documents)==1):
			""
			""
			print "\n%s\n"%desc
			print "\n%s\n"%documents[0][1]
			print "%s sameAs %s?\n"%(test_url,documents[0][0])
			return True
		else:
			print "No results from the DBpedia query"
			return False
	return

def get_input(input_file = "zbios.txt"):
	"""
	Go through an input list of Smith IDs for entities, and for each of them
	try to find a matching entry in DBpedia.
	"""
	try:
		f = open(input_file,"r")
		data = f.read().split("\n")
		random.shuffle(data)
		f.close()
		logger.info("There are %i Smith IDs in the input list"%len(data))
		return data
	except IOError:
	    print "There was a problem reading the input file"
	return

def main():
	parser = argparse.ArgumentParser(prog="script.py",description='Match Perseus\' Smith URIs against DBpedia URIs.') # initialise the argument parser
	parser.add_argument('--id', action="store", dest="id", type=str,default=None)
	parser.add_argument('--verbose','-v',action='store_true', default=False,help='Logs DEBUG information (default is INFO level)')
	args = parser.parse_args()
	global logger
	logger = init_logger(verbose=args.verbose,log_file=None) # initialise the logger
	try:
		assert args.id is not None
		logger.debug("id==%s"%args.id)
		try:
			match_entity(args.id)
		except Exception as inst:
			print inst
		#run(limit=1)
	except:
		logger.error("Needed valid ID: pass one using the %s parameter"%"--id")
		data = get_input()
		want_continue = True
		while(want_continue):
			try:
				res = match_entity(data.pop())
				if(res is True):
					answer = raw_input("Do you want to continue? [Yy/Nn]: ")
					if(answer == "Y" or answer == "y"):
						want_continue = True
					else:
						want_continue = False
				else:
					print "Keep going!"
			except:
				print "There was a problem. Trying with the next one."
	
	# initialise the logger
	
	#run(limit=1)
	# load the data
	#load_data(opts.aph_volume,opts.input_filename,opts.json_filename)

if __name__ == '__main__':
	main()