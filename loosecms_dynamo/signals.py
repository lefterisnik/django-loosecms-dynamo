# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.apps import apps
from django.db import connection, ProgrammingError, OperationalError
from django.core.management import call_command
import utils

# Constants to check that models are loaded in registry
DEPEND = ['Dynamo', 'DynamoManager']
APP_NAME = 'loosecms_dynamo'
ALREADY_PREPARED = {}

def dynamomanager_post_save(sender, instance, created, **kwargs):
    """ Ensure that a table exists for this logger. """

    # Force our response model to regenerate
    Table = instance.register_model()

    # Create a new table if it's missing
    utils.create_db_table(Table)

    # Reregister the model in the admin
    #utils.reregister_in_admin(admin.site, Table)


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
        DynamoManager = ALREADY_PREPARED[DEPEND[1]]
        Dynamo = ALREADY_PREPARED[DEPEND[0]]

        # Fetch all objects!!! Filter queryset is not possibly as throw an exception
        # django.core.exceptions.AppRegistryNotReady
        # Django docs: https://docs.djangoproject.com/en/1.8/ref/applications/#troubleshooting
        # Executing database queries with the ORM at import time in models modules will also trigger this exception.
        # The ORM cannot function properly until all models are available.
        dynamo_managers = DynamoManager.objects.all()
        dynamo_fields = Dynamo.objects.all()

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