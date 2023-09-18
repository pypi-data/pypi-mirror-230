import QtQuick 6.0
import QtQuick.Controls.Basic 6.0
import QtQuick.Layouts 6.0
import io.portmod 1.0

ColumnLayout {
    id: searchTab
    Layout.fillWidth: true

    RowLayout {
        Layout.fillWidth: true

        TextField {
            id: searchField
            placeholderText: L10n.tr("search-text-field-placeholder-text")
            Layout.fillWidth: true

            Keys.onReturnPressed: function () {
                searchPackagesListView.model.updateSearchTerm(text);
                searchPackagesListView.focus = true;
            }
        }

        Button {
            id: searchButton
            text: L10n.tr("search-button-text")
            onClicked: searchPackagesListView.model.updateSearchTerm(searchField.text)

            Layout.fillWidth: true
        }
    }

    ListView {
        id: searchPackagesListView

        property int selectedRow: 0

        model: searchPackagesModel
        clip: true
        // TODO: Have an 'i' icon on each delegate that opens up a details window or popup
        delegate: ItemDelegate {
            highlighted: index == searchPackagesListView.selectedRow
            text: model.display
            onClicked: function () {
                searchPackagesListView.selectedRow = index;
                searchPackagesListView.focus = true;
            }
            onDoubleClicked: searchPackagesModel.getAtom(index)

            width: Window.width
        }

        ScrollBar.vertical: ScrollBar {
            id: searchPackagesTableVerticalScrollBar
        }

        ScrollBar.horizontal: ScrollBar {
            id: searchPackagesTableHorizontalScrollBar
        }

        Layout.fillWidth: true
        Layout.fillHeight: true

        Keys.onUpPressed: function () {
            if (selectedRow != 0) {
                selectedRow -= 1;
            }

            // TODO: Move scrollbar up if the selectedRow is going to be invisible
            // if (selectedRow == topRow) {
            //     searchPackagesTableVerticalScrollBar.decrease()
            // }
        }

        Keys.onDownPressed: function () {
            if (selectedRow != searchPackagesModel.rowCount() - 1) {
                selectedRow += 1;

                // TODO: Move scrollbar down if the selectedRow is going to be invisible
                // if (selectedRow == bottomRow) {
                //     searchPackagesTableVerticalScrollBar.increase()
                // }
            }
        }
    }
}
