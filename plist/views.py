from puente.plist.models import Customer, RegisterForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from datetime import date
import datetime
from datetime import datetime as dt
from decimal import Decimal
from email.message import Message
import smtplib


prices = [ 40, 60, 80, 100, 130, 150 ]

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
                                        dept_status=0,
                                        isPuente=isP)
                new_customer.save()
                # ... an return to list ...
                return HttpResponseRedirect("..")
            except:
                # .. or something went wrong
                return render_to_response("plist_register.html", {"error" : "Customer still in database",
                                                                  "registerForm" : form, })
    else:
        # display empty form
        form = RegisterForm()
    
    return render_to_response("plist_register.html", {"registerForm" : form })
            
# display list. this method processes most incoming data from forms
def customerList(request):
    unname = ""
    unmoney = ""
    error = ""
    # if some data come in (a submit button were pressed)
    if request.method == 'POST':
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
                if Decimal(request.POST['money']) - customer.depts < Decimal(1000):
                    customer.depts -= Decimal(request.POST['money'])
                    # customer paid ...
                    if Decimal(request.POST['money']) > 0:
                        customer.lastPaid = datetime.now()
                        unmoney = "-%s" %(request.POST['money'])
                    # ... or bought
                    else:
                        customer.weeklySales -= Decimal(request.POST['money'])
                else:
                    error = "Soviel hat doch niemand wirklich bezahlt!"
 
            except:
                pass
        # undo the last transaction
        elif "undo" in request.POST:
            unname = ""
            money = Decimal(request.POST['unmoney'])
            customer.depts -= money
            customer.weeklySales -= money
        # customer receives a remembermail of his depts
        elif "inform" in request.POST:
            # construct mail ...
            fr = "flensbox@ossnet.uni-oldenburg.de"
            to = customer.email
            text = "\nHallo %s,\n" %(customer.name)
            text += "du hast in der Puente %.2f Euro Schulden.\n" %(customer.depts)
            text += "Bitte bezahle diese bei deinem naechsten Besuch\n"
            text += "Viele Gruesse, dein Puententeam"
            msg = Message()
            msg.set_payload(text)
            msg["Subject"] = "[Puente]Zahlungserinnerung"
            msg["From"] = "Puente <%s>" %(fr)
            msg["To"] = "%s <%s>" %(customer.name, customer.email)
            date = dt.now()
            msg["Date"] = date.strftime("%a, %d %b %Y %H:%M:%S")
            # ... and try to send it
            try:
                
                #s = smtplib.SMTP('smtp.gmail.com', 587)
                s = smtplib.SMTP('134.106.143.1')
                s.ehlo()
                s.starttls()
                s.login(fr, "3ierfl1p")
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
        # delete customer if dept-free
        if "delete" in request.POST and customer.depts == 0:
            customer.delete()
    # get all customer to update and calculate weekly sales
    allCustomers = Customer.objects.all()
    allWeekly = 0
    for c in allCustomers:
        if datetime.date.today() - c.salesSince > datetime.timedelta(7):
            c.salesSince = c.salesSince + datetime.timedelta(7)
            c.weeklySales = 0
            c.save()
        allWeekly += Decimal(c.weeklySales)
    # return customers to the html-template
    return render_to_response("plist.html", {"customer" : allCustomers,
                                             "unname" : unname,
                                             "unmoney" : unmoney,
                                             "error" : error,
                                             "prices" : prices,
                                             "weekly" : allWeekly, })

# get customer data and put into customer detail template
def customerDetails(request, customer_id):
    if request.method == 'POST':
        return HttpResponseRedirect("..")
    customer = get_object_or_404(Customer, id=customer_id)
    return render_to_response("plist_customer.html", {"customer" : customer })
        
