import QtQuick 6.0
import QtQuick.Controls.Basic 6.0
import QtQuick.Layouts 6.0
import io.portmod 1.0

ColumnLayout {
    property int selectedRow: 0
    clip: true

    HorizontalHeaderView {
        id: installedPackagesHeader
        syncView: installedPackagesTableView
        implicitHeight: 40
        delegate: ItemDelegate {
            text: model.display
            onClicked: installedPackagesModel.toggleSort(index)

            background: Rectangle {
                implicitWidth: 100
                implicitHeight: 40
                color: down ? "#dddedf" : "#eeeeee"
            }
        }

        Layout.fillWidth: true
    }

    TableView {
        id: installedPackagesTableView

        focus: true
        columnSpacing: 1
        rowSpacing: 1
        clip: true
        model: installedPackagesModel
        columnWidthProvider: function () {
            // TODO: Force columns to be wider if they reach a minimum size
            // TODO: Implement column resizing

            // -1 accounts for columnSpacing = 1
            return parent.width / installedPackagesTableView.model.columnCount() - 1;
        }
        onWidthChanged: installedPackagesTableView.forceLayout()
        delegate: ItemDelegate {
            highlighted: row == selectedRow
            onClicked: selectedRow = row
            text: model.display
        }

        Layout.fillWidth: true
        Layout.fillHeight: true

        ScrollBar.vertical: ScrollBar {
            id: installedPackagesTableVerticalScrollBar
        }

        ScrollBar.horizontal: ScrollBar {
            id: installedPackagesTableHorizontalScrollBar
        }


        Keys.onUpPressed: function () {
            if (selectedRow != 0) {
                selectedRow -= 1;
            }

            // Moves scrollbar up if the selectedRow is going to be invisible
            if (selectedRow == topRow) {
                installedPackagesTableVerticalScrollBar.decrease();
            }
        }

        Keys.onDownPressed: function () {
            if (selectedRow != installedPackagesModel.rowCount() - 1) {
                selectedRow += 1;

                // Moves scrollbar down if the selectedRow is going to be invisible
                if (selectedRow == bottomRow) {
                    installedPackagesTableVerticalScrollBar.increase();
                }
            }
        }
    }
}
