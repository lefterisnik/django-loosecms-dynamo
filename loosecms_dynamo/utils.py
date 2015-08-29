# -*- coding: utf-8 -*-
from django.db import models, connection, OperationalError
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.utils.importlib import import_module
from django.contrib.admin.sites import NotRegistered
from django.core.urlresolvers import clear_url_caches


## Database actions

def create_db_table(model):
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


def rm_db_table(model):
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(model)


def add_db_field(model, field):
    with connection.schema_editor() as schema_editor:
        schema_editor.add_field(model, field)


def rm_db_field(model, field):
    with connection.schema_editor() as schema_editor:
        schema_editor.remove_field(model, field)


def alter_db_field(model, old_field, new_field):
    with connection.schema_editor() as schema_editor:
        schema_editor.alter_field(model, old_field, new_field)


## Register and unregister model

def get_dynamic_model(model_name):
    app_config = apps.get_app_config('loosecms_dynamo')
    for model in list(app_config.get_models()):
        if model._meta.model_name == model_name.lower():
            return model
    return


def register_dynamic_model(dynamo_manager, fields=None):
    app_config = apps.get_app_config('loosecms_dynamo')
    if dynamo_manager.name.lower() in [x._meta.model_name for x in list(app_config.get_models())]:
        return

    attrs = {
        '__module__': 'loosecms_dynamo.models',
    }

    class Meta:
        managed = False
        if dynamo_manager.verbose_name:
            verbose_name = dynamo_manager.verbose_name
        if dynamo_manager.verbose_name_plural:
            verbose_name_plural = dynamo_manager.verbose_name_plural

    attrs['Meta'] = Meta

    if fields:
        for field in fields:
            attrs[field.name] = field.get_field()

    dynamic_model = type(str(dynamo_manager.name), (models.Model, ), attrs)

    return dynamic_model


def unregister_dynamic_model(model_name):
    app_config = apps.get_app_config('loosecms_dynamo')
    try:
        app_config.models.pop(model_name.lower(), None)
        return
    except LookupError:
        return


## Register and unregister model from admin site

def reregister_in_admin(dynamic_models, dynamic_modeladmin, initial=False):
    if dynamic_modeladmin and initial:
        admin.site.register(dynamic_models, dynamic_modeladmin)
    elif not dynamic_modeladmin and initial:
        admin.site.register(dynamic_models)
    elif not dynamic_modeladmin and not initial:
        unregister_in_admin(dynamic_models)
        admin.site.register(dynamic_models)

    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()


def unregister_in_admin(dynamic_models):
    if not isinstance(dynamic_models, list):
        dynamic_models = [dynamic_models]

    for dynamic_model in dynamic_models:
        if admin.site.is_registered(dynamic_model):
            # First deregister the current definition
            # This is done "manually" because model will be different
            # db_table is used to check for class equivalence.
            for reg_model in admin.site._registry.keys():
                if dynamic_model._meta.db_table == reg_model._meta.db_table:
                    del admin.site._registry[reg_model]

            try:
                admin.site.unregister(dynamic_model)
            except NotRegistered:
                pass

            reload(import_module(settings.ROOT_URLCONF))
            clear_url_caches()
        return


## Check if model exist else raise Exception

def check_model_exist(model_name):
    app_config = apps.get_app_config('loosecms_dynamo')
    for model in list(app_config.get_models()):
        if model._meta.model_name == model_name.lower():
            raise OperationalError
    return


