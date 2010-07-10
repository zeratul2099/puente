from django.contrib import admin
from puente.plist.models import Customer, Transaction, PlistSettings, PriceList

admin.site.register(Customer)
admin.site.register(Transaction)
admin.site.register(PlistSettings)
admin.site.register(PriceList)
