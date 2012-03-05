# Create your views here.
from dexter.doxer.models import *
from dexter.doxer.forms import *

from dexter.doxer.utils import *
import codecs

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

import settings
import os

from lxml import etree

import json
import csv

# for ng_id replace in makeClusters
import re

# to update_index SOLR from view
from haystack.management.commands import update_index, clear_index

# Search with haystack
from haystack.views import *
from haystack.forms import *
from haystack.query import *


###########################################################################
# SOLR simple process manager
###########################################################################
SOLR_JARNAME = "startdextersolr.jar"
#############################
def checkSolrProcess():
	tmp = os.popen("ps -Af").read()
	process_name = "startdextersolr.jar"
	if SOLR_JARNAME not in tmp[:]:
		newprocess = "cd %s && nohup java -Dsolr.clustering.enabled=true -jar %s &" % (settings.DEXTERPROJECTPATH+"/solr/",SOLR_JARNAME)
		os.system(newprocess)
		return 'solr was relaunched, refresh page to be sure'
	else:
		return 'running'
#############################
def killSolrProcess(request):
	killcmd = "kill `ps -ef | grep "+SOLR_JARNAME+" | grep -v grep | awk '{print $2}'`"
	os.system(killcmd)
	return HttpResponse("solr killed", mimetype="application/json")
############################################################












############################################################
def home(request):
	ctx={}
	#searchresults={}
	
	# list files in directory
	uploadPath = settings.DEXTERPROJECTPATH+'upload/'
	contents = os.listdir(uploadPath)
	
	for a in contents:
		locationpath = uploadPath+a
#		 if a.endswith('.csv'): ## Ngram list
# 			header,content = parseCsvFile(locationpath)
		if a.endswith('.xml') or a.endswith('.csv') or a.endswith('.txt') or a.endswith('.mmm'): ## Texte
			dtype='-'
			if a.endswith('.txmtxt.xml'):
				dtype='txmtxt'
			elif a.endswith('.txmxml.xml'):
				dtype='txmxml'
			elif a.endswith('.mlb.csv'):
				dtype='mlbcsv'
			elif a.endswith('.mlb.xml'):
				dtype='mlbxml'
			newTexte,isnew = Texte.objects.get_or_create(doctype=dtype,name=a,locationpath=locationpath)
				
	# data for table
	tabledata=[]
	did = request.GET.get('d','')
	see = request.GET.get('see','') # 'raw|index|table
	if did!='':
		texte = Texte.objects.get(id=did)	
		if see=='index':
			if texte.locationpath.endswith('.xml'):
				mintn = int(request.GET.get('mintn','1'))
				tabledata = getSolrNgramsArray(texte,mintn=mintn)
				tabledata = sorted(tabledata, key=lambda a: -int(a['tn']))
			elif texte.locationpath.endswith('.csv'):
				tabledata = getSolrClusters(texte)
				tabledata = sorted(tabledata, key=lambda a: -int(a['total']))
		elif see=='table':
			if texte.locationpath.endswith('.csv'):
				reader = csv.DictReader(open(texte.locationpath), delimiter='\t')
				for row in reader:
					tabledata.append(row)
		
	ctx.update({'textes':Texte.objects.all().order_by('name'),'tabledata':tabledata,'did':did,'see':see})
	ctx.update({'request':request})
	ctx.update({'solrstatus':checkSolrProcess()})
		
	########### RESPONSE
	if request.GET.get('q'):
		query = request.GET.get('q')
		#res = launchSolrQuery(query,0)

		jsondata = json.dumps(res,indent=4,ensure_ascii=False)
		return HttpResponse(jsondata, mimetype="application/json")

		#ctx.update({ 'results':res['response']['docs'] })
		#return render_to_response('searchresults.html',ctx ,context_instance=RequestContext(request))
	else:
		return render_to_response('home.html',ctx ,context_instance=RequestContext(request))
############################################################
# def list2dict(data):
# 	stop=len(data)
# 	keys=[data[i] for i in range(stop) if i%2==0] 
# 	values=[data[i] for i in range(stop) if i%2==1]
# 	return dict(zip(keys,values))





