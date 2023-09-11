# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from six import text_type


class Event(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "事件"
        ordering = ('-create_time',)

    owner_type = models.ForeignKey(ContentType, verbose_name='属主类别', null=True, blank=True,
                                   related_name='eventlog_event_set', on_delete=models.PROTECT)
    owner_id = models.PositiveIntegerField(verbose_name='属主编号', null=True, blank=True, db_index=True)
    owner = GenericForeignKey('owner_type', 'owner_id')
    name = models.CharField("名称", max_length=64)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s.%s@%s" % (self.owner, self.name, self.create_time.isoformat())

    def object_name(self):
        return text_type(self.owner)

    object_name.short_description = "对象名称"


class Period(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "周期"
        ordering = ('-create_time',)

    owner_type = models.ForeignKey(ContentType, verbose_name='属主类别', null=True, blank=True,
                                   related_name='eventlog_period_set', on_delete=models.PROTECT)
    name = models.CharField("结束", max_length=64)
    begin_event = models.CharField("开始", max_length=64)
    end_event = models.CharField("结束", max_length=64)
    is_active = models.BooleanField("有效", blank=False, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s(%s)" % (self.name, self.owner_type)


class Duration(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "时长"
        ordering = ('-create_time',)

    owner_type = models.ForeignKey(ContentType, verbose_name='属主类别', null=True, blank=True,
                                   related_name='eventlog_duration_set', on_delete=models.PROTECT)
    owner_id = models.PositiveIntegerField(verbose_name='属主编号', null=True, blank=True, db_index=True)
    owner = GenericForeignKey('owner_type', 'owner_id')
    period = models.ForeignKey(Period, verbose_name=Period._meta.verbose_name, on_delete=models.PROTECT)
    action_time = models.DateTimeField("发生时间", db_index=True)
    value = models.PositiveIntegerField("秒")
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s(%s)" % (self.name, self.period)