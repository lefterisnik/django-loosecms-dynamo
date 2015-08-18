# -*- coding: UTF-8 -*-
from decimal import Decimal
from django.db import models


def get_decimal_field(**kwargs):
    kwargs.setdefault('max_digits', 6)
    kwargs.setdefault('decimal_places', 2)
    kwargs.setdefault('null', True)
    if 'choices' in kwargs:
        kwargs['choices'] = [(Decimal(k),v) for k,v in kwargs['choices']]
    return models.DecimalField(**kwargs)


def get_char_field(**kwargs):
    kwargs.setdefault('max_length', 255)
    kwargs.setdefault('default', "")
    return models.CharField(**kwargs)


def get_text_field(**kwargs):
    kwargs.setdefault('default', "")
    return models.TextField(**kwargs)


def get_integer_field(**kwargs):
    kwargs.setdefault('null', True)
    if 'choices' in kwargs:
        kwargs['choices'] = [(int(k),v) for k,v in kwargs['choices']]
    return models.IntegerField(**kwargs)


ANSWER_FIELDS = {
    'CharField': get_char_field,
    'TextField': get_text_field,
    'IntegerField': get_integer_field,
    'DecimalField': get_decimal_field,
}

ANSWER_TYPES = (
    ('CharField', 'CharField'),
    ('TextField', 'TextField'),
    ('IntegerField', 'IntegerField'),
    ('DecimalField', 'DecimalField'),
)
