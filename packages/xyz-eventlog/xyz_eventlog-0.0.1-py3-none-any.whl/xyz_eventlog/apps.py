#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:denishuang

from __future__ import unicode_literals

from django.apps import AppConfig


class Config(AppConfig):
    name = 'xyz_eventlog'
    label = 'eventlog'
    verbose_name = '事件日志'

    def ready(self):
        super(Config, self).ready()
        # from . import receivers