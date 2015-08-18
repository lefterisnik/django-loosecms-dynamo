# -*- coding: utf-8 -*-
from django.db import models, connection
from django.contrib import admin

from loosecms.forms import PluginForm
from loosecms.models import Plugin


def create_db_table(model, fields):
    if connection.vendor == 'mysql':
        cursor = connection.cursor()
        db_table = model._meta.db_table
        db_fields = "`id` int(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (`id`),"
        for field in fields:
            if field.type == 'CharField':
                db_fields += "`%s` varchar(80) NOT NULL" % field.slug
            elif field.type == 'TextField':
                db_fields += "`%s` longtext NOT NULL" %field.slug

        query = "CREATE TABLE IF NOT EXISTS `%s` (%s) ENGINE=InnoDB  DEFAULT CHARSET=utf8;" % (db_table, db_fields)
        cursor.execute(query)
        return


def get_form(app_model):
    class Meta(PluginForm.Meta):
        model=app_model

    attrs = dict(
        Meta=Meta,
    )
    name = str(app_model._meta.object_name) + 'Form'
    return type(name, (PluginForm, ), attrs)


def register_user_model(dynamo_manager, fields):
        attrs = {
            '__module__': 'loosecms_dynamo.models'
        }

        for field in fields:
            attrs[field.slug] = field.get_field()

        #TODO: create the model to the database
        model = type(str(dynamo_manager.table_name), (Plugin, ), attrs)
        return model


def reregister_in_admin(model, plugin):
    admin.site.register(model, plugin)