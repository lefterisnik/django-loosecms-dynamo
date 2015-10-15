# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from .models import *

from loosecms.plugin_pool import plugin_pool
from loosecms.plugin_modeladmin import PluginModelAdmin


class DynamoManagerPlugin(PluginModelAdmin):
    model = DynamoPluginManager
    name = _('Dynamic model manager')
    template = "plugin/dynamo.html"
    plugin = True

    def update_context(self, context, manager):
        dynamos = manager.content_type.model_class().objects.all()
        headers = Dynamo.objects.filter(manager__name=manager.content_type.model_class()._meta.object_name)
        context['dynamopluginmanager'] = manager
        context['dynamos'] = dynamos.values()
        context['headers'] = headers
        return context

plugin_pool.register_plugin(DynamoManagerPlugin)