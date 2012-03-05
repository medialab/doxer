# -*- coding: utf-8 -*-
################################################
from haystack.indexes import *
from haystack import site
from doxer.models import *
################################################

# For the most basic usage, you can simply register a model with the `site`.
# It will get a `haystack.indexes.BasicSearchIndex` assigned to it, whose
# only requirement will be that you create a
# `search/indexes/bare_bones_app/cat_text.txt` data template for indexing.
################################################


# This is where fields for solr/lucene indexing are set
# note that you may need to modify schema.xml file anyway... cause haystack isn't so much "tunable"

################################################
class TexteIndex(SearchIndex):
	text = CharField(document=True, use_template=True)
	texteid = IntegerField(model_attr='id')
	# ngrams in the text
	textengram = EdgeNgramField(model_attr='contentxml')
	
	fulltext = CharField(model_attr='contentxml')
	
################################################
class NgramIndex(SearchIndex):
	text = CharField(document=True, use_template=True)
	texteid = IntegerField(model_attr='texte__id')
	ngramxmlid = CharField(model_attr='xmlid')
	fullngram = CharField(model_attr='content')
	
	#w_pos = CharField(model_attr='pos', faceted=True)
	#w_id = CharField(model_attr='wid', faceted=True)
################################################

site.register(Texte,TexteIndex)
site.register(Ngram,NgramIndex)



