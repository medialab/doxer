#!/usr/bin/python
# -*- coding: utf-8 -*-
########################################
from lxml import etree
import re

SHORTPOS={}
SHORTPOS['ABR'] = "X"		#"abréviations"
SHORTPOS['INT'] = "X"		#"interjections"
SHORTPOS['PUN'] = "X"		#"marques de ponctuation"
SHORTPOS['PUN:cit'] = "X"	#"marques de ponctuation marquant des citations"
SHORTPOS['SENT'] = "X"		#"phrases"
SHORTPOS['SYM'] = "J"		#"symboles"			novembre/janvier
SHORTPOS['ADJ'] = "A"		#"adjectifs"		même
SHORTPOS['ADV'] = "R"		#"adverbes"			grosso/modo/tout/rien/ne/n'/là/pas/mal/très
SHORTPOS['KON'] = "E"		#"conjonctions"		et/ou/mais/quand
SHORTPOS['NOM'] = "N"		#"noms"
SHORTPOS['NUM'] = "N"		#"numéraux"
SHORTPOS['NAM'] = "N"		#"noms propres"
SHORTPOS['PRP'] = "S"		#"prépositions"		de/du/à/pour/sur
SHORTPOS['PRP:det'] = "O"		#"déterminants contractés 	au/du/aux/des
SHORTPOS['DET:ART'] = "T"		#"articles"					le/la
SHORTPOS['DET:POS'] = "F"		#							mon
SHORTPOS['PRO'] = "M"			#"pronoms"					il/elle/nous/vous
SHORTPOS['PRO:POS'] = "F"		#"pronoms possessifs"		mon/ton/son/sa
SHORTPOS['PRO:DEM'] = "F"		#"pronoms démonstratifs"	ce/ces
SHORTPOS['PRO:IND'] = "P"		#"pronoms indéfinis"		les/des
SHORTPOS['PRO:PER'] = "L"		#"pronoms personnels"		ils/il/vous/on/eux/(il)en(a)
SHORTPOS['PRO:REL'] = "Q"		#"pronoms relatifs"			qui/que
SHORTPOS['VER:cond'] = "V"		#"verbes au conditionnel"
SHORTPOS['VER:futu'] = "V"		#"verbes au futur"
SHORTPOS['VER:impe'] = "W"		#"verbes à l'impératif"
SHORTPOS['VER:infi'] = "W"		#"verbes à l'infinitif"
SHORTPOS['VER:impf'] = "V"		#"verbes à l'imparfait"
SHORTPOS['VER:pper'] = "V"		#"participes passés"
SHORTPOS['VER:ppre'] = "V"		#"participes présents"
SHORTPOS['VER:pres'] = "V"		#"verbes au présent"
SHORTPOS['VER:simp'] = "V"		#"verbes au passé simple"
SHORTPOS['VER:subi'] = "V"		#"verbes au subjonctif imparfait"
SHORTPOS['VER:subp'] = "V"		#"verbes au subjonctif présent"

# ajouter 1-grams (N/Vinfinitif)
# ajouter MESURES !
# 	tn,tf
# 	max-tf for each d
# 	dn
# 	tfidf
# 	A = tx d'inclusion + tx recouvrement
# 	B = nb de conteneurs différents
# regexp dans interface

# COMPRENDRE NEGATION
# ils ne veulent pas = L R V R
# ne veut = R V

# ADVERBES ?
# ce plan-là = F N X R

# ?
# d'entreprises = S N
# de giscard

# GARDER LES 'SL'
# j'ai voté pour eux = V V S L

coolpos = re.compile("^[^E^X^V^Q^S^T^O^R].*[^E^X^O^B^T^F^P^L^R^S^Q]$")
########################################
def isCoolPos(posStr):
	test = posStr.replace(" ","")
	if re.match(coolpos,test):
		return True
	else:
		return False
########################################



########################################
class modif:
	def __init__(self,offs,st):
		#self.start=i
		#self.end=o
		self.offsets = offs
		self.ngram = st
		self.pos = ""
		self.lem = ""
		self.keep = False
