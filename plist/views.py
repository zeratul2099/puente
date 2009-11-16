# -*- coding: UTF-8 -*-
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



from puente.plist.models import Customer, RegisterForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from datetime import date
import datetime, sys
from datetime import datetime as dt
from decimal import Decimal
from email.message import Message
import smtplib, simplejson
from email.mime.text import MIMEText
from email.header import Header



prices = [ 60, 80, 100, 130, 150 ]
pPrices = [ 40, 60, 80, 100 ]
version = 1.6
# if a new customer is added
def registerCustomer(request):
    # process form data...
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                if 'isPuenteBox' in request.POST:
                    isP = True
                else:
                    isP = False
                weekday = date.today().weekday()
                last_sunday = datetime.date.today() - datetime.timedelta(weekday+1)
                new_customer = Customer(name=request.POST['nameBox'],
                                        room=request.POST['roomBox'],
                                        email=request.POST['emailBox'],
                                        depts=0,
                                        weeklySales=0,
                                        salesSince=last_sunday,
                                        lastPaid=dt.now(),
                                        dept_status=0,
                                        isPuente=isP)
                new_customer.save()
                # ... an return to list ...
                return HttpResponseRedirect("..")
            except:
                # .. or something went wrong
                return render_to_response("plist_register.html", {"error" : "Customer still in database",
                                                                  "registerForm" : form,
                                                                  "version" : version,  })
    else:
        # display empty form
        form = RegisterForm()
    
    return render_to_response("plist_register.html", {"registerForm" : form,
                                                      "version" : version,  })
            
