from django.db import models

from lxml import etree
import settings

import re

# for raw search to do tag cloud using haystack/solr
from haystack.query import SearchQuerySet,SQ
# to get termVectors tf/df/tfidf using raw_queries with pythonsolr
import dexter.pythonsolrpatched as pythonsolr




########################################################################
class Texte(models.Model):
	# file
	locationpath = models.CharField(max_length=150)
	#filesize = models.BigIntegerField(default=0)
	name = models.CharField(max_length=100)
	doctype = models.CharField(max_length=10)
	# for verbatims, we store content in DB
	contenttxt = models.TextField()
	contenthtml = models.TextField()
	contentxml = models.TextField()
	# output
	relatedtextes = models.ManyToManyField('self')
	def __unicode__(self):
		return str(self.id)+":"+self.name
####################################################################
class Ngram(models.Model):
	texte = models.ForeignKey(Texte)
	content = models.CharField(max_length=100)
	xmlid = models.CharField(max_length=20)
	dn = models.BigIntegerField(default=0)
	tn = models.BigIntegerField(default=0)
	#pos = models.CharField(max_length=20,default="_nope_")
	######
	#df = models.FloatField(default=0)			# % of speakers using this word
	#dn = ngramspeaker_set.count()				# n of speakers using this word (easy using django queries)
	# NB: no need to store max values here ! do it using django queries !
	# maxtfidf = models.FloatField(default=0)
	# maxspeakerid = models.BigIntegerField(default=0)
	def __unicode__(self):
		return "Ngram:"+str(self.xmlid)+":"+self.content
########################################################################







	################################ ON TEXT
	# SIMPLE SEARCH
	#?q=et

	# TERMVECTOR (tfidf,df) gives the list of ngrams !
	#?q=texteid:1&fq=django_ct:(doxer.text)&qt=tvrh&fl=score&tv.fl=textengram&tv.all=true
	#p = {'fq':'django_ct:(doxer.text)','qt':'tvrh','fl':'text','tv.fl':'textengram','tv.all':'true'}
	
	
	################################ ON NGRAMS
	# MORE LIKE THIS SIMILARITY
	#?q=texteid:1&fq=django_ct:(doxer.ngram)&mlt=true&mlt.fl=text&mlt.mindf=1&mlt.mintf=1&fl=score&mlt.count=10
	#p = {'fq':'django_ct:(doxer.ngram)','mlt':'true','mlt.fl':'text','mlt.mindf':1,'mlt.mintf':1,'fl':'score','mlt.count':maxcount}
	#p = {'mlt':'true','mlt.fl':'textengram','mlt.mindf':1,'mlt.mintf':1,'fl':'score','mlt.count':maxcount}
	
	#p = {'fl':'score','rows':100}
	#q = "textengram:"+query #+' texteid:'+str(texte.id)


############################################################
def getSolrNgramsArray(texte,mintn=0):
	q = "texteid:"+str(texte.id)
	p = {'fq':'django_ct:(doxer.texte)','qt':'tvrh','fl':'text','tv.positions':'true','tv.fl':'textengram','tv.all':'true'}
	
	#select?q=texteid:1&fq=django_ct:(doxer.texte)&qt=tvrh&fl=text&tv.positions=true&tv.fl&tv.all=true
	res = launchSolrQuery(q,p)
	
	tv = res['termVectors'][1]
	tv = list2dict(tv)

	# NB: For SOLR : TF=nTermOccurences, DF=nDocumentOcurrences, TFIDF=TF/DF
	# We need frequency, not nOccurrences !!
	# so:
	#totalDocuments=0
	#totalTerms=0
	#totalTerms = len(tv["textengram"])
	
	res = list2dict(tv["textengram"])
	# first transform all data in dict
	alldic={}
	for k,v in res.iteritems():
		d = list2dict(v)
		alldic.update({k:d})
	
	# then keep words wanted
	out=[]
	for w,d in alldic.items():
		keepw = True
		keepw = len(w)>2
		keepw = keepw and (d['tf']>=mintn)
		###### RULE 1 : dont keep words which appear only 1 time for that speaker and never else (df=tf=1)
		#keepw = d['df']+d['tf']!=2
		###### RULE 2 : dont keep words included in other-longer-word (if same df/tf)
		# deprecated: now we keep all ngrams, cause tests are made later based on POS
		#keepw = keepw and not True in [(w in otherw and w!=otherw and d['df']==alldic[otherw]['df'] and d['tf']==alldic[otherw]['tf']) for otherw in alldic.keys()]
		
		if keepw:
			# nb: there is one offset for each position of ngram in text
			offsets = list2list(d['offsets'])
			df = d['df']
			tf = d['tf']
			#tfidf = tf/float(df)
			dic = {'ngram':w,'dn':d['df'],'tn':d['tf'],'offsets':offsets}
			out.append(dic)
	return out
############################################################





