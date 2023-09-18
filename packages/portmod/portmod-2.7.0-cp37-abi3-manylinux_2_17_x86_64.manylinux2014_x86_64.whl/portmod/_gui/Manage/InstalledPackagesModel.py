from typing import Any, Dict, List, Union

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
    Slot,
)

from portmod._gui.human_bytes import format_bytes
from portmod._gui.Manage.FlagListModel import FlagListModel
from portmod._gui.packages import get_installed_packages, get_local_flags
from portmod.download import get_total_download_size
from portmod.pybuild import InstalledPybuild
from portmod.query import get_package_metadata
from portmod.repo import get_repo

# TODO: Maybe _data can be a dictionary with InstalledPybuilds as keys, and the flags as values.

# TODO: The logic behind most of these getters should be moved to the real model. Leave the proxy
# model for just sorting and such.


class InstalledPackagesProxyModel(QSortFilterProxyModel):
    flagModels: Dict[str, FlagListModel] = {}
    sortOrders: List[Union[Qt.SortOrder, None]]
    prefixChanged = Signal()

    def __init__(self, data: List[InstalledPybuild]) -> None:
        super().__init__()

        self.sortOrders = [None, None, None, None]
        self.realModel = InstalledPackagesModel(data)
        self.setSourceModel(self.realModel)

    @Slot(int, result=str)  # type: ignore
    def getAtom(self, rowIndex: int) -> str:
        """
        Returns the atom of the given row, and returns it in string form.
        """

        # TODO: Should this be CPN?
        return str(self.get_source_pybuild(rowIndex).CPN)

    @Slot(int, result=str)  # type: ignore
    def get_name(self, rowIndex: int) -> str:
        return self.get_source_pybuild(rowIndex).NAME

    @Slot(int, result=str)  # type: ignore
    def get_author(self, rowIndex: int) -> str:
        pybuild = self.get_source_pybuild(rowIndex)
        atom = pybuild.CPN
        repo = get_repo(pybuild.REPO)
        metadata = get_package_metadata(atom, repo)

        if metadata:
            return ", ".join(metadata.upstream_maintainers)
        else:
            return ""

    @Slot(int, result=str)  # type: ignore
    def get_version(self, rowIndex: int) -> str:
        return str(self.get_source_pybuild(rowIndex).version)

    @Slot(int, result=str)  # type: ignore
    def get_size(self, rowIndex: int) -> str:
        size = get_total_download_size([self.get_source_pybuild(rowIndex)])
        return format_bytes(size)

    @Slot(int, result=str)  # type: ignore
    def get_license(self, rowIndex: int) -> str:
        _license = self.get_source_pybuild(rowIndex).LICENSE
        if _license:
            return _license
        else:
            return "No license"

    @Slot(int, result=str)  # type: ignore
    def get_description(self, rowIndex: int) -> str:
        return self.get_source_pybuild(rowIndex).DESC

    @Slot(int, result=str)  # type: ignore
    def get_homepage(self, rowIndex: int) -> str:
        return self.get_source_pybuild(rowIndex).HOMEPAGE

    @Slot(str, result=FlagListModel)  # type: ignore
    def get_local_flags_model(self, row_index: int) -> FlagListModel:
        atom = self.get_source_pybuild(row_index).CPN
        model = self.flagModels.get(atom)
        if model:
            return model
        else:
            self.flagModels[atom] = FlagListModel(
                get_local_flags(self.get_source_pybuild(row_index))
            )
            return self.flagModels[atom]

    @Slot()
    def changeToCurrentPrefix(self) -> None:
        self.realModel.changeToCurrentPrefix()
        self.prefixChanged.emit()

    def setSortOrder(self, columnIndex: int, sortOrder: Qt.SortOrder) -> None:
        self.sort(columnIndex, sortOrder)
        self.sortOrders[columnIndex] = sortOrder

    @Slot(int)
    def toggleSort(self, columnIndex: int) -> None:
        """
        Toggle between sort orders at the specified column index. If the sort order is ascending,
        change it to descending. If it's descending order not set, change it to ascending.
        """
        # TODO: Add 🢓 or 🢑 to column header based on sort order
        if self.sortOrders[columnIndex] == Qt.SortOrder.AscendingOrder:
            self.setSortOrder(columnIndex, Qt.SortOrder.DescendingOrder)
        elif (
            self.sortOrders[columnIndex] == Qt.SortOrder.DescendingOrder
            or self.sortOrders[columnIndex] is None
        ):
            self.setSortOrder(columnIndex, Qt.SortOrder.AscendingOrder)

    def get_source_pybuild(self, proxy_row_index: int) -> InstalledPybuild:
        source_row_index = self.mapToSource(self.index(int(proxy_row_index), 0)).row()
        pybuild: InstalledPybuild = self.realModel._data[source_row_index]
        return pybuild


class InstalledPackagesModel(QAbstractTableModel):
    def __init__(self, data: List[InstalledPybuild]):
        super(InstalledPackagesModel, self).__init__()
        self._data = data

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: Qt.ItemDataRole) -> Any:  # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            pybuild = self._data[index.row()]
            column_data = [
                pybuild.PN,
                ", ".join(pybuild.get_use()),
                pybuild.CATEGORY,
                str(pybuild.version),
            ]

            return column_data[index.column()]

    def rowCount(self, index: Union[QModelIndex, QPersistentModelIndex]) -> int:  # type: ignore
        return len(self._data)

    def columnCount(self, index: Union[QModelIndex, QPersistentModelIndex]) -> int:  # type: ignore
        return 4

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> str:  # type: ignore
        header_labels = ["Name", "Use Flags", "Category", "Version"]

        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return header_labels[section]

        header_data: str = QAbstractTableModel.headerData(
            self, section, orientation, role
        )
        return header_data

    def changeToCurrentPrefix(self) -> None:
        """
        Repopulates the table with installed packages from the current prefix.
        Used when the prefix is changed while the GUI is still running.
        """
        self.beginRemoveRows(QModelIndex(), 0, len(self._data))
        self._data.clear()
        self.endRemoveRows()

        new_data = get_installed_packages()

        self.beginInsertRows(QModelIndex(), 0, len(new_data) - 1)
        self._data.extend(new_data)
        self.endInsertRows()
