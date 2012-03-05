from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('dexter',

	(r'^$', 'doxer.views.home'),
	
	(r'^reset$', 'doxer.views.reset'),
	(r'^solrkill$', 'doxer.views.killSolrProcess'),
	
	(r'^upload$', 'doxer.views.uploadFile'),
	
	(r'^d/xslt/(?P<did>\d+)/(?P<typ>\w+)$', 'doxer.views.edMakeXslt'),
	(r'^d/enrichxml/(?P<did>\d+)/$', 'doxer.views.edMakeEnrichXmlWithNgrams'),
	(r'^d/groupngrams/(?P<did>\d+)/$', 'doxer.views.edMakeGroupNgrams'),
	
	(r'^d/delete/(?P<did>\d+)/$', 'doxer.views.edDelete'),
	
	(r'^d/refresh/(?P<did>\d+)/$', 'doxer.views.edRefresh'),
	
	(r'^d/rawlook/(?P<did>\d+)/$', 'doxer.views.edRawLook'),
	(r'^d/rawget/(?P<did>\d+)/$', 'doxer.views.edRawGet'),
	
	
    # Examples:
    # url(r'^$', 'dexter.views.home', name='home'),
    # url(r'^dexter/', include('dexter.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
