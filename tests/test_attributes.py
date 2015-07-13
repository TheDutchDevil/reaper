import json
import numbers
import os
import pickle
import tempfile
import types
import unittest

from lib.attributes import Attributes
from lib.database import Database


class AttributesTestCase(unittest.TestCase):
    def setUp(self):
        parentpath = (
            os.path.abspath(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    os.pardir
                )
            )
        )
        manifestpath = os.path.join(parentpath, 'manifest.json')
        self.rawattributes = None
        with open(manifestpath, 'r') as file_:
            self.rawattributes = json.load(file_)['attributes']

        configpath = os.path.join(parentpath, 'config.json')
        self.rawsettings = None
        with open(configpath, 'r') as file_:
            self.rawsettings = json.load(file_)['options']['datasource']

    def test_init(self):
        # Arrange
        expected = len(self.rawattributes)

        # Act
        attributes = Attributes(self.rawattributes, database=None)

        # Assert
        self.assertEqual(expected, len(attributes.attributes))
        for attribute in attributes.attributes:
            self.assertNotEqual('', attribute.name)
            self.assertNotEqual('', attribute.initial)
            self.assertIsInstance(attribute.weight, numbers.Number)
            self.assertIsInstance(attribute.enabled, bool)
            self.assertIsInstance(attribute.essential, bool)
            self.assertIsInstance(attribute.persist, bool)
            self.assertIsInstance(attribute.dependencies, list)
            self.assertIsInstance(attribute.options, dict)
            self.assertIsInstance(attribute.reference, types.ModuleType)

    def test_pickling(self):
        # Arrange
        attributes = Attributes(self.rawattributes, database=None)
        expected = len(attributes.attributes)

        # Act
        pickled = pickle.dumps(attributes)
        unpickled = pickle.loads(pickled)

        # Assert
        self.assertIsInstance(unpickled, Attributes)
        self.assertEqual(expected, len(unpickled.attributes))
        for attribute in unpickled.attributes:
            self.assertNotEqual('', attribute.name)
            self.assertNotEqual('', attribute.initial)
            self.assertIsInstance(attribute.weight, numbers.Number)
            self.assertIsInstance(attribute.enabled, bool)
            self.assertIsInstance(attribute.essential, bool)
            self.assertIsInstance(attribute.persist, bool)
            self.assertIsInstance(attribute.dependencies, list)
            self.assertIsInstance(attribute.options, dict)
            self.assertIsInstance(attribute.reference, types.ModuleType)

    def test_keystring(self):
        # Arrange
        keystring = 'DuAlIcH'

        # Act
        attributes = Attributes(
            self.rawattributes, database=None, keystring=keystring
        )

        # Assert
        for attribute in attributes.attributes:
            index = str.find(keystring.lower(), attribute.initial)
            if index == -1:
                self.assertFalse(attribute.enabled)
            else:
                self.assertTrue(attribute.enabled)
                if keystring[index].isupper():
                    self.assertTrue(attribute.persist)
                else:
                    self.assertFalse(attribute.persist)

    def test_init_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            # Arrange
            project_id = 788
            repository_path = os.path.join(directory, str(project_id))
            expected = os.path.join(
                directory, str(project_id), 'FFmpeg-FFmpeg-'
            )

            # Act
            attributes = Attributes(
                self.rawattributes, database=Database(self.rawsettings)
            )
            try:
                attributes.database.connect()
                actual = attributes._init_repository(
                    project_id, repository_path
                )

                # Assert
                self.assertTrue(len(os.listdir(repository_path)) > 0)
                self.assertTrue(expected in actual)
            finally:
                attributes.database.disconnect()