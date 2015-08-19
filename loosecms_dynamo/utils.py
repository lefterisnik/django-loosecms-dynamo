# -*- coding: utf-8 -*-
from django.db import models, connection
from django.contrib import admin
from django.apps import apps
from django.template import loader

from loosecms.forms import PluginForm
from loosecms.models import Plugin
from loosecms.plugin_pool import plugin_pool
from loosecms.plugin_modeladmin import PluginModelAdmin

import types


def create_db_table(model, fields):
    if connection.vendor == 'mysql':
        cursor = connection.cursor()
        db_table = model._meta.db_table
        db_fields = "`plugin_ptr_id` int(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (`plugin_ptr_id`),"
        for field in fields:
            if field.type == 'CharField':
                db_fields += "`%s` varchar(80) NOT NULL" % field.name
            elif field.type == 'TextField':
                db_fields += "`%s` longtext NOT NULL" %field.name

        query = "CREATE TABLE IF NOT EXISTS `%s` (%s) ENGINE=InnoDB  DEFAULT CHARSET=utf8;" % (db_table, db_fields)
        cursor.execute(query)
        return


def register_dynamic_plugin_admin(admin_site):
    app_config = apps.get_app_config('loosecms_dynamo')
    for model in list(app_config.get_models()):
        if not admin_site.is_registered(model):
            dynamic_plugin_admin = get_dynamic_plugin_admin(model)
            reregister_in_admin(admin_site, model, dynamic_plugin_admin, True)


def get_dynamic_plugin_admin(model):
    attrs = dict(
        model=model,
        name=model._meta.verbose_name,
        plugin=True,
        form=get_form(model),
        template='plugin/dynamo.html',
        extra_initial_help=None,
    )

    fields = tuple(x.name for x in model._meta.get_fields() if (x.model == model and not x.is_relation))

    attrs['fields'] = ('type', 'placeholder')
    attrs['fields'] += fields
    attrs['fields'] += ('published',)

    dynamic_plugin_admin = type(model._meta.object_name + 'Plugin', (PluginModelAdmin, ), attrs)

    def render(self, context, manager):
        t = loader.get_template(self.template)
        context = {}
        return t.render(context)

    def get_changeform_initial_data(self, request):
        initial = {}
        if self.extra_initial_help:
            initial['type'] = self.extra_initial_help['type']
            initial['placeholder'] = self.extra_initial_help['placeholder']

            return initial
        else:
            return {'type': 'TextPlugin'}

    setattr(dynamic_plugin_admin, 'render', render)
    setattr(dynamic_plugin_admin, 'get_changeform_initial', get_changeform_initial_data)

    plugin_pool.register_plugin(dynamic_plugin_admin)
    return dynamic_plugin_admin


def get_form(app_model):
    class Meta(PluginForm.Meta):
        model = app_model

    attrs = dict(
        Meta=Meta,
    )
    name = str(app_model._meta.object_name) + 'Form'
    return type(name, (PluginForm, ), attrs)


def register_dynamic_model(dynamo_manager, fields):
    app_config = apps.get_app_config('loosecms_dynamo')
    if dynamo_manager.name in [x._meta.object_name for x in list(app_config.get_models())]:
        return

    attrs = {
        '__module__': 'loosecms_dynamo.models',
    }

    class Meta:
        if dynamo_manager.verbose_name:
            verbose_name = dynamo_manager.verbose_name
        if dynamo_manager.verbose_name_plural:
            verbose_name_plural = dynamo_manager.verbose_name_plural

    attrs['Meta'] = Meta

    for field in fields:
        attrs[field.name] = field.get_field()

    #TODO: create the model to the database
    dynamic_model = type(str(dynamo_manager.name), (Plugin, ), attrs)

    def __unicode__(self):
        return "(%s)" %(self.type)

    setattr(dynamic_model, '__unicode__', __unicode__)
    return dynamic_model


def reregister_in_admin(admin_site, model, dynamic_plugin_admin, initial=False):
    if initial:
        admin_site.register(model, dynamic_plugin_admin)