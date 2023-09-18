from typing import Any, List, Union

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Slot,
)

from portmod._gui.packages import search_packages
from portmodlib.atom import QualifiedAtom
from portmodlib.portmod import PackageIndexData


class SearchedPackagesModel(QAbstractListModel):
    def __init__(self) -> None:
        super(SearchedPackagesModel, self).__init__()
        self._data: List[PackageIndexData] = []

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: Qt.ItemDataRole) -> Any:  # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            index_data = self._data[index.row()]
            value = f"{index_data.name}\n\n{index_data.desc}"
            if isinstance(value, QualifiedAtom):
                return str(value)

            return value

    def rowCount(self, index: Union[QModelIndex, QPersistentModelIndex]) -> int:  # type: ignore
        return len(self._data)

    @Slot(str)
    def updateSearchTerm(self, searchTerm: str) -> None:
        self.beginRemoveRows(QModelIndex(), 0, len(self._data))
        self._data.clear()
        self.endRemoveRows()

        new_data = search_packages(searchTerm)

        self.beginInsertRows(QModelIndex(), 0, len(new_data) - 1)
        self._data.extend(new_data)
        self.endInsertRows()

    @Slot(int)
    def getAtom(self, rowIndex: int) -> str:
        index = self.index(rowIndex)
        # The atom is stored in the first index of the list
        atom: str = self._data[index.row()].cpn
        return atom
