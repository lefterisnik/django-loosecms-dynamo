=================================
Django Loose CMS - Dynamic Models
=================================

A plugin to create dynamic models for Django Loose CMS.

Requirements
------------

Loose CMS Dynamo plugin requires:

* Django version 1.8
* Python 2.6 or 2.7
* django-loose-cms

Quick Start
-----------

1. Instalation via pip::

    pip install https://github.com/lefterisnik/django-loosecms-dynamo/archive/master.zip

2. Add "loosecms_dynamo" to your INSTALLED_APPS setting after "loosecms" like this::

    INSTALLED_APPS = (
        ...
        'loosecms_dynamo',
    )
    
3. Run ``python manage.py migrate`` to create the loosecms_dynamo models.

4. Run development server ``python manage.py runserver`` and visit http://127.0.0.1:8000/ to start
   playing with the cms.