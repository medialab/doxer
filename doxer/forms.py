# -*- coding: utf-8 -*-
###########################################################################################
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django import forms

# haystack forms
from haystack.forms import *

from dexter.doxer.models import *
###########################################################################################



from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


#RADIO_CHOICES = ( ('d','doc'), ('s','speak') )
CHECKBOX_CHOICES = ( ('i','interventions'), ('w','wordentities'), ('t','textes') )

# HAYSTACK SEARCH FORMS
############################################################
class SentenceSearchForm(SearchForm):
	# main searchfield
	#q = forms.CharField(required=False, label='chercher:')
	
	#Textes = forms.CharField(required=False)
	rawQuery = forms.BooleanField(required=False)
	autocomplete = forms.BooleanField(required=False)
	autocompletew = forms.BooleanField(required=False)
	#thetype = forms.ChoiceField(required=False, widget=RadioSelect, choices=RADIO_CHOICES)
	
	# to search only in specidied model
	#searchOnly = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple, choices=CHECKBOX_CHOICES)
	
	
	##### DEPRECATED, to do facets or advanced search (by Texte/Speaker)
	#inTextes = forms.ModelMultipleChoiceField(queryset=Texte.objects.all(),widget=forms.CheckboxSelectMultiple(), label='Dans les textes')
	
	#inTextes = forms.ModelMultipleChoiceField(queryset=Texte.objects.all(), label='Dans les textes', required=False)
	#inSpeakers = forms.ModelMultipleChoiceField(queryset=Speaker.objects.all(), label='Participants', required=False)
	
	# trying to change options in certain fields
#	def __init__(self, *args, **kwargs):
		# adding facets parameters a la mano
# 		if kwargs.get('selected_facets') is None:
# 			try:
# 				kwargs['selected_facets'] = args[0].getlist("selected_facets")
# 			except:
# 				donothing=1
# 		super(SearchForm, self).__init__(*args, **kwargs)
			
		#choices = 'ALl Textes'
		#choices = Texte.objects.all()
		#self.fields['inTextes'].queryset = choices 
		
# 	def search(self):
# 		# First, store the SearchQuerySet received from other processing.
# 		sqs = super(MyFacetedSearchForm, self).search()
# 		
# 		#sqs = sqs.filter(content__icontains='et')
# 		
# 		return sqs
############################################################

