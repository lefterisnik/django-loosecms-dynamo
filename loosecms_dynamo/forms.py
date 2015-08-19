# -*- coding:utf-8 -*-
from .models import DynamoManager, DynamoPluginManager
from loosecms.forms import PluginForm


class DynamoPluginManagerForm(PluginForm):

    class Meta(PluginForm.Meta):
        model = DynamoPluginManager