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


from puente.pmenu.models import Category, MenuItem
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from django.db import IntegrityError

def showMenu(request):
    itemDict = {}
    cats = Category.objects.all()
    for c in cats:
        cItems = MenuItem.objects.filter(category=c)
        itemDict[c] = cItems
    return render_to_response("pmenu_list.html", { "itemDict":itemDict})
    
def menuEdit(request):
    if request.method == 'POST':
        if 'delItem' in request.POST:
	  print request.POST
	  MenuItem.objects.filter(name=request.POST['delItem']).delete()
	  return HttpResponseRedirect(".")
	elif 'addItem' in request.POST:
	  try:
	      priceVal = int(request.POST['price'])
	      pPriceVal = int(request.POST['pPrice'])
	      catId = int(request.POST['cat'])
	  except ValueError:
	      return HttpResponseRedirect(".")
	  cat = Category.objects.filter(id=catId)[0]
	  try:
	    item = MenuItem(name=request.POST['name'], price=priceVal, pPrice=pPriceVal, category=cat)
	    item.save()
	  except IntegrityError:
	    return HttpResponseRedirect(".")
	elif 'addCat' in request.POST:
	  try:
	    cat = Category(name=request.POST['cat'])
	    cat.save()
	  except IntegrityError:
	    return HttpResponseRedirect(".")
	elif 'delCat' in request.POST:
	  cat = Category.objects.filter(name=request.POST['delCat'])
	  print cat
	  print MenuItem.objects.filter(category=cat)
	  MenuItem.objects.filter(category=cat).delete()
	  cat.delete()
	  return HttpResponseRedirect(".")
    itemDict = {}
    cats = Category.objects.all()
    for c in cats:
        cItems = MenuItem.objects.filter(category=c)
        itemDict[c] = cItems
    return render_to_response("pmenu_list_edit.html", { "itemDict":itemDict})