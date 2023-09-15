from deprecated import deprecated
from pathlib import Path
from tarfile import ExFileObject, TarInfo, DIRTYPE
from typing import Any, List
from drb.core.node import DrbNode
from drb.nodes.abstract_node import AbstractNode
from drb.exceptions.core import DrbNotImplementationException
import os
import datetime
import enum
import drb.topics.resolver as resolver


class DrbTarAttributeNames(enum.Enum):
    SIZE = 'size'
    """
    The size of the file in bytes.
    """
    DIRECTORY = 'directory'
    """
    A boolean that tell if the file is a directory.
    """
    MODIFIED = 'modified'
    """
    The last modification date of the file with this format:
        [DAY MONTH NUMB HH:MM:SS YEAR].
    """


class DrbTarNode(AbstractNode):
    """
    This node is used to browse the content of a zip container.

    Parameters:
        parent (DrbNode): The zip container.
        tar_info (ZipInfo): Class with attributes describing
                            each file in the ZIP archive.

    """

    def __init__(self, parent: DrbNode, tar_info: TarInfo = None,
                 name=None, dir=False):
        super().__init__()
        self._tar_info = tar_info
        self.name = name if tar_info is None \
            else self.__init_name(name, tar_info)
        self.parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._dir = dir if tar_info is None else tar_info.type == DIRTYPE
        self.__init_attributes()
        if not self @ DrbTarAttributeNames.DIRECTORY.value:
            self.add_impl(ExFileObject, _to_stream)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, item):
        raise NotImplementedError

    def __init_attributes(self):
        name_attribute = DrbTarAttributeNames.DIRECTORY.value
        self @= (name_attribute, None, self._dir)

        if self._tar_info is not None:
            name_attribute = DrbTarAttributeNames.SIZE.value
            self @= (name_attribute, None, self._tar_info.size)

            date_time = datetime.datetime.fromtimestamp(self._tar_info.mtime)
            name_attribute = DrbTarAttributeNames.MODIFIED.value
            self @= (name_attribute, None, date_time.strftime("%c"))

    @staticmethod
    def __init_name(name: str, tar_info: TarInfo) -> str:
        n = name
        if tar_info is not None:
            if tar_info.name.endswith('/'):
                n = tar_info.name[:-1]
            else:
                n = tar_info.name
            if '/' in n:
                return n[n.rindex('/') + 1:]
        return n

    def name_entry(self):
        if self._tar_info is not None:
            return self._tar_info.name
        else:
            name_entry = self.parent.name_entry() + self.name
            if self._dir:
                name_entry += '/'
            return name_entry

    @staticmethod
    def is_a_subdir(entry) -> bool:
        if os.path.basename(entry.name) is not None and len(
                os.path.basename(entry.name)) > 1:
            return False

        paths_array = Path(entry.name).parts

        if len(paths_array) > 1:
            return False
        return True

    def _add_sub_child(self):

        name = self.name_entry()
        for entry in self.get_members():
            filename = entry.name[len(name):]

            # Chek if this entries is a child or a sub
            # child if yes => not a child
            # of the root
            # if os.path.basename(entry.name) is not None and len(
            #         os.path.basename(entry.name)) > 1:
            #         continue

            if filename.startswith('/'):
                filename = filename[1:]

            paths_array = Path(filename).parts

            if len(paths_array) == 1:
                continue

            name_sub_dir = paths_array[0]

            found = False
            for child in self._children:
                if child.name == name_sub_dir:
                    found = True
            if not found:
                self._children.append(DrbTarNode(self, None,
                                                 name=name_sub_dir, dir=True))

    def get_members(self):
        if not self._dir:
            return []

        members = []

        name = self.name_entry()
        if name.startswith('/'):
            name = name[1:]
        for entry in self.parent.get_members():
            entry_name = entry.name
            if entry_name.startswith('/'):
                entry_name = entry_name[1:]
            if not entry_name.startswith(name):
                continue

            filename = entry_name[len(name):]
            if not filename:
                continue

            members.append(entry)
        return members

    def _is_a_child(self, filename):
        name = self.name_entry()
        filename = filename[len(name):]

        if not filename.startswith('/') and \
                not name.endswith('/'):
            return False

        filename = filename[1:]
        if filename.endswith('/'):
            filename = filename[:-1]

        paths_array = Path(filename).parts

        if len(paths_array) > 1:
            return False

        if os.path.basename(filename) is not None \
                and len(os.path.basename(filename)) > 0:
            return True

        # Either the name do not contains sep either only one a last position
        return '/' not in filename

    @property
    @resolver.resolve_children
    @deprecated(version='2.1.0')
    def children(self) -> List[DrbNode]:

        if self._children is None:
            self._children = []

            for entry in self.get_members():
                if self._is_a_child(entry.name):
                    self._children.append(DrbTarNode(self, entry))
                elif self.is_a_subdir(entry):
                    self._children.append(DrbTarNode(self,
                                                     None, name=entry.name))

            self._add_sub_child()

            self._children = sorted(self._children,
                                    key=lambda entry_cmp: entry_cmp.name)

        return self._children

    def open_member(self, tar_info: TarInfo):
        # open a member to retrieve tje implementation
        # back to first parent that is file tar to open it...
        return self.parent.open_member(tar_info)


def _to_stream(node: DrbTarNode, **kwargs):
    return node.parent.open_member(node._tar_info)