########################################
class XpathOffsetUpdater():
#	tree = etree.parse('./entretienpetite.xml')
#	root = tree.getroot()
	def __init__(self,modifs):
		self.currentpos=0
		self.modifs = modifs
		self.updates=[]
	def getTag(self,elem):
		if '}' not in elem.tag:
			return elem.tag
		else:
			return elem.tag.split('}')[1]
	def getStartTag(self,elem,isroot):
		attstr=''
		if isroot:
			atts={}
			for k,v in elem.nsmap.items():
				if k==None:
					key='xmlns'
				else:
					key='xmlns:'+k
				atts[key]=v	
		else:
			atts = elem.attrib
		for k,v in atts.items():
			attstr+=' '+k+'="'+v+'"'
		return '<'+self.getTag(elem)+attstr+'>'
	def updateElementAttributes(self,elem,theclass):
		if elem.get('class'):
			elem.set('class',elem.get('class')+" "+theclass)
		else:
			elem.set('class',theclass)
		if 'ng ' not in elem.get('class'):
			elem.set('class','ng '+elem.get('class'))
	def getElemPos(self,elem):
		# return simplified version of POS (VERB:pres become VERB)
		# see above to see list of possible POS
		pos = elem.get('class').split(' ')[0].split('_')[1]
		return SHORTPOS.get(pos,pos)
	def getElemLem(self,elem):
		lem = elem.get('class').split(' ')[1].split('_')[1]
		return lem
	def addNgramsToUpdate(self,pos,elem):
		for i,mod in enumerate(self.modifs):
			for k,off in enumerate(mod.offsets):
				if off[0]<pos and off[1]>=pos:
					self.updates.append([elem,i,mod])
					# store the successive POS in the modif object (only for first occurence of ngram)
					if k==0:
						mod.pos += " "+self.getElemPos(elem)
						mod.lem += " "+self.getElemLem(elem)
		return 1
	def run(self,source):
		allt="<?xml version='1.0' encoding='UTF-8'?>\n"
		buff=len(allt)
		for event,elem in etree.iterparse(source,events=('start','end')):
			thetree = elem.getroottree()
			if event == 'start':
				#allt += self.getStartTag(elem,elem==thetree.getroot())
				buff += len(self.getStartTag(elem,elem==thetree.getroot()))
				if elem.text is not None:
					#allt += elem.text
					buff += len(elem.text)
				self.addNgramsToUpdate(buff,elem)
			elif event == 'end':
				if elem.text is None and elem.getchildren()==[]: # self closing tag
					#allt = allt[:-1]+"/>"
					buff += 1
				else:
					#allt += '</'+self.getTag(elem)+'>'
					buff += len('</'+self.getTag(elem)+'>')
				if elem.tail is not None:
					#allt += elem.tail
					buff += len(elem.tail)
		# now update the elements (for each modif object)
		for up in self.updates:
			if isCoolPos(up[2].pos):
				self.updateElementAttributes(up[0],'ng_'+str(up[1]))
				up[2].keep = True
		return thetree,buff,self.modifs#,allt
########################################













