# -*- coding: utf-8 -*-
from django.contrib import admin
from django.apps import apps
from .models import DynamoManager, Dynamo
import plugin

class DynamoInline(admin.StackedInline):
    model = Dynamo
    extra = 1


class DynamoManagerAdmin(admin.ModelAdmin):
    inlines = [
        DynamoInline,
    ]


admin.site.register(DynamoManager, DynamoManagerAdmin)
admin.site.register(Dynamo)
plugin_admin = plugin.get_plugins_admin()
for model in plugin_admin:
    admin.site.register(model, plugin_admin[model])