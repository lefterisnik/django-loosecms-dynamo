# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.apps import apps
from django.db import connection, ProgrammingError, OperationalError

from .models import *

import utils

# Constants to check that models are loaded in registry
DEPEND = ['Dynamo', 'DynamoManager']
APP_NAME = 'loosecms_dynamo'
ALREADY_PREPARED = {}


def dynamomanager_post_delete(sender, instance, **kwargs):
    """
    Delete the model from database and try to delete the reference
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    model_name = instance.name

    # Get model if exist
    dynamic_model = utils.get_dynamic_model(model_name)

    # Delete the table in database
    utils.rm_db_table(dynamic_model)

    # Force unregister model
    utils.unregister_dynamic_model(model_name)

    # Unregister the model in the admin
    utils.unregister_in_admin(admin.site, dynamic_model)


def dynamomanager_post_save(sender, instance, created, **kwargs):
    """
    Exam if model exist and if exist delete definition and make a new one, otherwise we create the model
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    if created:
        model_name = instance.name
        # Force unregister model if exist
        utils.unregister_dynamic_model(model_name)

        # Force our response model to regenerate
        dynamic_model = utils.register_dynamic_model(instance)

        # Create a new table if it's missing
        utils.create_db_table(dynamic_model)

        # Reregister the model in the admin
        utils.reregister_in_admin(admin.site, dynamic_model, None, True)


def dynamo_post_save(sender, instance, created, **kwargs):
    """
    Add or Edit field from model
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    if created:
        model_name = instance.manager.name
        # Get model if exist
        dynamic_model = utils.get_dynamic_model(model_name)

        # Get field
        dynamic_field = instance.get_field()

        # Update model with new field
        setattr(dynamic_model, instance.name, dynamic_field)

        # Add name and column to field
        dynamic_field.name = instance.name
        dynamic_field.column = instance.name

        # Add new field to model
        utils.add_db_field(dynamic_model, dynamic_field)

        # Reregister the model in the admin
        utils.reregister_in_admin(admin.site, dynamic_model, None, False)


def dynamo_post_delete(sender, instance, **kwargs):
    """
    Delete field from model
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    model_name = instance.manager.name
    # Get model if exist
    dynamic_model = utils.get_dynamic_model(model_name)

    # Get field
    dynamic_field = instance.get_field()

    # Add name and column to field
    dynamic_field.name = instance.name
    dynamic_field.column = instance.name

    # Remove field from model class
    dynamic_model._meta.fields = tuple(x for x in dynamic_model._meta.fields if x.name != dynamic_field.name)

    # Remove field from model db
    utils.rm_db_field(dynamic_model, dynamic_field)

    # Reregister the model in the admin
    utils.reregister_in_admin(admin.site, dynamic_model, None, False)


def model_class_prepared(sender, **kwargs):
    """
    Builds all existing dynamic models at once.
    :param sender:
    :param instance:
    :param kwargs:
    :return: None
    """
    sender_name = sender._meta.object_name
    sender_app_name = sender._meta.app_label
    ALREADY_PREPARED[sender_name] = sender
    if sender_app_name == APP_NAME and all([x in ALREADY_PREPARED for x in DEPEND]) and sender_name in DEPEND:
        # To avoid circular imports, the model is retrieved from the sender
        LocalDynamoManager = ALREADY_PREPARED[DEPEND[1]]
        LocalDynamo = ALREADY_PREPARED[DEPEND[0]]

        # Fetch all objects!!! Filter queryset is not possibly as throw an exception
        # django.core.exceptions.AppRegistryNotReady
        # Django docs: https://docs.djangoproject.com/en/1.8/ref/applications/#troubleshooting
        # Executing database queries with the ORM at import time in models modules will also trigger this exception.
        # The ORM cannot function properly until all models are available.
        dynamo_managers = LocalDynamoManager.objects.all()
        dynamo_fields = LocalDynamo.objects.all()

        try:
            for dynamo_manager in dynamo_managers:
                fields = []
                for dynamo_field in dynamo_fields:
                    if dynamo_field.manager == dynamo_manager:
                        fields.append(dynamo_field)
                dynamic_model = utils.register_dynamic_model(dynamo_manager, fields)

                # Create the table if necessary, shouldn't be necessary anyway
                if dynamic_model:
                    utils.create_db_table(dynamic_model, fields)
        except (ProgrammingError, OperationalError) as e:
            # The tables are not to database, so we return here to continue the migrate command
            return