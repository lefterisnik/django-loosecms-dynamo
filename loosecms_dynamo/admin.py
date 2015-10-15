# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import DynamoManager, Dynamo


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
