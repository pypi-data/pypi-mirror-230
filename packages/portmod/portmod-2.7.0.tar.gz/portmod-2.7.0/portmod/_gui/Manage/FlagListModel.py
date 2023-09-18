from typing import Any, Dict, Tuple, Union

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)


class FlagListModel(QAbstractListModel):
    def __init__(self, use_flags: Dict[str, Tuple[bool, str]]):
        super().__init__()

        self._data = use_flags

    def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex]) -> int:  # type: ignore
        return len(self._data)

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:  # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            return list(self._data.keys())[index.row()]
        elif role == Qt.ItemDataRole.CheckStateRole:
            state = list(self._data.values())[index.row()][0]
            if state:
                return Qt.CheckState.Checked
            else:
                return Qt.CheckState.Unchecked
        elif role == Qt.ItemDataRole.UserRole:
            return list(self._data.values())[index.row()][1]

    def roleNames(self) -> Dict[int, QByteArray]:
        result: Dict[int, Any] = super().roleNames()
        result[Qt.ItemDataRole.CheckStateRole] = QByteArray(b"checkState")
        result[Qt.ItemDataRole.UserRole] = QByteArray(b"description")
        return result
