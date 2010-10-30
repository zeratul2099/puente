# -*- coding: utf-8 -*-
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django.db import models
from django import forms
from datetime import datetime
from django.forms.widgets import TextInput, DateInput, DateTimeInput, TimeInput

class Html5EmailForm(TextInput):
    input_type = 'email'

class Html5NumberForm(TextInput):
    input_type = 'number'

class Html5RangeForm(TextInput):
    input_type = 'range'

class Customer(models.Model):
    name = models.CharField(max_length=30, unique=True)
    room = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    depts = models.DecimalField(max_digits=5, decimal_places=2)
    isPuente = models.BooleanField()
    # 0 for normal, 1 for alert, 2 for no sale, -1 for deposit
    dept_status = models.IntegerField()
    weeklySales = models.DecimalField(max_digits=6, decimal_places=2)
    salesSince = models.DateField()
    lastPaid = models.DateTimeField()
    comment = models.TextField()
    locked = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name

class Transaction(models.Model):
    customer = models.ForeignKey(Customer)
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    def __unicode__(self):
        return self.customer.name+": "+self.time.strftime("%H:%M, %d. %b.")

class PlistSettings(models.Model):
    markLastPaid = models.IntegerField()
    custLimit = models.IntegerField()
    teamLimit = models.IntegerField()
  
class PriceList(models.Model):
    price = models.IntegerField()
    isPuente = models.BooleanField()
    settings = models.ForeignKey(PlistSettings)
    def __unicode__(self):
        return "%d, %s"%(self.price, self.isPuente)
        
class RegisterForm(forms.Form):
    nameBox = forms.CharField(max_length=30, label='Name', widget=TextInput(attrs={'placeholder':'Name'}))
    roomBox = forms.CharField(max_length=30, label='Zimmernummer', widget=TextInput(attrs={'placeholder':'Zimmernummer'}))
    emailBox = forms.EmailField(max_length=50, label='Email', widget=Html5EmailForm(attrs={'placeholder':'E-Mail'}))
    isPuenteBox = forms.BooleanField(label='Puententeam', required=False)
    lockedBox = forms.BooleanField(label='Gesperrt', required=False)
    
class EditForm(forms.Form):
    emailBox = forms.EmailField(max_length=50, label='Email', widget=Html5EmailForm(attrs={'placeholder':'E-Mail'}))
    roomBox = forms.CharField(max_length=30, label='Zimmernummer', widget=TextInput(attrs={'placeholder':'Zimmernummer'}))
    isPuenteBox = forms.BooleanField(label='Puententeam', required=False)
    lockedBox = forms.BooleanField(label='Gesperrt', required=False)
    
    
class SettingsForm(forms.Form):
    custLimitBox = forms.CharField(max_length=3, label='Limit (Euro)', widget=Html5NumberForm(attrs={'placeholder':'Limit', 'min':'0','max':'100','step':'1'}))
    teamLimitBox = forms.CharField(max_length=3, label='Teamlimit (Euro)', widget=Html5NumberForm(attrs={'placeholder':'Teamlimit', 'min':'0','max':'100','step':'1'}))
    markLastPaidBox = forms.CharField(max_length=3, label='zuletzt bezahlt Rot markieren (Tage)', widget=Html5NumberForm(attrs={'placeholder':'zuletzt bezahlt', 'min':'0','max':'100','step':'1'}))