############################################################
def reset(request):
	Texte.objects.all().delete()
	Ngram.objects.all().delete()
	arg = {'interactive':False,'verbosity':0}
	clear_index.Command().handle(**arg)
	# os.system() disabled in django view when there is 
	#res = os.system('~/djangos/dexter/dexter/manage.py clear_index --noinput --verbosity=0')
	#subprocess.Popen('~/djangos/dexter/dexter/python manage.py clear_index --noinput --verbosity=0',shell=True).wait()
	#subprocess.call('~/djangos/dexter/dexter/python manage.py clear_index --noinput --verbosity=0',shell=True)
	#management.call_command('clear_index', verbosity=0)
	#backend = connections['default'].get_backend()
	#backend.clear()
	return redirect('/dexter')
############################################################
def edRefresh(request,did):
	texte = Texte.objects.get(id=did)
	
	# testing custom request handler /dataimport within solr
	if texte.locationpath.endswith('.mmm'):
		# XML = indexing TEXTE.CONTENTXML
		inFile = open(texte.locationpath,'r')
		texte.contentxml = inFile.read()
		inFile.close()
		texte.save()
		conn = pythonsolr.Solr( settings.HAYSTACK_SOLR_URL )
		# we use a patched version of pysolr.py, with a medialab function using /dataimport custom requesthandler !
		res = conn.addrawxml(texte.contentxml)
		oulog = open(texte.locationpath+'.log','w')
		oulog.write(res)
		oulog.close()
			
	if texte.locationpath.endswith('.xml'):
		# XML = indexing TEXTE.CONTENTXML
		inFile = open(texte.locationpath,'r')
		texte.contentxml = inFile.read()
		inFile.close()
		texte.save()
		# update lucene index
		update_index.Command().handle(verbosity=0)
	
	if texte.locationpath.endswith('.csv'):
		texte.ngram_set.all().delete()
		# CSV = indexing NGRAMS.CONTENT
		reader = csv.DictReader(open(texte.locationpath),delimiter='\t',quotechar='"')
		for row in reader:
			w_content = row['ngram'].replace("_"," ")
			#w_content = row['lem']
			w_xmlid = row['id']
			try:
				dn=row['dn']
				tn=row['tn']
			except:
				dn=tn=0
			#if row['highlight']=='True':
			newNgram,isnew = Ngram.objects.get_or_create(dn=dn,tn=tn,texte=texte,content=w_content,xmlid=w_xmlid)
		# update lucene index
		update_index.Command().handle(verbosity=0)
			
	return redirect('/dexter')
############################################################
def edDelete(request,did):
	texte = Texte.objects.get(id=did)
	filename = texte.locationpath.split("/")[-1]
	if '*' not in texte.locationpath and (not filename.startswith("_") or "[" in filename):
		os.remove(texte.locationpath)
		texte.delete()
	return redirect('/dexter')
############################################################
def edRawLook(request,did):
	texte = Texte.objects.get(id=did)
	inFile = open(texte.locationpath,'r')
	alltxt = inFile.read()
	inFile.close()
	#return HttpResponse(texte.contentxml)
	return HttpResponse(alltxt)
############################################################
def edRawGet(request,did):
	texte = Texte.objects.get(id=did)
	inFile = open(texte.locationpath,'r')
	alltxt = inFile.read()
	inFile.close()
	answ = HttpResponse(alltxt)
	answ['Content-Disposition'] = 'attachment; filename='+texte.locationpath.split('/')[-1]
	return answ
############################################################







############################################################
def uploadFile(request):
	d={}
	success=""
	if request.method == "POST":
		foldname = settings.DEXTERPROJECTPATH+'upload/'
		if request.is_ajax( ):
			upload = request
			is_raw = True
			try:
				filename = request.GET['qqfile']
			except KeyError:
				return HttpResponseBadRequest( "AJAX request not valid" )
		else:
			is_raw = False
			if len( request.FILES ) == 1:
				upload = request.FILES.values( )[ 0 ]
			else:
				raise Http404( "Bad Upload" )
			filename = upload.name
	
		success = save_upload( upload, foldname, filename, is_raw )
		d['success'] = success
		d['loc'] = foldname+"/"+filename
	jsondata = json.dumps(d,indent=4,ensure_ascii=False)
	return HttpResponse(jsondata, mimetype="application/json")
