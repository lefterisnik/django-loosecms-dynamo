# -*- coding: UTF-8 -*-

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.apps import apps
from django.db import connection
from . import utils

# Constants to check that models are loaded in registry
DEPEND = ['Dynamo', 'DynamoManager']
APP_NAME = 'loosecms_dynamo'
ARLEADY_PREPARED = {}

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
    ARLEADY_PREPARED[sender_name] = sender
    if sender_app_name == APP_NAME and all([x in ARLEADY_PREPARED for x in DEPEND]) and sender_name in DEPEND:
        # To avoid circular imports, the model is retrieved from the sender
        DynamoManager = ARLEADY_PREPARED[DEPEND[1]]
        Dynamo = ARLEADY_PREPARED[DEPEND[0]]

        # Fetch all objects!!! Filter querysets is not possibly as
        # throw an exception django.core.exceptions.AppRegistryNotReady
        dynamo_managers = DynamoManager.objects.all()
        dynamo_fields = Dynamo.objects.all()

        for dynamo_manager in dynamo_managers:
            fields = []
            for dynamo_field in dynamo_fields:
                if dynamo_field.manager == dynamo_manager:
                    fields.append(dynamo_field)
            User_Dynamo = utils.register_user_model(dynamo_manager, fields)

            # Create the table if necessary, shouldn't be necessary anyway
            utils.create_db_table(User_Dynamo, fields)