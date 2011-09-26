from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^sym_gui/', include('sym_gui.foo.urls')),
    (r'^pmenu/$', 'pmenu.views.showMenu'),
    (r'^pmenu/edit/$', 'pmenu.views.menuEdit'),
    (r'^pmenu/pdf/$', 'pmenu.views.generatePdf'),
    (r'^plist/$', 'plist.views.customerList'),
    (r'^plist/(?P<customer_id>\d+)/$', 'plist.views.customerDetails'),
    (r'^plist/edit/(?P<customer_id>\d+)/$', 'plist.views.customerEdit'),
    (r'^plist/register/$', 'plist.views.registerCustomer'),
    (r'^plist/transactions/(?P<type>\w*)/(?P<page>\d{1,2})/$', 'plist.views.transactionList'),
    (r'^plist/backup/$', 'plist.views.encryptDatabase'),
    (r'^plist/settings/$', 'plist.views.settingsPage'),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/content/favicon.ico'}),
    #(r'^admin/(.*)', admin.site.root),
    (r'^cache.manifest$', 'plist.views.manifestView'),
    (r'^$', 'plist.views.wrongUrl'),
    (r'^content/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
