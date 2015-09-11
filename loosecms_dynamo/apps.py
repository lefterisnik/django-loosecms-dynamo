# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.db import ProgrammingError, OperationalError
import utils


class LooseCMSDynamoConfig(AppConfig):
    name = 'loosecms_dynamo'
    verbose_name = _('Loose CMS Plugin - Dynamic Models')

    def ready(self):
        """
        Builds all existing dynamic models at once.
        :param sender:
        :param instance:
        :param kwargs:
        :return: None
        """
        # List to store all dynamic models
        dynamic_models = []
        DynamoManager = self.get_model('DynamoManager')
        Dynamo = self.get_model('Dynamo')

        # Fetch all objects!!! Filter queryset is not possibly as throw an exception
        # django.core.exceptions.AppRegistryNotReady
        # Django docs: https://docs.djangoproject.com/en/1.8/ref/applications/#troubleshooting
        # Executing database queries with the ORM at import time in models modules will also trigger this exception.
        # The ORM cannot function properly until all models are available.
        try:
            dynamo_managers = DynamoManager.objects.all()

            for dynamo_manager in dynamo_managers:
                dynamo_fields = Dynamo.objects.filter(manager=dynamo_manager)
                try:
                    dynamic_model = utils.register_dynamic_model(dynamo_manager, dynamo_fields)
                    dynamic_models.append(dynamic_model)

                    # Create the table if necessary, shouldn't be necessary anyway
                    if dynamic_model:
                        utils.create_db_table(dynamic_model)
                except (ProgrammingError, OperationalError) as e:
                    # The tables are not to database, so we return here to continue the migrate command or
                    # the tables are in database
                    continue
        except (ProgrammingError, OperationalError) as e:
            return

        # Register all dynamic models
        utils.reregister_in_admin(dynamic_models, None, initial=True)

