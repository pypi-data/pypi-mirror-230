import enum
import io
import zipfile
from typing import Any, List, Dict, Optional, Tuple
from zipfile import ZipExtFile, ZipInfo
from deprecated import deprecated

from drb.core import DrbNode, ParsedPath, DrbFactory
from drb.exceptions.core import DrbNotImplementationException
from drb.nodes.abstract_node import AbstractNode
from drb.topics.resolver import resolve_children
from drb.exceptions.zip import DrbZipNodeException


class DrbZipAttributeNames(enum.Enum):
    SIZE = 'size'
    """
    The size of the file in bytes.
    """
    DIRECTORY = 'directory'
    """
    A boolean that tell if the file is a directory.
    """
    RATIO = 'ratio'
    """
    the ratio between the size of the compressed file and the original file.
    """
    PACKED = 'packed'
    """
    The size of the compressed file in bytes.
    """


class DrbZipNode(AbstractNode):
    """
    This node is used to browse the content of a zip container.

    Parameters:
        parent (DrbNode): The zip container.
        zip_info (ZipInfo): Class with attributes describing
                            each file in the ZIP archive.

    """

    def __init__(self, parent: DrbNode, zip_info: ZipInfo):
        super().__init__()
        self._zip_info = zip_info
        if zip_info is not None:
            self.name = self.__retrieve_name(zip_info)
            if not zip_info.is_dir():
                self.add_impl(ZipExtFile, _open_zip_node_entry)
        self.__init_attributes_from_info(zip_info)
        self._parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._path = None

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __init_attributes_from_info(self, info: ZipInfo):
        if info is not None:
            self @= (DrbZipAttributeNames.DIRECTORY.value, info.is_dir())
            self @= DrbZipAttributeNames.SIZE.value, info.file_size
            if info.compress_size > 0:
                ratio = info.file_size / info.compress_size
            else:
                ratio = 0
            self @= (DrbZipAttributeNames.RATIO.value, ratio)
            self @= (DrbZipAttributeNames.PACKED.value, info.compress_size)

    @staticmethod
    def __retrieve_name(zip_info: ZipInfo) -> str:
        if zip_info.filename.endswith('/'):
            name = zip_info.filename[:-1]
        else:
            name = zip_info.filename
        if '/' in name:
            name = name[name.rindex('/') + 1:]
        return name

    def get_file_list(self):
        return self.parent.get_file_list()

    def _is_a_child(self, filename):
        if not filename.startswith(self._zip_info.filename):
            return False

        filename = filename[len(self._zip_info.filename):]

        if not filename:
            return False

        if not filename.startswith('/') and \
                not self._zip_info.filename.endswith('/'):
            return False

        # Either the name do not contains sep either only one a last position
        return '/' not in filename or filename.index('/') == (
                len(filename) - 1)

    @property
    @resolve_children
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = [DrbZipNode(self, entry) for entry in
                              self.get_file_list()
                              if self._is_a_child(entry.filename)]
            self._children = sorted(self._children,
                                    key=lambda entry_cmp: entry_cmp.name)

        return self._children

    def open_entry(self, zip_info: ZipInfo):
        # open the entry on zip file to return ZipExtFile
        # we back to the first node_file to open is
        return self.parent.open_entry(zip_info)


def _open_zip_node_entry(node: DrbZipNode, **kwargs) -> ZipExtFile:
    return node.open_entry(node._zip_info)


class DrbBaseZipNode(DrbZipNode):
    """
    This node is used to open a zip container, and browse his content.

    Parameters:
        base_node (DrbNode): The base node.
    """

    def __init__(self, base_node: DrbNode):
        super().__init__(parent=base_node.parent, zip_info=None)
        self._file_list = None
        self._zip_file = None
        self._zip_file_source = None
        self.base_node = base_node

    @property
    def parent(self) -> Optional[DrbNode]:
        """
        Returns the parent of the base node.

        Returns:
            DrbNode: the parent of the node
        """
        return self.base_node.parent

    @property
    def path(self) -> ParsedPath:
        """
        Returns the path of the base node.

        Returns:
            ParsedPath: the full path of the base node
        """
        return self.base_node.path

    @property
    def name(self) -> str:
        """
        Return the name of the base node.
        This name doesn't contain the path.

        Returns:
            str: the base node name
        """
        return self.base_node.name

    @property
    def value(self) -> Optional[Any]:
        """
        Return the value of the base node.

        Returns:
            Any: the value
        """
        return self.base_node.value

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        """
        Return the attributes of the base node.

        Returns:
            Dict: Key(key_name, key_namespace): value(Any)
        """
        return self.base_node.attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        """
        Return a specific attributes of the base node.

        Parameters:
            name (str): The name of the attribute.
            namespace_uri (str): The namespace_uri of the attribute
                                 (default: None).
        Returns:
            Any: the attribute
        """
        return self.base_node.get_attribute(name, namespace_uri)

    @property
    def zip_file(self) -> zipfile.ZipFile:
        if self._zip_file is None:
            try:
                if self.base_node.has_impl(io.BufferedIOBase):
                    self._zip_file_source = self.base_node \
                        .get_impl(io.BufferedIOBase)
                    self._zip_file = zipfile.ZipFile(self._zip_file_source)
                else:
                    raise DrbZipNodeException(f'Unsupported base_node '
                                              f'{type(self.base_node).name} '
                                              f'for DrbFileZipNode')
            except Exception as e:
                raise DrbZipNodeException(f'Unable to read zip file'
                                          f' {self.name} ') from e
        return self._zip_file

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type, **kwargs) -> Any:
        if self.base_node.has_impl(impl):
            return self.base_node.get_impl(impl)
        raise DrbNotImplementationException

    def impl_capabilities(self) -> List[type]:
        return self.base_node.impl_capabilities()

    def close(self):
        if self._zip_file_source is not None:
            self._zip_file_source.close()
        if self._zip_file is not None:
            self._zip_file.close()
        self.base_node.close()

    def __add_dir_for_path(self, file_info):
        self._file_list.append(file_info)

        if file_info.filename[:-1].find('/') > 0:
            index = file_info.filename[:-1].rindex('/')
            if index > 0:
                path_zip = file_info.filename[:index + 1]
                if path_zip not in self.zip_file.NameToInfo.keys() and \
                        not any(
                            x.filename == path_zip for x in self._file_list):
                    self.__add_dir_for_path(
                        zipfile.ZipInfo(path_zip, file_info.date_time))

    def get_file_list(self):
        if self._file_list is None:
            self._file_list = []
            for fileInfo in self.zip_file.filelist:
                self.__add_dir_for_path(fileInfo)

        return self._file_list

    def _is_a_child(self, filename):
        if '/' not in filename or filename.index('/') == (len(filename) - 1):
            return True
        return False

    def open_entry(self, zip_info: zipfile.ZipInfo):
        # open a entry of the zip en return an BufferedIOBase impl
        return self._zip_file.open(zip_info)


class DrbZipFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbBaseZipNode) or \
                isinstance(node, DrbZipNode):
            return node
        return DrbBaseZipNode(base_node=node)
