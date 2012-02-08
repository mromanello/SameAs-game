import urllib
import random
from xml.etree.ElementTree import ElementTree,fromstring
from lxml import etree
from nltk.corpus import stopwords
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
input_file = "zbios.txt"

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

def suggest_matching(docs,query):
	"""
	The idea is to suggest the document among docs which is most matching the query (query).
	The suggestion is based on gensim's implementation of Latent Semantic Indexing, with tfidf as similarity measure.
	"""
	# stopword list comes from NLTK
	# we might want to consider removing pucntuation
	stoplist = stopwords.words('english')
	texts = [[word for word in document.lower().split() if word not in stoplist] for document in docs]
	#all_tokens = sum(texts, [])
	#tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
	#texts = [[word for word in text if word not in tokens_once] for text in texts]
	dictionary = corpora.Dictionary(texts)
	dictionary.save('test.dict')
	#print dictionary
	#print dictionary.token2id
	corpus = [dictionary.doc2bow(text) for text in texts]
	#print corpus
	
	"""
	lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)
	index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
	vec_bow = dictionary.doc2bow(query.lower().split())
	vec_lsi = lsi[vec_bow] # convert the query to LSI space
	sims = index[vec_lsi] # perform a similarity query against the corpus
	sims = sorted(enumerate(sims), key=lambda item: -item[1])
	#print list(enumerate(sims))
	print "Highest ranked (LSI): \"%s\" with LSI value %s"%(docs[sims[0][0]],str(sims[0][1]))
	"""
	
	tfidf = models.TfidfModel(corpus)
	index = similarities.SparseMatrixSimilarity(tfidf[corpus])
	vec_bow = dictionary.doc2bow(query.lower().split())
	vec_tfidf = tfidf[vec_bow] # convert the query to TFIDF space
	sims = index[vec_tfidf] # perform a similarity query against the corpus
	sims = sorted(enumerate(sims), key=lambda item: -item[1])
	#print list(enumerate(sims))
	print "Highest ranked (TFIDF): \"%s\" with TFIDF value %s"%(docs[sims[0][0]],str(sims[0][1]))
	return docs[sims[0][0]]
try:
	f = open(input_file,"r")
	data = f.read().split("\n")
	random.shuffle(data)
	f.close()
	print "There are %i Smith IDs in the input list..."%len(data)

	for n in range(len(data)):
		if(n<5):
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
				max_res = 10
				lookup_results = parse_lookup_reply(do_lookup(n,max_res))
				while(len(lookup_results) == max_res):
					#do stuff
					# need to add a breaking condition
					lookup_results = parse_lookup_reply(do_lookup(n,max_res*max_res))
					
				documents = [r["desc"] for r in lookup_results if r["desc"] is not None]
				print desc
				#print documents
				"""
				handle the fact that, when the number of lookup results is equal to the number
				of max query results, we should increase the latter and get more lookup results
				"""
				if(len(documents)>=1):
					suggest_matching(documents,query=desc)
				#	print "\n## Smith entry: %s"%desc
				#	print "\n## Suggested matching: %s"%suggest_matching(documents,query=desc)
		else:
			break
			
except IOError:
    print "this time didn't work"
