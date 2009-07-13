from django.db import models
from django import forms

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=30, unique=True)
    room = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    depts = models.DecimalField(max_digits=5, decimal_places=2)
    isPuente = models.BooleanField()
    # 0 for normal, 1 for alert, 2 for no sale
    dept_status = models.IntegerField()
    weeklySales = models.DecimalField(max_digits=5, decimal_places=2)
    salesSince = models.DateField()
    lastPaid = models.DateTimeField()
    comment = models.TextField()
    def __unicode__(self):
        return self.name

    
class RegisterForm(forms.Form):
    nameBox = forms.CharField(max_length=30, label='Name')
    roomBox = forms.CharField(max_length=30, label='Zimmernummer')
    emailBox = forms.EmailField(max_length=50, label='Email')
    isPuenteBox = forms.BooleanField(label='Puententeam', required=False)

