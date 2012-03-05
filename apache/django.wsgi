import os
import sys

sys.path.append('/home/pj/djangos')
sys.path.append('/home/pj/djangos/dexter')

os.environ['DJANGO_SETTINGS_MODULE'] = 'dexter.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