################################################################################
def save_upload( uploaded, foldname, filename, raw_data ):
	''' 
	raw_data: if True, uploaded is an HttpRequest object with the file being
			the raw post data 
			if False, uploaded has been submitted via the basic form
			submission and is a regular Django UploadedFile in request.FILES
	'''
	try:
		from io import FileIO, BufferedWriter
		# check if dir exist, create it if needed
		wantedDir = foldname
		if not os.path.exists(wantedDir):
			os.mkdir(wantedDir)
		with BufferedWriter( FileIO( wantedDir+"/"+filename, "wb" ) ) as dest:
			# if the "advanced" upload, read directly from the HTTP request 
			# with the Django 1.3 functionality
			if raw_data:
				foo = uploaded.read( 1024 )
				while foo:
					dest.write( foo )
					foo = uploaded.read( 1024 ) 
			# if not raw, it was a form upload so read in the normal Django chunks fashion
			else:
				for c in uploaded.chunks( ):
					dest.write( c )
		# got through saving the upload, report success
		return True
	except IOError:
		# could not open the file most likely
		pass
	return False
############################################################








############################################################
def edMakeXslt(request,did,typ):
	texte = Texte.objects.get(id=did)
	xml_file = texte.locationpath
	
	xslt_nms = settings.MEDIA_ROOT + 'xml/remove_nms.xsl'
	
	xslt_file = settings.MEDIA_ROOT + 'xml/'+typ+'.xsl'
	
	#xslt_file = settings.MEDIA_ROOT + 'xml/txm_tei2html.xsl'
	#xslt_file = settings.MEDIA_ROOT + 'xml/txm_trans2html.xsl'
	#xslt_file = settings.MEDIA_ROOT + 'xml/tei2html.xsl'
	
	# first remove nms
	xml_root = etree.XML(open(xml_file,'r').read())
	xslt_root = etree.XML(open(xslt_nms,'r').read())
	transform = etree.XSLT(xslt_root)
	result = etree.tostring(transform(xml_root),pretty_print=True,encoding='UTF-8')
	
	# transform to mlb
	xml_root = etree.XML(result)
	xslt_root = etree.XML(open(xslt_file,'r').read())
	transform = etree.XSLT(xslt_root)
	result = etree.tostring(transform(xml_root),pretty_print=True,encoding='UTF-8',xml_declaration=True)
	
	newname = texte.name[:-4]+"["+str(texte.id)+"].mlb.xml"
	newfilepath = settings.DEXTERPROJECTPATH+'upload/'+newname
	fileout=open(newfilepath,'w')
	fileout.write(result)
	fileout.close()
	return redirect('/dexter')
