import os
import json
import subprocess
from datetime import datetime
from django.test import TestCase
from yangsuite.paths import set_base_path
from ysfilemanager import YSYangSet
from ysyangtree.models import YangSetJSON, YangSetTree
from ysyangtree.ymodels import (
    DEFAULT_INCLUDED_NODETYPES,
    ALL_NODETYPES,
    ParseYang
)
from ysyangtree.yangsettree import (
    generate_key,
    get_trees,
    create_yangset_tree,
    create_tree_process,
    save_tree_to_database,
    clear_tree_entry,
    BackwardCompatibleYSmodel
)

BASE_DIR = os.path.join(os.path.dirname(__file__), 'data')
set_base_path(BASE_DIR)


def node_callback(stmt=None, parent_data=None, node=None):
    if node is not None:
        node['callback'] = True
    return node


class TestYangSetModel(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.owner = 'test'
        cls.setname = 'testyangset'
        cls.ys = YSYangSet.load(cls.owner, cls.setname)
        cls.queue = datetime.now().strftime('%Y%m%d%H%M%S%f') + '.json'
        cls.default_key = generate_key(
            cls.owner,
            cls.setname,
            'openconfig-interfaces',
            cls.owner,
            'yangsuite-yangtree',
            DEFAULT_INCLUDED_NODETYPES
        )

    def tearDown(self):
        if os.path.isfile(self.queue):
            os.remove(self.queue)
        if len(YangSetTree.objects.filter(key=self.default_key)):
            clear_tree_entry(self.default_key)
        # get_trees API creates its own queue so remove those
        for f in os.listdir('.'):
            if f.endswith('.json'):
                name_extension = os.path.splitext(f)
                if name_extension[0].isdigit():
                    os.remove(f)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_create_tree_process_default(self):
        """Test subprocess call to create JSON tree."""
        create_tree_process(
            self.owner,
            self.setname,
            ['openconfig-interfaces'],
            queue=self.queue
        )
        self.assertTrue(os.path.isfile(self.queue))

        data = json.load(open(self.queue))

        self.assertIn('openconfig-interfaces', data)

        save_tree_to_database(self.ys, data['openconfig-interfaces'])
        tree_obj = YangSetTree.objects.filter(key=self.default_key)
        tree = tree_obj.get().tree

        self.assertIsInstance(tree, YangSetJSON)

        clear_tree_entry(self.default_key)
        tree_obj = YangSetTree.objects.filter(key=self.default_key)
        self.assertEqual(len(tree_obj), 0, 'Tree not removed.')

    def test_get_tree_support_all(self):
        """Get supported tree ALL_NODETYPES no retrieve of main tree."""
        trees = get_trees(
            self.owner,
            self.setname,
            ['openconfig-if-ethernet'],
            nodes=ALL_NODETYPES,
            base_dir=BASE_DIR
        )

        key = self.default_key.replace(
            'openconfig-interfaces', 'openconfig-if-ethernet'
        ).replace('default', 'all')
        tree_obj = YangSetTree.objects.filter(key=key)

        self.assertEqual(len(tree_obj), 1)
        clear_tree_entry(key)

        # Supported tree is still created and added to database.
        key = self.default_key.replace('default', 'all')
        tree_obj = YangSetTree.objects.filter(key=key)
        self.assertEqual(len(tree_obj), 1)

        # API should only return one tree
        self.assertEqual(len(trees), 1)
        self.assertEqual(trees[0]['text'], 'openconfig-if-ethernet')
        # ALL_NODETYPES should have children in tree.
        self.assertIn('children', trees[0])

    def test_get_multiple_tree_no_support_all(self):
        """Get multiple trees ALL_NODETYPES both main and supported."""
        trees = get_trees(
            self.owner,
            self.setname,
            ['openconfig-interfaces', 'openconfig-if-ethernet'],
            nodes=ALL_NODETYPES,
            base_dir=BASE_DIR
        )

        key = self.default_key.replace('default', 'all')
        tree_obj = YangSetTree.objects.filter(key=key)

        self.assertEqual(len(tree_obj), 1)

        key = self.default_key.replace(
            'openconfig-interfaces', 'openconfig-if-ethernet'
        ).replace('default', 'all')
        tree_obj = YangSetTree.objects.filter(key=key)
        self.assertEqual(len(tree_obj), 1)

        self.assertEqual(len(trees), 2)

        for tree in trees:
            self.assertIn(
                tree['text'],
                ['openconfig-interfaces', 'openconfig-if-ethernet']
            )
            # ALL_NODETYPES should have children in tree.
            self.assertIn('children', tree)

    def test_subprocess_tree_create(self):
        """Call subprocess directly to assure successful creation."""

        cmd = [
            'create_yangtree',
            '-o',
            self.owner,
            '-s',
            self.setname,
            '-r',
            self.owner,
            '-p',
            'yangsuite-yangtree',
            '-m',
            'openconfig-interfaces',
            '-q',
            self.queue,
            '-b',
            BASE_DIR,
            '-n',
        ]
        cmd += [nd for nd in DEFAULT_INCLUDED_NODETYPES]

        proc = subprocess.run(cmd, capture_output=True)
        self.assertTrue(
            os.path.isfile(self.queue), proc.stderr.decode('utf-8')
        )

    def test_callback(self):
        """Test node callback function for parsing."""
        model_class = create_yangset_tree(
            self.owner,
            self.setname,
            ['openconfig-interfaces'],
            '',
            node_callback=node_callback,
            base_dir=BASE_DIR
        )
        self.assertIsInstance(model_class, BackwardCompatibleYSmodel)
        self.assertTrue(model_class.jstree['data'][0]['callback'])

    def test_child_class(self):
        """Test node callback function for parsing."""
        model_class = create_yangset_tree(
            self.owner,
            self.setname,
            ['openconfig-interfaces'],
            '',
            child_class=ParseYang,
            base_dir=BASE_DIR
        )
        self.assertIsInstance(model_class, BackwardCompatibleYSmodel)
        self.assertTrue(
            model_class.jstree['data'][0]['text'] == 'openconfig-interfaces'
        )

    def test_get_supported_yangset_tree(self):
        """Support model should return supported tree."""
        model_class = create_yangset_tree(
            self.owner,
            self.setname,
            ['openconfig-if-ethernet'],
            '',
            base_dir=BASE_DIR
        )
        self.assertIsInstance(model_class, BackwardCompatibleYSmodel)
        self.assertTrue(
            model_class.jstree['data'][0]['text'] == 'openconfig-if-ethernet'
        )
        self.assertTrue(
            model_class.jstree['data'][1]['text'] == 'openconfig-interfaces'
        )
