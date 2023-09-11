# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import Signal

to_record_event = Signal(providing_args=["owner", "name"])
