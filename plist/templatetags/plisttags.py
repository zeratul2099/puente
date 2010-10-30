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
            

backButton.is_safe = True

register = template.Library()
register.filter('backButton', backButton)
