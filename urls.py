from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('doxer',

	(r'^$', 'ngramer.views.home'),
	
	(r'^reset$', 'ngramer.views.reset'),
	(r'^solrkill$', 'ngramer.views.killSolrProcess'),
	
	(r'^upload$', 'ngramer.views.uploadFile'),
	
	(r'^d/xslt/(?P<did>\d+)/(?P<typ>\w+)$', 'ngramer.views.edMakeXslt'),
	(r'^d/enrichxml/(?P<did>\d+)/$', 'ngramer.views.edMakeEnrichXmlWithNgrams'),
	(r'^d/groupngrams/(?P<did>\d+)/$', 'ngramer.views.edMakeGroupNgrams'),
	
	(r'^d/delete/(?P<did>\d+)/$', 'ngramer.views.edDelete'),
	
	(r'^d/refresh/(?P<did>\d+)/$', 'ngramer.views.edRefresh'),
	
	(r'^d/rawlook/(?P<did>\d+)/$', 'ngramer.views.edRawLook'),
	(r'^d/rawget/(?P<did>\d+)/$', 'ngramer.views.edRawGet'),
)
