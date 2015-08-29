# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete, pre_save


from .signals import *
from .fields import *

from loosecms.models import Plugin


def get_default():
    dynamo_managers = DynamoManager.objects.count()
    name = 'Dynamo_%s' % dynamo_managers
    return name


class DynamoManager(models.Model):
    title = models.CharField(_('title'), max_length=200,
                             help_text=_('Give the name of the dynamo manager.'))
    name = models.CharField(_('name'), max_length=150, default=get_default,
                            help_text=_('Represent the name of the table in python.'))
    verbose_name = models.CharField(_('verbose name'), blank=True, max_length=100,
                                    help_text=_('Give the name of the table which will appear in admin panel. If set to'
                                                ' null will using the name field.'))
    verbose_name_plural = models.CharField(_('verbose name plural'), blank=True, max_length=100,
                                           help_text=_('Give the name of the table which will appear in admin panel for '
                                                       'the plural. If set to null will using the name field.'))
    ctime = models.DateTimeField(auto_now_add=True)

    utime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title


class Dynamo(models.Model):
    title = models.CharField(_('header title'), max_length=50,
                             help_text=_('Give the name of the header.'))
    name = models.SlugField(_('slug'),
                            help_text=_('Give the slug of the header'))
    type = models.CharField(_('type'), max_length=50, choices=ANSWER_TYPES,
                            help_text=_('Select the type of the field'))
    required = models.BooleanField(_('required'), default=True,
                                   help_text=_('Check this box if you want the field to be required'))
    manager = models.ForeignKey(DynamoManager, verbose_name=_('manager'),
                                help_text=_('Select the dynamo manager.'))
    ctime = models.DateTimeField(auto_now_add=True)

    utime = models.DateTimeField(auto_now=True)

    published = models.BooleanField(_('published'), default=True)

    def __unicode__(self):
        return self.title

    def get_field(self):
        kwargs = {}
        kwargs['blank'] = not self.required
        kwargs['verbose_name'] = self.title

        try:
            return ANSWER_FIELDS[self.type](**kwargs)
        except KeyError:
            return None


class DynamoPluginManager(Plugin):
    title = models.CharField(_('title'), max_length=200,
                             help_text=_('Give some title'))
    limit_choices_to = Q(app_label='loosecms_dynamo') & ~Q(model='Dynamo') & ~Q(model='DynamoManager') &\
                       ~Q(model='DynamoPluginManager')
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'),
                                     limit_choices_to=limit_choices_to,
                                     help_text=_('Select the table that contain the data.'))
    responsive = models.BooleanField(_('responsive'), default=True,
                                     help_text=_('Check this box if you like the table to be fully responsive.'))
    ctime = models.DateTimeField(auto_now_add=True)

    utime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s (%s)" %(self.title, self.type)

post_save.connect(dynamomanager_post_save, sender=DynamoManager)
post_delete.connect(dynamomanager_post_delete, sender=DynamoManager)
pre_save.connect(dynamo_pre_save, sender=Dynamo)
post_save.connect(dynamo_post_save, sender=Dynamo)
post_delete.connect(dynamo_post_delete, sender=Dynamo)
