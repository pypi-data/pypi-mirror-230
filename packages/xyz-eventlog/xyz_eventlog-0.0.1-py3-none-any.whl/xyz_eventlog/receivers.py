# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django.dispatch import receiver
from .signals import to_record_event
from . import models, serializers
import logging
from django.contrib.contenttypes.models import ContentType

log = logging.getLogger('django')


@receiver(to_record_event)
def record_event(sender, **kwargs):
    owner = kwargs.get('owner')
    event = models.Event.objects.create(
        owner_type=ContentType.objects.get_for_model(owner),
        owner_id=owner.id,
        name=kwargs.get('name')
    )
    return serializers.EventSerializer(event).data