############################################################
def getSolrClusters(texte):
	q = "texteid:"+str(texte.id)
	p = {'usingreqhandler':'clustering','fq':'django_ct:(doxer.ngram)','fl':'ngramxmlid,id','rows':texte.ngram_set.count()}
	
	#clustering?q=texteid:1&fq=django_ct:(doxer.ngram)&fl=ngramxmlid,id&rows=10
	res = launchSolrQuery(q,p)
	
	# nb: we asked for id(=solr id) and ngramid(=django model id), to be able to know which ngrams were clustered
	ngram_ids={}
	for d in res['response']['docs']:
		ngram_ids[d['id']] = d['ngramxmlid']
	
	tv = res['clusters']
	out=[]
	for clus in tv:
		label = clus['labels'][0]
		docs = clus['docs']
		if label=='Other Topics':
			for d in docs:
				docsArr = [ ngram_ids[d] ]
				docsStr = Ngram.objects.get(texte=texte,xmlid=ngram_ids[d]).content
				sumtn = int(Ngram.objects.get(texte=texte,xmlid=ngram_ids[d]).tn)
				out.append({'label':label,'ngrams':docsArr,'content':docsStr,'score':clus['score'],'total':1,'sumtn':sumtn,'highlight':True})
		else:
			docsArr = [ ngram_ids[d] for d in docs ]
			docsStr = " | ".join([ Ngram.objects.get(texte=texte,xmlid=ngram_ids[d]).content for d in docs ])
			sumtn = sum([int(Ngram.objects.get(texte=texte,xmlid=ngram_ids[d]).tn) for d in docs ])
			out.append({'label':label,'ngrams':docsArr,'content':docsStr,'score':clus['score'],'total':len(docsArr),'sumtn':sumtn,'highlight':False})
		
	return out
############################################################













############################################################
def launchSolrQuery(q,p):
	conn = pythonsolr.Solr( settings.HAYSTACK_SOLR_URL )
	r = conn.search(q,**p)
	return r.result
############################################################		
def list2dict(data):
	stop=len(data)
	keys=[data[i] for i in range(stop) if i%2==0] 
	values=[data[i] for i in range(stop) if i%2==1]
	return dict(zip(keys,values))
def list2list(data):
	stop=len(data)
	s=[data[i] for i in range(stop) if i%4==1] 
	e=[data[i] for i in range(stop) if i%4==3] 
	return [(s[i],e[i]) for i in range(len(s))]
############################################################








############################################################
# DEPRECATED
def parseXml(texte):
	texte.ngram_set.all().delete()
	
	########################################## XML Copy
	inFile = open(texte.locationpath,'r')
	texte.contentxml = inFile.read()
	inFile.close()
	texte.save()
# 	allcontentxml = re.sub('&','&amp;',allcontentxml)
# 	allcontentxml = re.sub('<','&lt;',allcontentxml)
# 	allcontentxml = re.sub('>','&gt;',allcontentxml)
# 	allcontentxml = re.sub('\'','&apos;',allcontentxml)
# 	allcontentxml = re.sub('"','&quot;',allcontentxml)
# &lt;	<	less than
# &gt;	>	greater than
# &amp;	&	ampersand 
# &apos;	'	apostrophe
# &quot;	"	quotation mark

	
	########################################## XML Parsing
# 	tree = etree.parse(texte.locationpath)
# 	root = tree.getroot()
# 	
# 	XMLTEI = settings.XMLTEI
# 	XMLTXM = settings.XMLTXM
# 	
# 	allcontenttxt=""
# 	######################### XML TXM
# 	if root.tag==XMLTEI+'TEI':
# 		words = root.findall(XMLTEI+'textunit/'+XMLTEI+'w')
# 		for wnode in words:
# 			w_id = wnode.attrib['id']
# 			w_content = wnode.find(XMLTXM+'form').text
# 			w_lem = wnode.find(XMLTEI+'interp[@type="#ttlemma"]').text
# 			w_pos = wnode.find(XMLTEI+'interp[@type="#ttpos"]').text
# 			newNgram,isnew = Ngram.objects.get_or_create(texte=texte,content=w_content,wid=w_id,pos=w_pos)
# 			
# 			allcontenttxt += w_content + " "
# 				
# 		texte.contenttxt = allcontenttxt
# 		texte.save()
############################################################
# def parseCsvFile(inPath):
# 	header=[]
# 	content=[]
# 	inFile = open(inPath,'r')
# 	nm=0
# 	for l in inFile.readlines():
# 		arr=l.split('\t')
# 		if nm==0:
# 			nm+=1
# 			for v in arr:
# 				header.append(removeQuotesStartEnd(v))
# 		else:
# 			valtab=arr
# 			values=dict()
# 			for k in range(len(header)):
# 				values[header[k]] = removeQuotesStartEnd(valtab[k])
# 			if values[header[k]]=="":
# 				values[header[k]]="[NC]"
# 			content.append(values)
# 	inFile.close()
# 	return {'header':header,'content':content}
############################################################