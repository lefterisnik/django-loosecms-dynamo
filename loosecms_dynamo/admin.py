# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import DynamoManager, Dynamo
import utils


class DynamoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'name': ('title', )}


class DynamoInline(admin.StackedInline):
    prepopulated_fields = {'name': ('title', )}
    model = Dynamo
    extra = 1


class DynamoManagerAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'name': ('title', ),
        'table_name': ('name', ),
    }
    inlines = [
        DynamoInline,
    ]


admin.site.register(DynamoManager, DynamoManagerAdmin)
admin.site.register(Dynamo, DynamoAdmin)

utils.register_dynamic_plugin_admin(admin.site)
