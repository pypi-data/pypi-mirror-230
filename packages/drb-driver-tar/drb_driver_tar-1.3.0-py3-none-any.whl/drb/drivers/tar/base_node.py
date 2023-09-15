import io
import tarfile
from typing import Any, Dict, Tuple, Optional

from drb.core.node import DrbNode
from drb.core.factory import DrbFactory
from drb.core.path import ParsedPath
from drb.exceptions.tar import DrbTarNodeException
from .node import DrbTarNode
from pathlib import Path


class DrbBaseTarNode(DrbTarNode):
    """
    This node is used to open a tar container, and browse his content.

    Parameters:
        base_node (DrbNode): The base node.
    """
    def __init__(self, base_node: DrbNode):
        super().__init__(parent=base_node.parent, tar_info=None)
        self.base_node = base_node
        self.name = self.base_node.name
        self.namespace_uri = self.base_node.namespace_uri
        self.parent = self.base_node.parent
        self.value = self.base_node.value
        self._all_members = None
        self._tar_file = None
        self._tar_file_source = None
        for name, namespace in self.base_node.attribute_names():
            self @= (name, namespace, self.base_node @ (name, namespace))

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    @property
    def path(self) -> ParsedPath:
        """
        Returns the path of the base node.

        Returns:
            ParsedPath: the full path of the base node
        """
        return self.base_node.path

    def name_entry(self):
        return ''

    @property
    def tar_file(self) -> tarfile.TarFile:
        if self._tar_file is None:
            try:

                if self.base_node.has_impl(io.BufferedIOBase):
                    self._tar_file_source = self.base_node \
                        .get_impl(io.BufferedIOBase)
                    # If the impl is not seekable
                    # it creates a ByteIO with the entire buff
                    if not self._tar_file_source.seekable():
                        self._tar_file_source = io.BytesIO(
                            self._tar_file_source.read())
                    self._tar_file = tarfile.TarFile(fileobj=self
                                                     ._tar_file_source)
                else:
                    raise DrbTarNodeException(
                        f'Unsupported base_node'
                        f' {type(self.base_node).__name__} '
                        f'for DrbFileTarNode')
            except Exception as e:
                raise DrbTarNodeException(f'Unable to read tar file'
                                          f' {self.name} ') from e

        return self._tar_file

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type, **kwargs) -> Any:
        return self.base_node.get_impl(impl)

    def get_members(self):
        if self._all_members is None:
            self._all_members = self.tar_file.getmembers()
        return self._all_members

    def _is_a_child(self, filename):

        # chek if this entries is a child or a sub child if yes => not a child
        # of the root
        if any(filename.startswith(name_entry) and filename != name_entry
               for name_entry in self.tar_file.getnames()):
            return False

        paths_array = Path(filename).parts

        if len(paths_array) == 1 or (len(paths_array) == 2
                                     and paths_array[0] == '/'):
            return True

        return False

    def _add_sub_child(self):

        for entry in self.get_members():
            filename = entry.name
            # chek if this entries is a child or a sub child
            # if yes => not a child
            # of the root
            if any(filename.startswith(name_entry) and filename != name_entry
                   for name_entry in self.tar_file.getnames()):
                return False

            paths_array = Path(filename).parts

            if len(paths_array) == 1 or (
                    len(paths_array) == 2 and
                    Path(paths_array[0]).as_posix() == '/'):
                continue

            if Path(paths_array[0]).as_posix() == '/':
                name_sub_dir = paths_array[1]
            else:
                name_sub_dir = paths_array[0]

            found = False
            for child in self._children:
                if child.name == name_sub_dir:
                    found = True
            if not found:
                self._children.append(DrbTarNode(self, None,
                                                 name=name_sub_dir,
                                                 dir=True))

    def open_member(self, tar_info: tarfile.TarInfo):
        # open a member of the tar en return an BufferedIOBase impl
        return self._tar_file.extractfile(tar_info)

    def close(self):
        if self._tar_file_source is not None:
            self._tar_file_source.close()
        if self._tar_file is not None:
            self._tar_file.close()
        self.base_node.close()


class DrbTarFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbTarNode):
            return node
        return DrbBaseTarNode(base_node=node)
