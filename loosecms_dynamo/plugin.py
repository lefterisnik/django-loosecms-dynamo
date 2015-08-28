# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from .models import *
from .forms import *

from loosecms.plugin_pool import plugin_pool
from loosecms.plugin_modeladmin import PluginModelAdmin


class DynamoPlugin(PluginModelAdmin):
    model = DynamoPluginManager
    name = _('Dynamo')
    form = DynamoPluginManagerForm
    template = "plugin/dynamo.html"
    plugin = True
    extra_initial_help = None
    fields = ('type', 'placeholder', 'title', 'content_type', 'responsive', 'published')

    def update_context(self, context, manager):
        dynamos = manager.content_type.model_class().objects.all()
        headers = Dynamo.objects.filter(manager__name=manager.content_type.model_class()._meta.object_name)
        context['dynamopluginmanager'] = manager
        context['dynamos'] = dynamos.values()
        context['headers'] = headers
        return context

    def get_changeform_initial_data(self, request):
        initial = {}
        if self.extra_initial_help:
            initial['type'] = self.extra_initial_help['type']
            initial['placeholder'] = self.extra_initial_help['placeholder']

            return initial
        else:
            return {'type': 'DynamoPlugin'}

plugin_pool.register_plugin(DynamoPlugin)