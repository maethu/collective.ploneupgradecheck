from collective.ploneupgradecheck.files import FileRegistry
from collective.ploneupgradecheck.interfaces import IFileRegistry
from collective.ploneupgradecheck.testing import ZCML_LAYER
from unittest2 import TestCase
from zope.component import getUtility
from zope.interface.verify import verifyClass
import os.path


def relativize_paths(basedir, paths):
    new_paths = []

    if not basedir.endswith('/'):
        basedir = basedir + '/'

    for path in paths:
        assert path.startswith(basedir), '%s does not start with %s' % (path, basedir)
        new_paths.append(path[len(basedir):])

    return new_paths


class TestFileRegistry(TestCase):

    layer = ZCML_LAYER

    def test_implements_interface(self):
        self.assertTrue(IFileRegistry.implementedBy(FileRegistry))
        verifyClass(IFileRegistry, FileRegistry)

    def test_utility_registered(self):
        getUtility(IFileRegistry)

    def test_get_basedir(self):
        registry = getUtility(IFileRegistry)
        self.assertEqual(registry.get_basedir(),
                         os.path.join(os.path.dirname(__file__), 'my.package'))

    def test_find_files(self):
        registry = getUtility(IFileRegistry)

        py_files = relativize_paths(registry.get_basedir(), registry.find_files(['py']))
        self.assertIn('my/package/eventhandlers.py', py_files)
        self.assertNotIn('my/package/configure.zcml', py_files)

        zcml_files = relativize_paths(registry.get_basedir(), registry.find_files(['zcml']))
        self.assertNotIn('my/package/eventhandlers.py', zcml_files)
        self.assertIn('my/package/configure.zcml', zcml_files)

        both_files = relativize_paths(registry.get_basedir(), registry.find_files(['zcml', 'py']))
        self.assertIn('my/package/eventhandlers.py', both_files)
        self.assertIn('my/package/configure.zcml', both_files)

    def test_clear_and_load(self):
        basedir = getUtility(IFileRegistry).get_basedir()

        # use a fresh registry, so that we dont destroy later tests on failure
        registry = FileRegistry()

        self.assertFalse(registry.get_basedir())
        self.assertFalse(registry.find_files())

        registry.load(basedir)

        self.assertTrue(registry.get_basedir())
        self.assertTrue(registry.find_files())

        registry.clear()

        self.assertFalse(registry.get_basedir())
        self.assertFalse(registry.find_files())