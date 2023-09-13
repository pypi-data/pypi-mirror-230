import os
import unittest
import drb.topics.resolver as resolver
from pathlib import Path
from drb.drivers.file import DrbFileFactory
from drb.exceptions.core import DrbException
from drb.drivers.zip import DrbZipFactory
from drb.drivers.zip.zip import DrbZipAttributeNames

MY_DATA1_TXT = "mydata1.txt"
MY_DATA2_TXT = "mydata2.txt"
EMPTY_DIR = "empty_dir"
ROOT_DIR_DATA = "data"
MY_DATA_TXT = "mydata.txt"
SENTINEL_1_ROOT = "sentinel-1"


class TestDrbZip(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    zip_ok1 = current_path / "files" / "data-ok.zip"
    zip_ko1 = current_path / "files" / "data-nok.zip"

    zip_ok2 = current_path / "files" / "data-ok2.zip"
    zip_ko2 = current_path / "files" / "data-nok2.zip"
    zip_s1 = current_path / "files" / "sentinel-1.zip"
    zip_confused_names = current_path / "files" / "data-name-confused.zip"
    not_zip_files = current_path / "files" / "mydata.txt"

    zip_fake = current_path / "files" / "fake.zip"

    node = None
    node_file = None

    def setUp(self) -> None:
        self.node = None
        self.node_file = None

    def tearDown(self) -> None:
        if self.node is not None:
            self.node.close()
        if self.node_file is not None:
            self.node_file.close()

    def open_node(self, path_file):
        self.node_file = DrbFileFactory().create(path_file)
        self.node = DrbZipFactory().create(self.node_file)
        return self.node

    def test_opened__file_node(self):
        node = self.open_node(str(self.zip_ok1))
        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 0])

    def test_fake(self):
        node = self.open_node(str(self.zip_fake))

        self.assertEqual(node.name, "fake.zip")

        with self.assertRaises(DrbException):
            len(node)

    def test_open_URL_ok1(self):
        node = self.open_node(str(self.zip_ok1))
        self.assertIsNotNone(node[ROOT_DIR_DATA, None, 0])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]
        self.assertIsNotNone(node[ROOT_DIR_DATA]
                             [MY_DATA_TXT])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][ROOT_DIR_DATA]
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][EMPTY_DIR]

        self.assertEqual(len(node), 1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA]),
            1)

    def test_open_URL_ko1(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertEqual(len(node), 1)

        self.assertIsNotNone(node[ROOT_DIR_DATA])
        with self.assertRaises(KeyError):
            node[MY_DATA_TXT]
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][ROOT_DIR_DATA]
        self.assertIsNotNone(node[ROOT_DIR_DATA]
                             [MY_DATA_TXT])

    def test_open_URL_ok2(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertIsNotNone(node[ROOT_DIR_DATA])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]
        self.assertIsNotNone(
            node[ROOT_DIR_DATA][MY_DATA_TXT])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][ROOT_DIR_DATA]

        self.assertIsNotNone(node[ROOT_DIR_DATA][EMPTY_DIR])
        self.assertIsNotNone(node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR, None, 2]

        self.assertEqual(len(node), 1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA]),
            2)
        self.assertEqual(
            len(node[ROOT_DIR_DATA][EMPTY_DIR]),
            1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA][MY_DATA_TXT]),
            0)

        self.assertEqual(
            len(node[ROOT_DIR_DATA][EMPTY_DIR][
                    EMPTY_DIR]),
            2)
        self.assertEqual(
            len(node[ROOT_DIR_DATA][EMPTY_DIR][
                    EMPTY_DIR]),
            2)
        self.assertIsNotNone(
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR][MY_DATA1_TXT])
        self.assertIsNotNone(
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR][MY_DATA2_TXT])

    def test_open_URL_ko2(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertIsNotNone(node[ROOT_DIR_DATA])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]
        self.assertIsNotNone(
            node[ROOT_DIR_DATA][MY_DATA_TXT])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][ROOT_DIR_DATA]

        self.assertIsNotNone(
            node[ROOT_DIR_DATA][EMPTY_DIR])
        self.assertIsNotNone(
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR, None, 2]

        self.assertEqual(len(node), 1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA]),
            2)
        self.assertEqual(
            len(node[ROOT_DIR_DATA][EMPTY_DIR]),
            1)
        self.assertEqual(
            len(node[ROOT_DIR_DATA][MY_DATA_TXT]),
            0)

        self.assertEqual(
            len(node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR]),
            2)
        self.assertIsNotNone(
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR][MY_DATA1_TXT])
        self.assertIsNotNone(
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR][MY_DATA2_TXT])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA][EMPTY_DIR][EMPTY_DIR]["mydata3.txt"]

    def test_first_end_child(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertEqual(len(node), 1)
        self.assertIsNotNone(node[0])

        self.assertEqual(node[0].name, ROOT_DIR_DATA)
        self.assertEqual(node[-1].name, ROOT_DIR_DATA)

        self.assertEqual(node[0][0].name, EMPTY_DIR)
        self.assertEqual(node[0][-1].name, MY_DATA_TXT)

        with self.assertRaises(IndexError):
            node[0][-1][0]
        with self.assertRaises(IndexError):
            node[0][-1][-1]

        self.assertEqual(node[0][EMPTY_DIR][0].name,
                         EMPTY_DIR)
        self.assertEqual(node[0][EMPTY_DIR][-1].name,
                         EMPTY_DIR)

        self.assertEqual(node[0][0][-1][0].name, MY_DATA1_TXT)
        self.assertEqual(node[0][0][-1][-1].name, MY_DATA2_TXT)

    def test_get_named_child_without_occurrence(self):
        node = self.open_node(str(self.zip_ok2))

        occurrence = node[ROOT_DIR_DATA][EMPTY_DIR]
        self.assertEqual(occurrence.name, EMPTY_DIR)

    def test_has_child(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child(EMPTY_DIR))
        self.assertFalse(node[0].has_child('nono'))

        self.assertTrue(node[0].has_child())
        self.assertTrue(
            node[0][EMPTY_DIR].has_child())
        self.assertTrue(
            node[0][EMPTY_DIR]
            [EMPTY_DIR].has_child())
        self.assertFalse(
            node[0][0][-1]
            [-1].has_child())

    def test_get_child_at(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child())

        self.assertEqual(node[0][0].name, EMPTY_DIR)
        self.assertEqual(node[0][0][0][0].name, MY_DATA1_TXT)
        self.assertEqual(node[0][0][0][1].name, MY_DATA2_TXT)
        with self.assertRaises(IndexError):
            node[0][0][0][3]

        self.assertEqual(node[0][0][0]
                         [-1].name, MY_DATA2_TXT)

    def test_namespace_uri(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child())
        self.assertIsNone(node[0].namespace_uri)

    def test_value_uri(self):
        node = self.open_node(str(self.zip_ok2))

        self.assertTrue(node[0].has_child())
        self.assertIsNone(node[0].value)

    def test_test_namespace_uri_file(self):
        node = self.open_node(str(self.zip_ok1))

        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)
        self.assertEqual(node.name, self.node_file.name)

    def test_value_file(self):
        node = self.open_node(str(self.zip_ok1))

        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)
        self.assertEqual(node.value, self.node_file.value)

    def test_attributes_zip_files(self):
        node = self.open_node(str(self.zip_s1))

        list_attributes = node.attributes.keys()
        self.assertIn(('mode', None), list_attributes)
        self.assertIn(('size', None), list_attributes)
        self.assertEqual(node.get_attribute('mode'), 'REGULAR')

    def test_attributes(self):
        node = self.open_node(str(self.zip_s1))

        self.assertIsNotNone(node[SENTINEL_1_ROOT].attributes)
        list_attributes = node[SENTINEL_1_ROOT].attributes
        self.assertIn((DrbZipAttributeNames.DIRECTORY.value, None),
                      list_attributes.keys())
        self.assertEqual(list_attributes[(DrbZipAttributeNames.DIRECTORY.value,
                                          None)], True)

        with self.assertRaises(KeyError):
            list_attributes[(DrbZipAttributeNames.DIRECTORY.value, 'toto')]

    def test_get_attribute(self):
        node = self.open_node(str(self.zip_s1))

        self.assertIsNotNone(node[SENTINEL_1_ROOT] @ 'directory')
        self.assertEqual(True, node[SENTINEL_1_ROOT] @ 'directory')

        child = node[SENTINEL_1_ROOT]["manifest.safe"]
        self.assertEqual(False, child @ 'directory')
        self.assertEqual(False, child.get_attribute('directory'))
        self.assertEqual(14945, child @ 'size')
        self.assertEqual(14945, child.get_attribute('size'))
        self.assertAlmostEqual(4.9, child @ 'ratio', delta=0.1)
        self.assertAlmostEqual(4.9, child.get_attribute('ratio'), delta=0.1)
        self.assertAlmostEqual(3014, child @ 'packed', delta=10)
        self.assertAlmostEqual(3014, child.get_attribute('packed'), delta=10)

        child = node[SENTINEL_1_ROOT]["measurement"]
        self.assertEqual(0, child @ 'size', 0)
        self.assertEqual(0, child.get_attribute('size'), 0)
        self.assertEqual(0, child @ 'ratio', 0)
        self.assertEqual(0, child.get_attribute('ratio'), 0)
        self.assertEqual(0, child @ 'packed', 0)
        self.assertEqual(0, child.get_attribute('packed'), 0)

    def test_open_name_confused(self):
        node = self.open_node(str(self.zip_confused_names))

        self.assertIsNotNone(node[ROOT_DIR_DATA])
        with self.assertRaises(KeyError):
            node[ROOT_DIR_DATA, None, 2]

        first_node = node[ROOT_DIR_DATA]
        self.assertEqual(len(first_node), 6)

        node_file = first_node[MY_DATA_TXT]
        self.assertFalse(node_file.has_child())
        self.assertEqual(len(node_file), 0)

        node_dir = first_node["mydata"]
        self.assertEqual(len(node_dir), 2)
        self.assertTrue(node_dir.has_child())

        node_dir = first_node["myd"]
        self.assertEqual(len(node_dir), 1)
        self.assertTrue(node_dir.has_child())

        node_dir = first_node["mydata_empty"]
        self.assertEqual(len(node_dir), 0)
        self.assertFalse(node_dir.has_child())

        node_file = first_node["my"]
        self.assertFalse(node_file.has_child())
        self.assertEqual(len(node_file), 0)

        node_file = first_node["mydata_txt"]
        self.assertFalse(node_file.has_child())
        self.assertEqual(len(node_file), 0)
        self.assertEqual(node_file.name, "mydata_txt")

    def test_parent(self):
        first_node = self.open_node(str(self.zip_ok2))

        self.assertEqual(first_node.parent, self.node_file.parent)
        self.assertEqual(first_node.value, self.node_file.value)

        first_child = first_node[0]
        self.assertEqual(first_child.parent, first_node)

    def test_path(self):
        first_node = self.open_node(str(self.zip_ok2))

        self.assertEqual(Path(first_node.path.name).as_posix(),
                         Path(self.zip_ok2).as_posix())

        first_child = first_node[0]
        path_child = Path(self.zip_ok2).joinpath(first_child.name).as_posix()
        self.assertEqual(str(first_child.path.name), path_child)

    def test_setitem(self):
        with self.assertRaises(NotImplementedError):
            parent = self.open_node(str(self.zip_s1))
            child = resolver.create(str(self.not_zip_files.absolute()))
            parent[None] = child

    def test_delitem(self):
        with self.assertRaises(NotImplementedError):
            node = self.open_node(str(self.zip_s1))[SENTINEL_1_ROOT]
            del node['manifest.safe']
