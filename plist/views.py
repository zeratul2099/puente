from puente.plist.models import Customer, RegisterForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from datetime import datetime
from decimal import Decimal


prices = [ 40, 60, 80, 100 ]

def registerCustomer(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                new_customer = Customer(name=request.POST['nameBox'],
                                        room=request.POST['roomBox'],
                                        email=request.POST['emailBox'],
                                        depts=0,
                                        lastPaid=datetime.now(),
                                        dept_status=0,)
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
        if customer.depts < 50:
            customer.dept_status = 0
        elif customer.depts < 100:
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
    
        
