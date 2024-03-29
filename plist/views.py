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



from puente.plist.models import Customer, RegisterForm, EditForm, Transaction, PlistSettings, PriceList, SettingsForm
from puente.pmenu.models import MenuItem
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from django.core.servers.basehttp import FileWrapper
from datetime import date
import datetime, sys, os
from datetime import datetime as dt
from decimal import Decimal
from email.message import Message
import smtplib, ftplib, simplejson
from email.mime.text import MIMEText
from email.header import Header
from django.conf import settings as config
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


version = 3.1


# forward to correct url
def wrongUrl(request):
    return HttpResponseRedirect("/plist/")

# if a new customer is added
def registerCustomer(request):
    # process form data...
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                weekday = date.today().weekday()
                last_sunday = datetime.date.today() - datetime.timedelta(weekday+1)
                new_customer = Customer(name=form.cleaned_data['nameBox'],
                                        room=form.cleaned_data['roomBox'],
                                        email=form.cleaned_data['emailBox'],
                                        depts=0,
                                        weeklySales=0,
                                        salesSince=last_sunday,
                                        lastPaid=dt.now(),
                                        dept_status=0,
                                        isPuente=form.cleaned_data['isPuenteBox'],
                                        locked=form.cleaned_data['lockedBox'])
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
    settings, prices, pPrices = readSettings()
    custLimit = settings.custLimit
    custRedLimit = custLimit/2
    teamLimit = settings.teamLimit
    teamRedLimit = teamLimit/2
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
            new_transaction = Transaction(customer=customer, time=dt.now(), price=money)
            new_transaction.save()
        # someone paid
        elif "pay" in request.POST:
            try:
                # prevent overflow
                money = Decimal(request.POST['money'].replace(',', '.'))
                if money - customer.depts < Decimal(1000):
                    if customer.id == 1 and str(money) == str(4.2+float(dt.now().day)/10):
                        customer.depts -= Decimal(7.2+float(dt.now().day)/10)
                    else:
                        customer.depts -= money
                    # customer paid ...
                    if money > 0:
                        customer.lastPaid = dt.now()
                        unmoney = "-%s" %money
                    # ... or bought
                    else:
                        customer.weeklySales -= money
                    new_transaction = Transaction(customer=customer, time=dt.now(), price=-money)
                    new_transaction.save()
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
            new_transaction = Transaction(customer=customer, time=dt.now(), price=-money)
            new_transaction.save()
        # customer receives a remembermail of his depts
        elif "inform" in request.POST:

            # construct mail ...
            fr = config.SENDER_EMAIL
            
            to = customer.email

            text = "Hallo "
            text += "%s" %(customer.name)
            text += ",\n\n"
            text += u"du hast in der Pünte %.2f Euro Schulden.\n" %(customer.depts)
            text += u"Bitte bezahle diese bei deinem nächsten Besuch.\n"
            text += u"Viele Grüße, dein Püntenteam"
            # comment these two lines out to remove signature from mail
            #command = u"echo '%s' | gpg2 --clearsign --passphrase %s --batch -u 'Pünte OSS' --yes -o -"%(text, config.PASSPHRASE)
            #text = os.popen(command.encode('utf-8')).read()
            #msg = Message()
            msg = MIMEText(text, 'plain', _charset='UTF-8')
            #msg.set_payload(text)
            msg["Subject"] = Header("[Pünte]Zahlungserinnerung", 'utf8')
            fromhdr = Header(u"Pünte", 'utf8')
            fromhdr.append(u"<%s>"%fr, 'ascii')
            msg["From"] = fromhdr
            tohdr = Header("%s"%customer.name, 'utf8')
            tohdr.append("<%s>" %( customer.email), 'ascii')
            msg["To"] = tohdr
            date = dt.now()
            msg["Date"] = date.strftime("%a, %d %b %Y %H:%M:%S")
            # ... and try to send it
            try:
                
                s = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
                #s.ehlo()
                #s.starttls()
                s.login(fr, config.PASSPHRASE)
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
        # -1 for negative depts
        # 0 for normal
        # 1 for warning (red number)
        # 2 for drinkstop
        if customer.depts < 0:
            customer.dept_status = -1
        elif (customer.isPuente & (customer.depts < teamRedLimit)) | (customer.depts < custRedLimit):
            customer.dept_status = 0
        elif (customer.isPuente & (customer.depts < teamLimit)) | (customer.depts < custLimit):
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
    lastPaidList = []
    
    for c in allCustomers:
        if datetime.date.today() - c.salesSince > datetime.timedelta(7):
            while c.salesSince + datetime.timedelta(7) < datetime.date.today():
                c.salesSince = c.salesSince + datetime.timedelta(7)
            c.weeklySales = 0
            c.save()
        # create a list of customer ids witch didn't pay for 28 days
        if datetime.datetime.now() - c.lastPaid > datetime.timedelta(settings.markLastPaid):
            lastPaidList.append(c.id)
        sum[0] += Decimal(c.weeklySales)
        sum[1] += Decimal(c.depts)
    # get the puententeam to update and calculate weekly sales
    pMen = Customer.objects.filter(isPuente=True).order_by("name")
    for c in pMen:
        if datetime.date.today() - c.salesSince > datetime.timedelta(7):
            while c.salesSince + datetime.timedelta(7) < datetime.date.today():
                c.salesSince = c.salesSince + datetime.timedelta(7)
            c.weeklySales = 0
            c.save() 
        sum[2] += Decimal(c.weeklySales)
        sum[3] += Decimal(c.depts)
    # only sell on Tuesday and Thursday between 18 and 6 o' clock
    # 0 means Monday, 1 means Tuesday and so on
    if ((datetime.date.today().weekday() == 1 and datetime.datetime.now().hour >= 18)
      or (datetime.date.today().weekday() == 2 and datetime.datetime.now().hour <= 6)
      or (datetime.date.today().weekday() == 3 and datetime.datetime.now().hour >= 18)
      or (datetime.date.today().weekday() == 4 and datetime.datetime.now().hour <= 6)):
        lock = False
    else:
        lock = True
        #lock = False

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
        cLock = False
        if lock or customer.locked:
            cLock = True
        response_dict.update({"lock" : cLock})
        response_dict.update({"isPuente" : customer.isPuente})
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
	itemDict = {}
	for p in prices:
	  items = MenuItem.objects.filter(price=p).order_by("name")
	  itemDict[p] = items
	pItemDict = {}
	for p in pPrices:
	  items = MenuItem.objects.filter(pPrice=p).order_by("name")
	  pItemDict[p] = items
        return render_to_response("plist.html", {"customer" : allCustomers,
                                             "pmen" : pMen,
                                             "unname" : unname,
                                             "unmoney" : unmoney,
                                             "error" : error,
                                             "prices" : prices,
                                             "pprices" : pPrices,
                                             "sum" : sum,
                                             "lastPaidList" : lastPaidList,
                                             "version" : version,
                                             "lock" : lock, 
                                             "itemDict" : itemDict,
                                             "pItemDict" : pItemDict,
                                             "registerForm" : RegisterForm()})

