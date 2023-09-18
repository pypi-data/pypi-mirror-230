from PySide6.QtCore import QObject, Slot

from portmodlib.l10n import l10n


class L10n(QObject):
    def __init__(self) -> None:
        super().__init__()

    @Slot(str, result=str)  # type: ignore
    def tr(self, msg_id: str) -> str:
        return l10n(msg_id)
