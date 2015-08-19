# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save, post_init, pre_init, class_prepared
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.management import g

from .signals import *
from .fields import *

from loosecms.models import Plugin

class_prepared.connect(model_class_prepared, weak=False)


class DynamoManager(models.Model):
    title = models.CharField(_('title'), max_length=200,
                             help_text=_('Give the name of the dynamo manager.'))
    name = models.SlugField(_('name'),
                            help_text=_('Give the name of the table which python will know.'))
    table_name = models.CharField(_('table name'), max_length=50,
                                  help_text=_('Give the name of the database table you want to create.'))
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
    manager = models.ForeignKey(DynamoManager, verbose_name=_('manager'),
                                help_text=_('Select the dynamo manager.'))
    ctime = models.DateTimeField(auto_now_add=True)

    utime = models.DateTimeField(auto_now=True)

    published = models.BooleanField(_('published'), default=True)

    def __unicode__(self):
        return self.title

    def get_field(self):
        kwargs = {}

        try:
            return ANSWER_FIELDS[self.type](**kwargs)
        except KeyError:
            return None









#post_save.connect(dynamomanager_post_save, sender=DynamoManager)
