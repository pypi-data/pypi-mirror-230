import string

from django.shortcuts import render

from django_apiview.views import apiview
from fastutils import pinyinutils



@apiview
def titleToCode(title):
    return pinyinutils.to_pinyin(title, clean_chars=string.ascii_letters + string.digits + "_-.")

