# Copyright 2016 - 2021, Cisco Systems, Inc., all rights reserved.
import pytz
import json

from django.db import models


def convert_datetime(dateobj, to_tz):
    try:
        tz = pytz.timezone(to_tz)
        return dateobj.astimezone(tz)
    except Exception:
        return dateobj


def format_date(dateobj, tz=None):
    if not dateobj:
        return ''
    dt = convert_datetime(dateobj, tz) if tz else dateobj
    return dt.strftime("%b %d %Y %I:%M:%S %p %Z")


def get_instance(key):
    ysettree = YangSetTree.objects.filter(key=key)
    return ysettree


class YangSetJSON(models.Model):
    data = models.TextField(default="", null=True, blank=True)

    def __str__(self):
        tree_len = len(self.data)
        tree = json.loads(self.data)
        name = tree.get('text', 'No text found')
        return '{0} - size: {1}'.format(name, tree_len)

    def __unicode__(self):
        tree_len = len(self.data)
        tree = json.loads(self.data)
        name = tree.get('text', 'No text found')
        return '{0} - size: {1}'.format(name, tree_len)


class YangSetTree(models.Model):
    """Save the JsTree data."""
    key = models.CharField(default="", max_length=2550, primary_key=True)
    supports = models.CharField(default="", max_length=2550)
    tree = models.ForeignKey(
        YangSetJSON,
        default=None,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        entry = 'YANG Set Key: {0}\n'.format(self.key)
        entry += self.tree.__str__()
        return entry

    def __unicode__(self):
        entry = 'YANG Set Key: {0}\n'.format(self.key)
        entry += self.tree.__str__()
        return entry
