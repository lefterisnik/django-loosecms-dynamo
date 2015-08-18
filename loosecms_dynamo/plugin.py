# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.template import loader
from django.contrib import admin
from django.apps import apps

from .models import *
from .forms import *
import utils

from loosecms.plugin_pool import plugin_pool
from loosecms.plugin_modeladmin import PluginModelAdmin


def get_plugins_admin():
    plugin_admin = {}
    appconfig = apps.get_app_config('loosecms_dynamo')
    for model in list(appconfig.get_models()):
        if model._meta.object_name != DynamoManager._meta.object_name and \
                        model._meta.object_name != Dynamo._meta.object_name:

            attrs = dict(
                model=model,
                name=model._meta.object_name,
                plugin=True,
                form=utils.get_form(model),
                template='plugin/dynamo.html',
                extra_initial_help=None,
            )

            DynamoPluginAdmin = type(model._meta.object_name + 'Plugin', (PluginModelAdmin, ), attrs)
            plugin_admin[model] = DynamoPluginAdmin
            plugin_pool.register_plugin(DynamoPluginAdmin)
            return plugin_admin


            #def render