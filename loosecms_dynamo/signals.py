# -*- coding: utf-8 -*-
from django.apps import apps
from .models import *

import utils


def dynamomanager_post_save(sender, instance, created, **kwargs):
    """
    Exam if model exist and if exist delete definition and make a new one, otherwise we create the model
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    model_name = instance.name

    if created:
        # Force our response model to regenerate
        dynamic_model = utils.register_dynamic_model(instance)

        # Create a new table if it's missing
        utils.create_db_table(dynamic_model)

        # Register the model in the admin
        utils.reregister_in_admin(dynamic_model, None, True)
    else:
        # Get the current model if exist
        dynamic_model = utils.get_dynamic_model(model_name)

        # Get all fields associate with this model
        dynamo_fields = instance.dynamo_set.all()

        # Force unregister current model and from admin
        utils.unregister_dynamic_model(model_name)
        utils.unregister_in_admin(dynamic_model)

        # Check if model is deleleted
        utils.check_model_exist(model_name)

        # Create the new model with the new attributes
        dynamic_model = utils.register_dynamic_model(instance, dynamo_fields)

        # Reregister the model in admin
        utils.reregister_in_admin(dynamic_model, None)


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

    if dynamic_model:
        # Delete the table in database
        utils.rm_db_table(dynamic_model)

        # Force unregister model
        utils.unregister_dynamic_model(model_name)

        # Check if model is deleled
        utils.check_model_exist(model_name)

        # Unregister the model in the admin
        utils.unregister_in_admin(dynamic_model)


def dynamo_pre_save(sender, instance, **kwargs):
    """
    Edit field for model
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    model_name = instance.manager.name

    # Get model if exist
    dynamic_model = utils.get_dynamic_model(model_name)
    if dynamic_model:
        # Get field
        new_dynamic_field = instance.get_field()

        # Get old field name
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return

        old_dynamic_field = dynamic_model._meta.get_field(old_instance.name)

        # Retrieve and remove old field from model
        dynamic_model._meta.local_fields.remove(old_dynamic_field)

        apps.clear_cache()

        # Re-add the chancged field in the model
        new_dynamic_field.contribute_to_class(dynamic_model, instance.name)

        # Alter new field to db
        utils.alter_db_field(dynamic_model, old_dynamic_field, new_dynamic_field)

        # Reregister the model in the admin
        utils.reregister_in_admin(dynamic_model, None)


def dynamo_post_save(sender, instance, created, **kwargs):
    """
    Process adding field for model
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    model_name = instance.manager.name

    # Get model if exist
    dynamic_model = utils.get_dynamic_model(model_name)
    if dynamic_model:
        # Get field
        dynamic_field = instance.get_field()
        if created:
            # Add new field to dynamic model
            dynamic_field.contribute_to_class(dynamic_model, instance.name)

            # Add new field to db
            utils.add_db_field(dynamic_model, dynamic_field)

            # Reregister the model in the admin
            utils.reregister_in_admin(dynamic_model, None, False)


def dynamo_post_delete(sender, instance, **kwargs):
    """
    Delete field from model
    :param sender:
    :param instance:
    :param kwargs:
    :return: None
    """
    model_name = instance.manager.name

    # Get old model if exist
    dynamic_model = utils.get_dynamic_model(model_name)

    # Get field
    dynamic_field = instance.get_field()
    dynamic_field.column = instance.name

    # Remove field from model db
    utils.rm_db_field(dynamic_model, dynamic_field)

    # Remove field from model class
    dynamic_field = dynamic_model._meta.get_field(instance.name)

    dynamic_model._meta.local_fields.remove(dynamic_field)

    apps.clear_cache()

    utils.reregister_in_admin(dynamic_model, None)


