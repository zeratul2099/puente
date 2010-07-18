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


def showMenu(request):
    cats = Category.objects.all()
    itemDict = {}
    for c in cats:
        cItems = MenuItem.objects.filter(category=c)
        itemDict[c] = cItems
    items = MenuItem.objects.all()
    print itemDict
    return render_to_response("pmenu_list.html", {"cats":cats, "items":items, "itemDict":itemDict})