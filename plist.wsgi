import os
import sys
# redirect stdout to stderr because of limitations of wsgi
sys.stdout = sys.stderr

# append project dir to path
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJ_DIR)
sys.path.append(os.path.join(PROJ_DIR, '..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'puente.settings'
os.environ['SETTINGS_MODULE'] = 'puente.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


