# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals

from six import text_type
from xyz_restful.mixins import UserApiMixin
from xyz_util.statutils import do_rest_stat_action, using_stats_db
from rest_framework.response import Response

__author__ = 'denishuang'

from . import models, serializers
from rest_framework import viewsets, decorators, status, permissions
from xyz_restful.decorators import register, register_raw


@register()
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    filter_fields = {
        'name': ['exact'],
        'owner_type': ['exact'],
        'owner_id': ['exact', 'in'],
    }