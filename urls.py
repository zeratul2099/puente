from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^sym_gui/', include('sym_gui.foo.urls')),
    (r'^plist/$', 'plist.views.customerList'),
    (r'^plist/(?P<customer_id>\d+)/$', 'plist.views.customerDetails'),
    (r'^plist/register/$', 'plist.views.registerCustomer'),
    (r'^admin/(.*)', admin.site.root),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