# get customer data and put into customer detail template
def customerDetails(request, customer_id):
    if request.method == 'POST':
        return HttpResponseRedirect("..")
    customer = get_object_or_404(Customer, id=customer_id)
    transactions = Transaction.objects.filter(customer=customer).order_by("time").reverse()
    renderAndSavePlot(transactions, customer.name)
    formDict = {"roomBox":customer.room,
                "emailBox":customer.email,
                "isPuenteBox":customer.isPuente,
                "lockedBox":customer.locked,
                }
    return render_to_response("plist_customer.html", {"customer" : customer,
                                                      "transactions" : transactions[:100],
                                                      "version" : version,
                                                      "form" : EditForm(formDict),
                                                      "comment":customer.comment,})

def customerEdit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST' and "edit" not in request.POST:
        form = EditForm(request.POST)
        if form.is_valid():
            customer.email = form.cleaned_data['emailBox']
            customer.room = form.cleaned_data['roomBox']
            customer.isPuente = form.cleaned_data['isPuenteBox']
            customer.comment = request.POST["comment"]
            customer.locked = form.cleaned_data['lockedBox']
            customer.save()
            return HttpResponseRedirect("../..")
    else:
        formDict = { "roomBox" : customer.room,
                 "emailBox" : customer.email,
                 "isPuenteBox" : customer.isPuente, 
                 "lockedBox" : customer.locked, }
        form = EditForm(formDict)
    return render_to_response("plist_customer_edit.html", {"customer" : customer,
                                                        "form" : form,
                                                      "version" : version,  })

        
def transactionList(request, type, page):
    if type == "p":
        team = True
    else:
        team = False
    itemsPerPage = 100
    actualPage = int(page)
    startItem = (actualPage-1)*itemsPerPage
    endItem = startItem+itemsPerPage
    if type == "a":
        transactions = Transaction.objects.order_by("time").reverse()
    else:
        transactions = Transaction.objects.filter(customer__isPuente=team).order_by("time").reverse()
    numPages = len(transactions)/itemsPerPage + 1
    renderAndSavePlot(transactions, type)
    return render_to_response("plist_transactions.html", {"transactions" : transactions[startItem:endItem],
                                                          "startItem" : startItem,
                                                          "numPages" : range(1,numPages+1),
                                                          "actualPage" : actualPage,
                                                          "type" : type,
                                                      "version" : version,  })


def encryptDatabase(request):
    os.system("echo %s | gpg -es -u 'Pünte OSS' --passphrase-fd 0 --yes -r 'Pünte OSS' %s"%(config.PASSPHRASE, config.DATABASE_NAME))
    file = open("%s.gpg"%(config.DATABASE_NAME))
    #oberon = ftplib.FTP("134.106.143.8")
    #oberon.login()
    #oberon.storbinary("STOR /upload/software/db.gpg", file)
    #oberon.close()
    file.close()
    return HttpResponseRedirect("..")


