# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

def backButton(var):
  url = reverse(var)
  return """<table align='center'>
              <tr height='50px'>
                <td><a class='button' href='"""+url+"""'><span>zur&uuml;ck</span></a></td>
              </tr>
            </table>"""
            

def drawDepts(var):
  if var.dept_status == 0:
    return "<b>"+str(var.depts)+" &euro;</b>"
  elif var.dept_status == -1 or var.id == 1:
    return "<b class='green'>"+str(var.depts)+" &euro;</b>"
  elif var.dept_status == 1:
    return "<b class='red'>"+str(var.depts)+" &euro;</b>"
  else:
    return "<b class='redblink'>"+str(var.depts)+" &euro;</b>"
    
def disableButton(var, lock):
  user = var;
  if user.id != 1 and (user.dept_status or lock or user.locked) and user.dept_status != -1:
    return "disabled='disabled'"
  else:
    return ""
   
backButton.is_safe = True
drawDepts.is_safe = True
disableButton.is_safe = True
register = template.Library()
register.filter('backButton', backButton)
register.filter('drawDepts', drawDepts)
register.filter('disableButton', disableButton)