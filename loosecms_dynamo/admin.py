# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import DynamoManager, Dynamo, DynamoPluginManager
from .plugin import DynamoPlugin
import utils


class DynamoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'name': ('title', )}


class DynamoInline(admin.StackedInline):
    prepopulated_fields = {'name': ('title', )}
    model = Dynamo
    extra = 1


class DynamoManagerAdmin(admin.ModelAdmin):
    readonly_fields = ('name', )
    inlines = [
        DynamoInline,
    ]


admin.site.register(DynamoManager, DynamoManagerAdmin)
admin.site.register(DynamoPluginManager, DynamoPlugin)
admin.site.register(Dynamo, DynamoAdmin)
