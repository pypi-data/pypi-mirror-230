import io
from pathlib import Path
from typing import Any, List, Optional

import affine
import numpy
import pandas
import rasterio
import copy
from deprecated.classic import deprecated
from drb.core import DrbFactory, DrbNode, ParsedPath
from drb.exceptions.core import DrbException
from drb.nodes.abstract_node import AbstractNode
from rasterio import MemoryFile
from rasterio.crs import CRS


class DrbLitto3dNode(AbstractNode):
    """
    This node is used to instantiate a DrbLitto3dNode from another
    implementation of drb such as file.


    Parameters:
        base_node (DrbNode): the base node of this node.
    """

    def __init__(self, base_node: DrbNode):
        super().__init__()

        self.base_node = base_node
        self._format = None
        suffix = Path(self.base_node.name).suffix
        self._impl_mng = copy.copy(base_node._impl_mng)
        if suffix == ".asc":
            self._format = "asc"
            self.add_impl(numpy.ndarray, self._to_numpy_ndarray)
            self.add_impl(rasterio.DatasetReader, self._to_rasterio_dataset)
        if suffix == ".xyz":
            self._format = "xyz"
            self.add_impl(pandas.DataFrame, self._to_panda_dataframe)

        self.__init_attributes()

    def __init_attributes(self):
        if self._format == "asc":
            io_stream = self._get_base_node_stream()
            header = [io_stream.readline() for i in range(6)]
            values = [
                float(h.decode().split(" ")[-1].strip()) for h in header
            ]
            io_stream.close()
            cols, rows, lx, ly, cell, nd = values
            self @= ("cols",  cols)
            self @= ("rows",  rows)
            self @= ("lx",  lx)
            self @= ("ly",  ly)
            self @= ("cell",  cell)
            self @= ("NODATA",  nd)
        else:
            self @= ("cols",  0)
            self @= ("rows",  0)
            self @= ("lx",  0)
            self @= ("ly",  0)
            self @= ("cell",  0)
            self @= ("NODATA",  0)

        for e in self.base_node.attribute_names():
            attr = self.base_node @ e[0]
            self @= (e[0], attr)

    def _get_base_node_stream(self):
        if self.base_node.has_impl(io.BufferedIOBase):
            return self.base_node.get_impl(io.BufferedIOBase)
        else:
            raise DrbException(
                "Unsupported parent "
                f"{type(self.base_node).__name__}"
                " for DrbLitto3dNode"
            )

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        """
        This node as no children.

        Returns:
            List: An empty List
        """
        return []

    @staticmethod
    def _to_numpy_ndarray(node: DrbNode, **kwargs) -> numpy.ndarray:
        if isinstance(node, DrbLitto3dNode):
            with node._get_base_node_stream() as io_stream:
                return numpy.loadtxt(io_stream, skiprows=6)
        raise TypeError(f'Invalid node type: {type(node)}')

    @staticmethod
    def _to_rasterio_dataset(node: DrbNode, **kwargs) \
            -> rasterio.DatasetReader:
        if isinstance(node, DrbLitto3dNode):
            return node._get_dataset()
        raise TypeError(f'Invalid node type: {type(node)}')

    @staticmethod
    def _to_panda_dataframe(node: DrbNode, **kwargs) -> pandas.DataFrame:
        if isinstance(node, DrbLitto3dNode):
            with node._get_base_node_stream() as io_stream:
                return pandas.read_table(
                    io_stream,
                    delim_whitespace=True,
                    names=["x", "y", "z", "a", "b", "c"],
                    usecols=["x", "y", "z"],
                )
        raise TypeError(f'Invalid node type: {type(node)}')

    def _get_dataset(self):
        io_stream = self._get_base_node_stream()
        header = [io_stream.readline() for i in range(6)]
        values = [float(h.decode().split(" ")[-1].strip()) for h in header]
        width, height, left, bottom, resolution, nodata = values
        crs = CRS.from_epsg(2154)  # CRS of Litto3D is Lambert93 : epsg 2154
        data = numpy.loadtxt(io_stream)
        io_stream.close()
        # add axis to have a shape like (band, row, col)
        data = data[numpy.newaxis, :]
        top = float(bottom) + float(height) * float(resolution)
        # create transform / affine
        transform = affine.Affine(
            float(resolution),
            0.0,
            float(left),
            0.0,
            -float(resolution),
            float(top),
        )

        profile = {
            "height": height,
            "width": width,
            "transform": transform,
            "count": 1,
            "driver": "GTiff",
            "nodata": nodata,
            "crs": crs,
            "dtype": "float64",
        }

        with MemoryFile() as memfile:
            with memfile.open(**profile) as dataset:
                dataset.write(data)
            return (
                memfile.open()
            )  # reopen with data to have a datasetReader object

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbLitto3dFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbLitto3dNode):
            return node
        return DrbLitto3dNode(base_node=node)
