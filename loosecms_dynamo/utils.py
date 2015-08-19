# -*- coding: utf-8 -*-
from django.db import models, connection
from django.apps import apps
from django.conf import settings
from django.utils.importlib import import_module
from django.core.urlresolvers import clear_url_caches


def create_db_table(model, fields=None):
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


def register_dynamic_plugin_admin(admin_site):
    app_config = apps.get_app_config('loosecms_dynamo')
    for model in list(app_config.get_models()):
        if not admin_site.is_registered(model):
            # Maybe will be need to customize the admin panel of the dynamic model if add some settings
            # in Dynamo model
            # dynamic_plugin_admin = get_dynamic_plugin_admin(model)
            reregister_in_admin(admin_site, model, None, True)


def get_dynamic_model(model_name):
    app_config = apps.get_app_config('loosecms_dynamo')
    for dynamic_model in list(app_config.get_models()):
        if dynamic_model._meta.object_name == model_name:
            return dynamic_model


def register_dynamic_model(dynamo_manager, fields=None):
    app_config = apps.get_app_config('loosecms_dynamo')
    if dynamo_manager.name in [x._meta.object_name for x in list(app_config.get_models())]:
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
        dynamic_model = app_config.get_model(model_name)
        del dynamic_model
        return
    except LookupError:
        return


def reregister_in_admin(admin_site, model, dynamic_plugin_admin, initial=False):
    if dynamic_plugin_admin and initial:
        admin_site.register(model, dynamic_plugin_admin)
    elif not dynamic_plugin_admin and initial:
        admin_site.register(model)
    elif not dynamic_plugin_admin and not initial:
        if admin_site.is_registered(model):
            admin_site.unregister(model)
            admin_site.register(model)
        else:
            admin_site.register(model)


    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()


def unregister_in_admin(admin_site, model):
    if admin_site.is_registered(model):
        admin_site.unregister(model)

    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()