############################################################
def edMakeEnrichXmlWithNgrams(request,did):
	texte = Texte.objects.get(id=did)
	
	mintn=int(request.GET.get('mintn','1'))
	
	basePath = texte.locationpath[:-8]+'ngr'+str(mintn)+'.mlb'
	outXmlPath = basePath+'.xml'
	outCsvPath = basePath+'.csv'
	
	# 1) fetch solr ngrams from that text
	keepNgrams = getSolrNgramsArray(texte,mintn=mintn)
	
	# 2) _ngramed.xml : update xml tree using homemade-XpathOffsetUpdater
	xmlupdater = XpathOffsetUpdater( [modif(ng['offsets'],ng['ngram']) for ng in keepNgrams] )
	newtree,buff,ngrammodifiedwithpos = xmlupdater.run(texte.locationpath)
	allxmlstr = etree.tostring(newtree,pretty_print=True,encoding='UTF-8',xml_declaration=True)
	fileout=open(outXmlPath,'w')
	# if you need to write the concatenated string made during parsing...
	#fileout=codecs.open(outpath,'w','utf-8')
	fileout.write(allxmlstr)
	fileout.close()
	newEnrichedTexteXml,isnew = Texte.objects.get_or_create(doctype='mlbxml',name=outXmlPath.split("/")[-1],locationpath=outXmlPath)
	
	# 3) _ngramed.csv : writes all ngrams in a csv file
	header = keepNgrams[0].keys()+['id','pos','lem','highlight']
	csvout = open(outCsvPath, 'wb')
	w = csv.DictWriter(csvout,fieldnames=header,delimiter='\t',quotechar='"')
	d = dict((k,k) for k in header)
	w.writerow(d)
	for i,ng in enumerate(keepNgrams):
		#w.writerow({'id':'ng_'+str(i),'ngram':ng['ngram'].encode('utf-8')})
		d = dict((k, v.encode('utf-8') if isinstance(v, unicode) else v) for k,v in ng.iteritems())
		# add interesting fields: id & pos
		md = ngrammodifiedwithpos[i]
		d['id']='ng_'+str(i)
		d['pos']=md.pos
		d['lem']=md.lem.encode('utf-8') if isinstance(md.lem, unicode) else md.lem
		d['highlight']=md.keep
		w.writerow(d)
	csvout.close()
	newEnrichedTexteCsv,isnew = Texte.objects.get_or_create(doctype='mlbcsv',name=outCsvPath.split("/")[-1],locationpath=outCsvPath)
	newEnrichedTexteCsv.relatedtextes.add(newEnrichedTexteXml)
	newEnrichedTexteCsv.save()
	
	return redirect('/dexter')
############################################################
def edMakeGroupNgrams(request,did):
	# source file is the ngram list
	# (optionnaly) there is a related file which is the enriched xml with ngrams ids in full text
	texte = Texte.objects.get(id=did)
	
	inCsvPath = texte.locationpath
	outCsvPath = texte.locationpath[:-8]+'grp.mlb.csv'
	
	try: # if was produced by dexter
		inXmlPath = texte.relatedtextes.all()[0].locationpath
		outXmlPath = texte.relatedtextes.all()[0].locationpath[:-8]+'grp.mlb.xml'
		producexml=True
	except:
		outCsvPath = texte.locationpath[:-8]+'['+str(texte.id)+']grp.mlb.csv'
		producexml=False
	
	# 1) fetch ngrams clusters from solr
	clusters = getSolrClusters(texte)
	
	# 2) (optionnaly) raw replace ng_ids with correspondant ngc_ids
	if producexml:
		filein=open(inXmlPath,'r')
		xmlContent = filein.read()
		filein.close()
		for i,clust in enumerate(clusters):
			id_new = 'ngc_'+str(i)
			for id_old in clust['ngrams']:
				xmlContent = re.sub(id_old,id_new,xmlContent)
		fileout = open(outXmlPath,'w')
		fileout.write(xmlContent)
		fileout.close()
		newEnrichedTexteXml,isnew = Texte.objects.get_or_create(doctype='mlbxml',name=outXmlPath.split("/")[-1],locationpath=outXmlPath)
	
	# 3) writes csv with groups and their content
	header = clusters[0].keys()+['id']
	fileout = open(outCsvPath, 'wb')
	w = csv.DictWriter(fileout,fieldnames=header,delimiter='\t',quotechar='"')
	d = dict((k,k) for k in header)
	w.writerow(d)
	for i,clust in enumerate(clusters):
		d = dict((k, v.encode('utf-8') if isinstance(v, unicode) else v) for k,v in clust.iteritems())
		d['ngrams']=", ".join(d['ngrams'])
		d['id']='ngc_'+str(i)
		w.writerow(d)
	fileout.close()
	newEnrichedTexteCsv,isnew = Texte.objects.get_or_create(doctype='mlbcsv',name=outCsvPath.split("/")[-1],locationpath=outCsvPath)
	if producexml:
		newEnrichedTexteCsv.relatedtextes.add(newEnrichedTexteXml)
		newEnrichedTexteCsv.save()
		
	return redirect('/dexter')
############################################################














