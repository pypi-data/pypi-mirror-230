from __future__ import annotations

from typing import Any
from typing import List
from typing import Optional

import h5py
import natsort
from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt

from egse.bits import beautify_binary
from egse.reg import RegisterMap


def get_type_name(x) -> str:
    """Return a readable representation of the type of the given object."""
    if isinstance(x, h5py.Dataset):
        return "Dataset"
    if isinstance(x, h5py.Group):
        return "Group"
    if isinstance(x, h5py.File):
        return "File"
    return str(type(x))


class TreeItem:
    """
    An item (node or leaf) in a generic tree structure.
    """
    def __init__(self, data: Any, parent: TreeItem = None):
        self._child_items = []
        self._item_data = data
        self._parent_item = parent

    def append_child(self, child: TreeItem):
        """Adds a child HDF5Item to this object."""
        self._child_items.append(child)

    def child(self, row: int) -> Optional[TreeItem]:
        """Returns the child at the given row. If an invalid row is given, None will be returned."""
        if 0 <= row < len(self._child_items):
            return self._child_items[row]
        return None

    def child_index(self, item: TreeItem) -> int:
        """Returns the index (=row) of the child in the list of children."""
        return self._child_items.index(item)

    def child_count(self) -> int:
        """Returns the number of children."""
        return len(self._child_items)

    def last_child(self) -> TreeItem:
        """Returns the last child from the list of children."""
        return self._child_items[-1]

    def column_count(self) -> int:
        """Returns the number of columns for this item."""
        return len(self._item_data)

    def data(self, column: int):
        """
        Returns the data in the given column for this item. If an invalid column is provided,
        None is returned.
        """
        if 0 <= column < len(self._item_data):
            return self._item_data[column]
        return None

    def row(self) -> int:
        """
        Returns the row index of this item in the list of children of its parent. Since the root
        item has no parent, row=0 will be returned.
        """
        if self._parent_item:
            return self._parent_item.child_index(self)
        return 0

    def parent_item(self) -> Optional[TreeItem]:
        """Returns the parent item for this item."""
        return self._parent_item


class HDF5Item(TreeItem):
    """
    An item (node or leaf) in a tree structure representing the HDF5 file. The structure is
    represented by a list of child items for this item and a link to the parent for this item.

    The parent item (HDF5TreeItem) is None for the root item in this linked list. Leaf items have
    no children, i.e. child_count=0.
    """
    def __init__(self, data: Any, parent: TreeItem = None, expandable: bool = False, item = None):
        super().__init__(data, parent)
        self._expandable = expandable
        self._item = item

    @property
    def is_expandable(self):
        return self._expandable

    @property
    def item_name(self):
        return self._item.name

    @property
    def item_type(self):
        return type(self._item)

    @property
    def item_size(self):
        if isinstance(self._item, h5py.Dataset):
            size = self._item.shape
        elif isinstance(self._item, h5py.Group):
            size = len(self._item)
        else:
            size = 0
        return size

    def get_item(self):
        return self._item


class TreeModel(QAbstractItemModel):
    """
    A (more or less) generic tree model.

    Args:
        data: a list of lists

    """
    ExpandableRole = Qt.UserRole + 500

    def __init__(self, data: Any, header_data: List[str], parent: QObject = None):
        super().__init__(parent)
        self._root_item = TreeItem(header_data)
        self.set_model_data(data, self._root_item)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        item: HDF5Item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(index.column())
        if role == TreeModel.ExpandableRole:
            return item.is_expandable
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return super().flags(index)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root_item.data(section)
        return None

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()

        child_item = child.internalPointer()
        parent_item = child_item.parent_item()

        if parent_item is self._root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            row_count = 0
            return row_count

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        row_count = parent_item.child_count()
        return row_count

    def columnCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            col_count = parent.internalPointer().column_count()
        else:
            col_count = self._root_item.column_count()
        return col_count

    def hasChildren(self, index: QModelIndex = QModelIndex(), *args, **kwargs):

        if self.data(index, TreeModel.ExpandableRole):
            has_children = True
        else:
            has_children = super().hasChildren(index)

        return has_children

    def set_model_data(self, data: Any, parent: TreeItem):
        raise NotImplementedError


class HDF5Model(TreeModel):
    def __init__(self, hdf_file: h5py.File, parent: QObject = None):
        self._hdf_file = hdf_file
        self._hdf_root = hdf_file['/']

        # Load the first items from the top level group '/' and pass them to the super class

        data = self.get_model_data(self._hdf_root)

        header_data = ['Datasets', 'Size', 'Type']

        super().__init__(data, header_data, parent)

    def set_model_data(self, data: Any, parent: TreeItem):

        for item_data, expand, item in data:
            parent.append_child(HDF5Item(item_data, parent, expandable=expand, item=item))

    def get_model_data(self, group: h5py.Group):
        data = []

        if len(group) < 2000:
            items = natsort.natsorted(group.items(), key=lambda x: x[0])
        else:
            items = group.items()

        for name, item in items:
            if isinstance(item, h5py.Dataset):
                size = str(item.shape)
                type_name = str(item.dtype)
                expandable = False
            else:
                size = len(item)
                type_name = get_type_name(item)
                expandable = True
            data.append(([name, size, type_name], expandable, item))

        return data

    def update_model_data(self, index: QModelIndex):

        item: HDF5Item = index.internalPointer()

        if isinstance(item, h5py.Dataset):
            return

        if not item.child_count():
            group_name = item.item_name
            group = self._hdf_file[group_name]
            data = self.get_model_data(group)
            self.set_model_data(data, item)
            self.layoutChanged.emit()


def convert_data_for_role(data, role):
    if role == 0:
        return int(data)
    if role == 1:
        return f"0x{data:08X}"
    if role == 2:
        return beautify_binary(data, prefix="0b")

    return data


class RegisterTableModel(QAbstractTableModel):
    def __init__(self, reg_map: RegisterMap):
        super().__init__()

        self.setRegisterMap(reg_map)

        self._col_names = ["Register name", "Parameter name", "Value"]
        self._display_role = dict()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            col = index.column()
            row = index.row()
            if col in (0, 1):
                return self._reg_names[row].split(':')[col]
            if col == 2:
                data = self._reg_data[self._reg_names[row]]
                return convert_data_for_role(data, self._display_role.get(row, 0))

    def setRegisterMap(self, reg_map: RegisterMap):
        self._reg_map = reg_map
        self._reg_data = reg_map.as_dict(flatten=True)
        self._reg_names = list(self._reg_data)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> Any:
        # section is the index of the column/row.
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._col_names[section]

    def toggleDisplayRole(self, index: QModelIndex):
        if index.column() == 2:
            role = self._display_role.get(index.row(), 0) + 1
            self._display_role[index.row()] = role if role < 3 else 0

    def rowCount(self, index):
        return len(self._reg_names)

    def columnCount(self, index):
        return 3
