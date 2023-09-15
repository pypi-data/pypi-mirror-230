# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from django.contrib import admin
from .models import YangSetTree, YangSetJSON


class YangSetJSONAdmin(admin.ModelAdmin):
    """Admin interface for YangSetJSON table.

    Table contains a JStree for user interfaces.
    """
    list_display = ('data',)


class YangSetTreeAdmin(admin.ModelAdmin):
    """Admin interface for YangSetTree table

    Table contains:
    - key: used as the index to retreive the entry
    - supports: a key that is an index to a tree it supports
    - tree: reference to a YangSetJSON table
    """
    list_display = ('key', 'supports', 'tree')


admin.site.register(YangSetJSON, YangSetJSONAdmin)
admin.site.register(YangSetTree, YangSetTreeAdmin)
