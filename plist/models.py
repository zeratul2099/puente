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



class Customer(models.Model):
    name = models.CharField(max_length=30, unique=True)
    room = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    depts = models.DecimalField(max_digits=5, decimal_places=2)
    isPuente = models.BooleanField()
    # 0 for normal, 1 for alert, 2 for no sale
    dept_status = models.IntegerField()
    weeklySales = models.DecimalField(max_digits=6, decimal_places=2)
    salesSince = models.DateField()
    lastPaid = models.DateTimeField()
    comment = models.TextField()
    def __unicode__(self):
        return self.name

class Transaction(models.Model):
    customer = models.ForeignKey(Customer)
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    def __unicode__(self):
        return self.customer.name


class RegisterForm(forms.Form):
    nameBox = forms.CharField(max_length=30, label='Name')
    roomBox = forms.CharField(max_length=30, label='Zimmernummer')
    emailBox = forms.EmailField(max_length=50, label='Email')
    isPuenteBox = forms.BooleanField(label='Puententeam', required=False)
