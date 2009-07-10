from puente.plist.models import Customer, RegisterForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from datetime import datetime
from decimal import Decimal
from email.message import Message
import smtplib


prices = [ 40, 60, 80, 100, 130, 150 ]

def registerCustomer(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                if 'isPuenteBox' in request.POST:
                    isP = True
                else:
                    isP = False
                new_customer = Customer(name=request.POST['nameBox'],
                                        room=request.POST['roomBox'],
                                        email=request.POST['emailBox'],
                                        depts=0,
                                        lastPaid=datetime.now(),
                                        dept_status=0,
                                        isPuente=isP)
                new_customer.save()
                return HttpResponseRedirect("..")
            except:
                return render_to_response("plist_register.html", {"error" : "Customer still in database",
                                                                  "registerForm" : form, })
    else:
        form = RegisterForm()
    
    return render_to_response("plist_register.html", {"registerForm" : form })
            
            
def customerList(request):
    unname = ""
    unmoney = ""
    error = ""
    if request.method == 'POST':
        customer = get_object_or_404(Customer, name=request.POST['customer'])
        unname = customer.name
        if "buy" in request.POST:
            customer.depts += Decimal(request.POST['buy'])/100
            unmoney = Decimal(request.POST['buy'])/100
        elif "pay" in request.POST:
            try:
                if Decimal(request.POST['money']) - customer.depts < Decimal(1000):
                    customer.depts -= Decimal(request.POST['money'])
                    if Decimal(request.POST['money']) > 0:
                        customer.lastPaid = datetime.now()
                        unmoney = "-%s" %(request.POST['money'])
                else:
                    error = "Soviel hat doch niemand wirklich bezahlt!"
 
            except:
                pass
        elif "undo" in request.POST:
            unname = ""
            customer.depts -= Decimal(request.POST['unmoney'])
        elif "inform" in request.POST:
            #fr = "zeratul2099@googlemail.com"
            fr = "flensbox@ossnet.uni-oldenburg.de"
            to = customer.email
            text = "From:%s\nTo:%s\nSubject:[Puente]Zahlungserinnerung\n" %(fr, to)
            text += "\nHallo %s,\n" %(customer.name)
            text += "du hast in der Puente %.2f Euro Schulden.\n" %(customer.depts)
            text += "Bitte bezahle diese bei deinem naechsten Besuch\n"
            text += "Viele Gruesse, dein Puententeam"
            #msg = Message()
            #msg.set_payload(text)
            #msg["Subject"] = "Zahlungserinnerung"
            #msg["From"] = "Puente <flensbox@ossnet.uni-oldenburg.de>"
            #msg["To"] = "%s" %(customer.email)
            #print msg.as_string()
            try:
                
                #s = smtplib.SMTP('smtp.gmail.com', 587)
                s = smtplib.SMTP('134.106.143.1')
                s.ehlo()
                s.starttls()
                s.login(fr, "3ierfl1p")
                s.sendmail(fr, customer.email, text)
                error = "Erinnerungsmail an %s verschickt" %(customer.name)
                s.quit()
            except:
                s.quit()
                error = "Fehler beim Versenden"

        if (customer.isPuente & (customer.depts < 50)) | (customer.depts < 10):
            customer.dept_status = 0
        elif (customer.isPuente & (customer.depts < 100)) | (customer.depts < 15):
            customer.dept_status = 1
        else:
            customer.dept_status = 2
        customer.save()
        if "delete" in request.POST and customer.depts == 0:
            customer.delete()
    return render_to_response("plist.html", {"customer" : Customer.objects.all(),
                                             "unname" : unname,
                                             "unmoney" : unmoney,
                                             "error" : error,
                                             "prices" : prices, })
def customerDetails(request, customer_id):
    if request.method == 'POST':
        return HttpResponseRedirect("..")
    customer = get_object_or_404(Customer, id=customer_id)
    return render_to_response("plist_customer.html", {"customer" : customer })
        
