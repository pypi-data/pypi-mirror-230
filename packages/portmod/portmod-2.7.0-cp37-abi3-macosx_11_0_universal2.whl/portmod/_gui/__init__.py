import logging
import sys

from portmodlib.l10n import l10n

try:
    import PySide6  # noqa: F401
except ModuleNotFoundError as error:
    if error.name == "PySide6":
        logging.error(l10n("pyside6-not-found-error"))
        sys.exit(-1)
    else:
        raise error


import signal
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance

from portmod._gui.config import Config
from portmod._gui.l10n import L10n
from portmod._gui.Manage.InstalledPackagesModel import InstalledPackagesProxyModel
from portmod._gui.packages import get_installed_packages
from portmod._gui.Search.SearchPackagesModel import SearchedPackagesModel


def main() -> None:
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Setup the application engine
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Pass Python objects to QML application
    config = Config()
    qmlRegisterSingletonInstance(Config, "io.portmod", 1, 0, "Config", config)  # type: ignore

    l10n = L10n()
    qmlRegisterSingletonInstance(Config, "io.portmod", 1, 0, "L10n", l10n)  # type: ignore

    installedPackagesModel = InstalledPackagesProxyModel(get_installed_packages())
    engine.rootContext().setContextProperty(
        "installedPackagesModel", installedPackagesModel
    )

    searchPackagesModel = SearchedPackagesModel()
    engine.rootContext().setContextProperty("searchPackagesModel", searchPackagesModel)

    # Load the QML file
    qml_file = Path(__file__).parent / "main.qml"
    engine.load(qml_file)

    # Start the app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
