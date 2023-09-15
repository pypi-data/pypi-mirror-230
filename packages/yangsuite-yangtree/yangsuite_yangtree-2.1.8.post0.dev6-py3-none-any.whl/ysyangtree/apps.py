# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import os
import sysconfig
from django.db.utils import OperationalError

try:
    from yangsuite.apps import YSAppConfig
except ImportError:
    from django.apps import AppConfig as YSAppConfig


class YSYangTreeConfig(YSAppConfig):
    name = 'ysyangtree'
    """Python module name/path"""

    verbose_name = (
        "Manages loading, caching, and validation of YANG "
        '(<a href="https://tools.ietf.org/html/rfc6020">RFC 6020</a>, '
        '<a href="https://tools.ietf.org/html/rfc7950">RFC 7950</a>) models. '
        "Represents parsed YANG models as Python dicts and JavaScript trees. "
        "Adds GUI for traversing, searching, and inspecting YANG model trees."
    )
    """More human-readable name"""

    url_prefix = 'yangtree'
    """Prefix under which to include this app's urlpatterns."""

    # Menu items {'menu': [(text, relative_url), ...], ...}
    menus = {
        'Explore': [
            ('YANG', 'explore'),
        ],
    }

    help_pages = [
        ('Exploring YANG', 'index.html'),
    ]

    default = True

    def ready(self):
        """This "ready" function runs at Django bootup.

        yangsuite-yangtree version 2.0.0 database has drastically changed
        from version 1.19.11.  The easiest transition is to just delete the
        old database and let Django create a new one.

        - Repository files are not stored in database so they are not affected.
        - Yangsets are manifest type files that have a list of module/revision
          yang files stored in repositories so they are not affected.
        - All existing yangsets and repositories still show up in UI.
        - When user loads a yang module from a yangset, the jstree is created
          and stored in the new database.

        Since the old way of loading modules from the database was so slow, you
        don’t even notice a difference.

        Upcoming releases of yangsuite-yangtree consider removing this.
        """
        from ysyangtree.models import YangSetJSON
        try:
            if 'DOCKER_RUN' in os.environ:
                return
            # table does not exist in old database and this will throw an error
            obj = YangSetJSON.objects.first()  # noqa
        except OperationalError:
            media = os.getenv('MEDIA_ROOT')
            if media and os.path.isfile(os.path.join(media, 'db.sqlite3')):
                print('Removing database for upgrade.')
                os.remove(os.path.join(media, 'db.sqlite3'))
            if media and os.path.isdir(os.path.join(
                sysconfig.get_paths()['purelib'],
                'ysyangtree',
                'migrations')
            ):
                print('Removing migration files.')
                path = os.path.join(
                    sysconfig.get_paths()['purelib'],
                    'ysyangtree',
                    'migrations'
                )
                for f in os.listdir(path):
                    if f == '__init__.py':
                        continue
                    if f.endswith('.py'):
                        os.remove(os.path.join(path, f))

        except Exception as exc:
            print('Unable to check database: {0}'.format(str(exc)))
