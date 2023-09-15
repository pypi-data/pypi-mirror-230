import io
import os
import unittest
from pathlib import Path

import numpy
import pandas
import rasterio
from drb.drivers.file import DrbFileFactory
from drb.drivers.litto3d import DrbLitto3dFactory, DrbLitto3dNode

GROUP_NOT_EXIST = "fake_group"


class TestDrbNodeFactorylitto3d(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    asc_file = current_path / "files" / "test_asc.asc"
    xyz_file = current_path / "files" / "test_xyz.xyz"
    litto3d_fake = current_path / "files" / "fake.litto3d"

    def open_node(self, path_file):
        self.node_file = DrbFileFactory().create(path_file)
        self.node = DrbLitto3dFactory().create(self.node_file)
        return self.node

    def test_opened_file_node(self):
        node = self.open_node(str(self.asc_file))

        self.assertIsInstance(node, DrbLitto3dNode)
        self.assertEqual(node.name, self.node_file.name)
        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)

    def test_base_node(self):
        node = self.open_node(str(self.asc_file))

        self.assertEqual(node.parent, self.node_file.parent)
        self.assertEqual(node.value, self.node_file.value)

        self.assertIsInstance(node, DrbLitto3dNode)

        self.assertFalse(node.has_child())

    def test_base_node_get_child(self):
        node = self.open_node(str(self.asc_file))

        self.assertEqual(len(node.children), 0)

    def test_base_node_attribute(self):
        node = self.open_node(str(self.asc_file))

        for key in self.node_file.attributes.keys():
            self.assertEqual(
                node.get_attribute(key[0]),
                self.node_file.get_attribute(key[0]),
            )

        self.assertTrue(("cols", None) in node.attributes.keys())
        self.assertTrue(("rows", None) in node.attributes.keys())
        self.assertTrue(("lx", None) in node.attributes.keys())
        self.assertTrue(("ly", None) in node.attributes.keys())
        self.assertTrue(("cell", None) in node.attributes.keys())
        self.assertTrue(("NODATA", None) in node.attributes.keys())

        self.assertEqual(node.get_attribute("cols"), 2)
        self.assertEqual(node.get_attribute("rows"), 2)
        self.assertEqual(node.get_attribute("lx"), 955000.000)
        self.assertEqual(node.get_attribute("ly"), 6225005.000)
        self.assertEqual(node.get_attribute("cell"), 5)
        self.assertEqual(node.get_attribute("NODATA"), -99999)

        self.assertEqual(node @ "cols", 2)
        self.assertEqual(node @ "rows", 2)
        self.assertEqual(node @ "lx", 955000.000)
        self.assertEqual(node @ "ly", 6225005.000)
        self.assertEqual(node @ "cell", 5)
        self.assertEqual(node @ "NODATA", -99999)

        node = self.open_node(str(self.xyz_file))

        for key in self.node_file.attributes.keys():
            self.assertEqual(
                node.get_attribute(key[0]),
                self.node_file.get_attribute(key[0]),
            )

        self.assertTrue(("cols", None) in node.attributes.keys())
        self.assertTrue(("rows", None) in node.attributes.keys())
        self.assertTrue(("lx", None) in node.attributes.keys())
        self.assertTrue(("ly", None) in node.attributes.keys())
        self.assertTrue(("cell", None) in node.attributes.keys())
        self.assertTrue(("NODATA", None) in node.attributes.keys())

        self.assertEqual(node.get_attribute("cols"), 0)
        self.assertEqual(node.get_attribute("rows"), 0)
        self.assertEqual(node.get_attribute("lx"), 0)
        self.assertEqual(node.get_attribute("ly"), 0)
        self.assertEqual(node.get_attribute("cell"), 0)
        self.assertEqual(node.get_attribute("NODATA"), 0)

    def test_base_node_impl(self):
        node = self.open_node(str(self.asc_file))

        impl_base_file = io.BufferedIOBase

        self.assertTrue(node.has_impl(impl_base_file))

        impl = node.get_impl(impl_base_file)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, impl_base_file)

    def test_node_impl(self):
        node = self.open_node(str(self.asc_file))
        data = numpy.array([[6.470, 6.400], [6.430, -99999]])

        self.assertTrue(node.has_impl(numpy.ndarray))

        impl = node.get_impl(numpy.ndarray)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, numpy.ndarray)
        numpy.testing.assert_array_equal(impl, data)

        self.assertTrue(node.has_impl(rasterio.DatasetReader))

        impl = node.get_impl(rasterio.DatasetReader)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, rasterio.DatasetReader)
        # Compare to the first and only band
        numpy.testing.assert_array_equal(impl.read()[0], data)

        node = self.open_node(str(self.xyz_file))

        self.assertTrue(node.has_impl(pandas.DataFrame))

        impl = node.get_impl(pandas.DataFrame)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, pandas.DataFrame)

    def test_path(self):
        node = self.open_node(str(self.asc_file))
        self.assertEqual(node.path.path, str(self.asc_file).replace('\\', '/'))