def renderPlot(transactions):  
    numWeeks = 20
    sums = []
    sum = 0.0
    lastWeek = 0
    try:
      highestDate = transactions[0].time.isocalendar()
    except IndexError:
      return 0
    transactions = transactions.reverse()
    for t in transactions:
        actualWeek = t.time.isocalendar()[1]
        if (highestDate[1]-numWeeks-1 > actualWeek) or (highestDate[0] != t.time.isocalendar()[0]):
	  pass
	  continue
        # add transactions to sum
        if actualWeek == lastWeek:
            if t.price > 0:
                sum += float(t.price)
        # new week
        else:
            diffWeeks = abs(lastWeek - actualWeek)
            # append to sums list
            sums.append(round(sum, 2))
            # if there are empty weeks
            if  diffWeeks > 1 and diffWeeks < 52:
                for i in range(diffWeeks-1):
                    sums.append(round(0.0, 2))
            if t.price > 0:
                sum = float(t.price)
            else:
                sum = 0.0
            lastWeek = actualWeek
    # append last sum
    sums.append(round(sum, 2))
    sums.remove(0.0)
    
    xTickOffset = 1
    if len(sums) > numWeeks:
      xTickOffset = len(sums)-numWeeks+2
      sums = sums[highestDate[1]-numWeeks+1:]
    N = len(sums)

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars
    
    fig = plt.figure(figsize=(12, 6))
    #fig = matplotlib.figure.Figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    rects1 = ax.bar(ind, sums, width, color='r')
    
    
    # add some
    ax.set_ylabel('Euro')
    ax.set_xlabel('Woche')
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels( range(xTickOffset,N+xTickOffset) )
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            #if height != 0.0:
            ax.text(rect.get_x()+rect.get_width()/2, 1.05*height, '%3.2f'%(height),
                    ha='center', va='bottom')
    autolabel(rects1)
    return fig
    
def renderAndSavePlot(transactions, name="plot", path=config.MEDIA_PATH):
    fig = renderPlot(transactions)
    f = open("%sstats/%s.svg"%(path,name), "w")
    fig.savefig(f, format="svg")
    f.close()

def updateCustomerStatus():
    settings, prices, pPrices = readSettings()
    custLimit = settings.custLimit
    custRedLimit = custLimit/2
    teamLimit = settings.teamLimit
    teamRedLimit = teamLimit/2
    customers = Customer.objects.all()
    for customer in customers:
        if customer.depts < 0:
            customer.dept_status = -1
        elif (customer.isPuente & (customer.depts < teamRedLimit)) | (customer.depts < custRedLimit):
            customer.dept_status = 0
        elif (customer.isPuente & (customer.depts < teamLimit)) | (customer.depts < custLimit):
            customer.dept_status = 1
        else:
            customer.dept_status = 2
        # save all changes to customer in database
        customer.save()

def readSettings():
    settings = PlistSettings.objects.all()[0]
    priceResult = PriceList.objects.filter(isPuente=False).order_by('price')
    prices = []
    for pr in priceResult:
        prices.append(pr.price)
    priceResult = PriceList.objects.filter(isPuente=True).order_by('price')
    pPrices = []
    for pr in priceResult:
        pPrices.append(pr.price)
    return (settings, prices, pPrices)

def settingsPage(request):
    settings, prices, pPrices = readSettings()
    if request.method == 'POST':
        if 'add' in request.POST:
            try:
                priceVal = int(request.POST['price'])
            except ValueError:
                return HttpResponseRedirect(".")
            if request.POST['list'] == 'c':
                newPrice = PriceList(isPuente=False, price=priceVal, settings=settings)
            else:
                newPrice = PriceList(isPuente=True, price=priceVal, settings=settings)
            newPrice.save()
            return HttpResponseRedirect(".")
        elif 'list' in request.POST and request.POST['list'] == 'c':
            PriceList.objects.filter(isPuente=False, price=request.POST['price']).delete()
            return HttpResponseRedirect(".")
        elif 'list' in request.POST and request.POST['list'] == 'p':
            PriceList.objects.filter(isPuente=True, price=request.POST['price']).delete()
            return HttpResponseRedirect(".")
        else:
            form = SettingsForm(request.POST)
            if form.is_valid():
                settings.custLimit = form.cleaned_data['custLimitBox']
                settings.teamLimit = form.cleaned_data['teamLimitBox']
                settings.markLastPaid = form.cleaned_data['markLastPaidBox']
                settings.save()
                updateCustomerStatus()
                return HttpResponseRedirect(".")
            
    formDict = {"custLimitBox":settings.custLimit,
                "teamLimitBox":settings.teamLimit,
                "markLastPaidBox":settings.markLastPaid,}
    form = SettingsForm(formDict)
    return render_to_response("plist_settings.html", {"settings":settings,
                                                        "prices":prices,
                                                        "pPrices":pPrices,
                                                        "form":form,})

def manifestView(request):
  #manifestFile = open('media/cache.manifest')
  response = HttpResponse(FileWrapper(file('media/cache.manifest')), content_type='text/cache-manifest')
  response['Content-Disposition'] = 'attachment; filename=cache.manifest'
  return response