"""
########################################
def insertTail(elem,ngram,theclass,pos_a,pos_b,start,end):
	rtree = elem.getroottree()
	#print 'INSERTING on ELEMENT tail:'+ rtree.getpath(elem)
	parentInd = elem.getparent().index(elem)
	#print 'NOTE THAT INDEX:',parentInd
	newelem = etree.Element("span")
	newelem.set("class",theclass)
	newelem.text = ngram
	
	initialtext = elem.tail
	#print 'CONTENT',initialtext,pos_a,pos_b,start,end
	if pos_a==start:
		elem.tail=""
	else:
		elem.tail=initialtext[:start-pos_a]
	if pos_b==end:
		newelem.tail=""
	else:
		newelem.tail=initialtext[-(pos_b-end):]
		
	elem.getparent().insert(parentInd+1,newelem)
	return len(etree.tostring(newelem))-len(newelem.text)-len(newelem.tail)
########################################
def insertIn(elem,ngram,theclass,pos_a,pos_b,start,end):
	# insert tag and keep text/tail
	# elem.text = a + ngram + b
	rtree = elem.getroottree()
	#print 'INSERTING ('+theclass+') inside ELEMENT:'+ rtree.getpath(elem)
	#curid = elem.get("id")
	# 1) if already exact tag
	#elem.set("id",curid+"TUNED")
	# 2) else insert new one
	
	newelem = etree.Element("span")
	newelem.set("class",theclass)
	newelem.text = ngram
	
	initialtext = elem.text
	if pos_a==start:
		elem.text=""
	else:
		elem.text=initialtext[:start-pos_a]
	if pos_b==end:
		newelem.tail=""
	else:
		newelem.tail=initialtext[-(pos_b-end):]
		
	elem.insert(0,newelem)
	#print "AAAAA",elem.attrib
	return len(etree.tostring(newelem))-len(newelem.text)-len(newelem.tail)
def insertUpdate(elem,theclass):
	# we are lucky it was exactly a tag
	elem.set("class",elem.get("class")+" "+theclass)
	return len(" "+theclass)
########################################
class modif:
	def __init__(self,i,o,st):
		self.start=i
		self.end=o
		self.theclass = st
########################################
class XpathOffsetUpdater():
#	tree = etree.parse('./entretienpetite.xml')
#	root = tree.getroot()
	def __init__(self,modifs):
		self.currentpos=0
		self.modifs = modifs
		self.start = self.modifs[0].start
		self.end = self.modifs[0].end
		self.e='inserting'
		self.more='yes'
	def nextPos(self):
		self.e='inserting'
		self.currentpos +=1
		if self.currentpos==len(self.modifs):
			self.more='no'
	def run(self,source):
		allt=""
		buff=0
		for event,elem in etree.iterparse(source,events=('start','end')):
			thetree = elem.getroottree()
			if event == 'start':
				#print '========= START',elem.tag
				atts = elem.attrib
				attstr=''
				for k,v in atts.items():
					attstr+=' '+k+'="'+v+'"'
				allt += '<'+elem.tag+attstr+'>'
				pos_a = len(allt)
				if elem.text is not None:
					allt += elem.text
				pos_b = len(allt)
				#print 'POSSTART',pos_a,pos_b
				# ====================================
				while self.e=='inserting' and self.more=='yes':
					self.e='end'
					start = self.modifs[self.currentpos].start
					end = self.modifs[self.currentpos].end
					#pos_a+=buff
					#pos_b+=buff
					#print 'POSse',self.modifs[self.currentpos].theclass,start,end
					#print 'POSab',pos_a,pos_b
					if start==pos_a and end==pos_b:
						buff += insertUpdate(elem,self.modifs[self.currentpos].theclass)
						#print 'BUFFup=',buff
						self.nextPos()
					if (start>pos_a and end==pos_b) or (start==pos_a and end<pos_b) or (start>pos_a and end<pos_b):
						buff += insertIn(elem,allt[start:end],self.modifs[self.currentpos].theclass,pos_a,pos_b,start,end)
						#print 'BUFFin=',buff
						self.nextPos()
				self.e='inserting'
				# ====================================
			elif event == 'end':
				#print '========= END',elem.tag
				allt += '</'+elem.tag+'>'
				pos_a = len(allt)
				if elem.tail is not None:
					allt += elem.tail
					pos_b = len(allt)
				#print 'POSEND',pos_a,pos_b
				# ====================================
				while self.e=='inserting' and self.more=='yes':
					self.e='end'
					start = self.modifs[self.currentpos].start+buff
					end = self.modifs[self.currentpos].end+buff
					if pos_b>start:
						buff += insertTail(elem,allt[start:end],self.modifs[self.currentpos].theclass,pos_a,pos_b,start,end)
						self.nextPos()
				self.e='inserting'
				# ====================================
		return thetree,buff
########################################
"""