# display list. this method processes most incoming data from forms
def customerList(request):
    unname = ""
    unmoney = ""
    error = ""
    response_dict = {}
    # if some data come in (a submit button were pressed)
    if request.method == 'POST' and "customer" in request.POST and request.POST['customer'] != "":
        # get the corresponding customer
        customer = get_object_or_404(Customer, name=request.POST['customer'])
        unname = customer.name
        # someone bought a drink
        if "buy" in request.POST:
            money = Decimal(request.POST['buy'])/100
            # update depts ...
            customer.depts += money
            # ... and the weekly sales
            customer.weeklySales += money
            # save for undo function
            unmoney = money
        # someone paid
        elif "pay" in request.POST:
            try:
                # prevent overflow
                money = Decimal(request.POST['money'].replace(',', '.'))
                if money - customer.depts < Decimal(1000):
                    customer.depts -= money
                    # customer paid ...
                    if money > 0:
                        customer.lastPaid = dt.now()
                        unmoney = "-%s" %money
                    # ... or bought
                    else:
                        customer.weeklySales -= money
                else:
                    error = "Soviel hat doch niemand wirklich bezahlt!"
 
            except:
                pass
        # undo the last transaction
        elif "undo" in request.POST and "unmoney" in request.POST and request.POST['unmoney'] != "":
            unname = ""
            money = Decimal(request.POST['unmoney'])
            customer.depts -= money
            customer.weeklySales -= money
        # customer receives a remembermail of his depts
        elif "inform" in request.POST:

            # construct mail ...
            fr = "puente.oss@googlemail.com"
            
            to = customer.email

            text = "\nHallo "
            text+= "%s" %(customer.name)
            text += ",\n"
            text += "du hast in der Puente %.2f Euro Schulden.\n" %(customer.depts)
            text += "Bitte bezahle diese bei deinem naechsten Besuch\n"
            text += "Viele Gruesse, dein Puententeam"
            #msg = Message()
            msg = MIMEText(text, 'plain', _charset='ISO-8859-1')
            #msg.set_payload(text)
            msg["Subject"] = Header("[Pünte]Zahlungserinnerung", 'utf8')
            fromhdr = Header("Pünte", 'utf8')
            fromhdr.append("<%s>"%fr, 'ascii')
            msg["From"] = fromhdr
            tohdr = Header("%s"%customer.name, 'utf8')
            tohdr.append("<%s>" %( customer.email), 'ascii')
            msg["To"] = tohdr
            date = dt.now()
            msg["Date"] = date.strftime("%a, %d %b %Y %H:%M:%S")
            # ... and try to send it
            try:
                
                s = smtplib.SMTP('smtp.gmail.com', 587)
                #s = smtplib.SMTP('134.106.143.1')
                s.ehlo()
                s.starttls()
                s.login(fr, "lastpub897km")
                s.sendmail(fr, customer.email, msg.as_string())
                error = "Erinnerungsmail an %s verschickt" %(customer.name)
                s.quit()
            except:
                s.quit()
                error = "Fehler beim Versenden"
        # Update customers comment
        elif "addComment" in request.POST:
            customer.comment = request.POST["comment"]
        # update customers status:
        # 0 for normal
        # 1 for warning (red number)
        # 2 for drinkstop
        if (customer.isPuente & (customer.depts < 50)) | (customer.depts < 10):
            customer.dept_status = 0
        elif (customer.isPuente & (customer.depts < 100)) | (customer.depts < 15):
            customer.dept_status = 1
        else:
            customer.dept_status = 2
        # save all changes to customer in database
        customer.save()
        # ajax stuff

        # delete customer if dept-free
        if "delete" in request.POST and customer.depts == 0:
            customer.delete()
    # get all customer to update and calculate weekly sales
    allCustomers = Customer.objects.filter(isPuente=False).order_by("name")
    sum = [ 0, 0, 0, 0 ]
    for c in allCustomers:
        if datetime.date.today() - c.salesSince > datetime.timedelta(7):
            c.salesSince = c.salesSince + datetime.timedelta(7)
            c.weeklySales = 0
            c.save()
        sum[0] += Decimal(c.weeklySales)
        sum[1] += Decimal(c.depts)
    # get the puententeam to update and calculate weekly sales
    pMen = Customer.objects.filter(isPuente=True).order_by("name")
    for c in pMen:
        if datetime.date.today() - c.salesSince > datetime.timedelta(7):
            c.salesSince = c.salesSince + datetime.timedelta(7)
            c.weeklySales = 0
            c.save() 
        sum[2] += Decimal(c.weeklySales)
        sum[3] += Decimal(c.depts)

    # return customers to the html-template
    if "ajax" in request.POST:
        response_dict = { "id" : customer.id }
        response_dict.update({"depts" : str(customer.depts)})
        response_dict.update({"status" : customer.dept_status})
        response_dict.update({"unname" : unname})
        response_dict.update({"unmoney" : str(unmoney)})
        response_dict.update({"ptSum" : str(sum[3])})
        response_dict.update({"ptSales" : str(sum[2])})
        response_dict.update({"cSum" : str(sum[1])})
        response_dict.update({"cSales" : str(sum[0])})
        # germanisation of weekdays
        lastPaidStr = customer.lastPaid.strftime("%a, %d.%b. %Y")
        lastPaidStr = lastPaidStr.replace("Mon", "Mo")
        lastPaidStr = lastPaidStr.replace("Tue", "Di")
        lastPaidStr = lastPaidStr.replace("Wed", "Mi")
        lastPaidStr = lastPaidStr.replace("Thu", "Do")
        lastPaidStr = lastPaidStr.replace("Fri", "Fr")
        lastPaidStr = lastPaidStr.replace("Sat", "Sa")
        lastPaidStr = lastPaidStr.replace("Sun", "So")
        response_dict.update({"lastPaid" : lastPaidStr})
        return HttpResponse(simplejson.dumps(response_dict), mimetype="application/json")
    else:
        return render_to_response("plist.html", {"customer" : allCustomers,
                                             "pmen" : pMen,
                                             "unname" : unname,
                                             "unmoney" : unmoney,
                                             "error" : error,
                                             "prices" : prices,
                                             "pprices" : pPrices,
                                             "sum" : sum,
                                             "version" : version, })

# get customer data and put into customer detail template
def customerDetails(request, customer_id):
    if request.method == 'POST':
        return HttpResponseRedirect("..")
    customer = get_object_or_404(Customer, id=customer_id)
    return render_to_response("plist_customer.html", {"customer" : customer,
                                                      "version" : version,  })
        
