# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import loosecms_dynamo.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('loosecms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dynamo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Give the name of the header.', max_length=50, verbose_name='header title')),
                ('name', models.SlugField(help_text='Give the slug of the header', verbose_name='slug')),
                ('type', models.CharField(help_text='Select the type of the field', max_length=50, verbose_name='type', choices=[(b'CharField', b'CharField'), (b'TextField', b'TextField'), (b'IntegerField', b'IntegerField'), (b'DecimalField', b'DecimalField')])),
                ('required', models.BooleanField(default=True, help_text='Check this box if you want the field to be required', verbose_name='required')),
                ('ctime', models.DateTimeField(auto_now_add=True)),
                ('utime', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=True, verbose_name='published')),
            ],
        ),
        migrations.CreateModel(
            name='DynamoManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Give the name of the dynamo manager.', max_length=200, verbose_name='title')),
                ('name', models.CharField(default=loosecms_dynamo.models.get_default, help_text='Represent the name of the table in python.', max_length=150, verbose_name='name')),
                ('verbose_name', models.CharField(help_text='Give the name of the table which will appear in admin panel. If set to null will using the name field.', max_length=100, verbose_name='verbose name', blank=True)),
                ('verbose_name_plural', models.CharField(help_text='Give the name of the table which will appear in admin panel for the plural. If set to null will using the name field.', max_length=100, verbose_name='verbose name plural', blank=True)),
                ('ctime', models.DateTimeField(auto_now_add=True)),
                ('utime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='DynamoPluginManager',
            fields=[
                ('plugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='loosecms.Plugin')),
                ('title', models.CharField(help_text='Give some title', max_length=200, verbose_name='title')),
                ('responsive', models.BooleanField(default=True, help_text='Check this box if you like the table to be fully responsive.', verbose_name='responsive')),
                ('ctime', models.DateTimeField(auto_now_add=True)),
                ('utime', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType', help_text='Select the table that contain the data.')),
            ],
            bases=('loosecms.plugin',),
        ),
        migrations.AddField(
            model_name='dynamo',
            name='manager',
            field=models.ForeignKey(verbose_name='manager', to='loosecms_dynamo.DynamoManager', help_text='Select the dynamo manager.'),
        ),
    ]
