import QtQuick 6.0
import QtQuick.Controls.Basic 6.0
import QtQuick.Layouts 6.0
import Qt.labs.settings
import io.portmod 1.0

ColumnLayout {
    id: manageTab

    // TODO: All of this gets called every time you click on a package.
    // It should be saved on click, and restored when clicked again.
    function updateDetailsPanel(rowIndex) {
        var atom = installedPackagesModel.getAtom(rowIndex);
        var name = installedPackagesModel.get_name(rowIndex);
        var author = installedPackagesModel.get_author(rowIndex);
        var version = installedPackagesModel.get_version(rowIndex);
        var size = installedPackagesModel.get_size(rowIndex);
        var license = installedPackagesModel.get_license(rowIndex);
        var description = installedPackagesModel.get_description(rowIndex);
        var homepage = installedPackagesModel.get_homepage(rowIndex);
        var flags_model = installedPackagesModel.get_local_flags_model(rowIndex);

        packageDetailsPanel.atom = atom;
        packageDetailsPanel.name = name;
        packageDetailsPanel.author = author;
        packageDetailsPanel.version = version;
        packageDetailsPanel.size = size;
        packageDetailsPanel.license = license;
        packageDetailsPanel.description = description;
        packageDetailsPanel.homepage = homepage;
        packageDetailsPanel.flags_model = flags_model;

        // Hide author text box if there are no authors
        if (!author) {
            packageDetailsPanel.author_exists = false;
        } else {
            packageDetailsPanel.author_exists = true;
        }

        // Disable homepage button if there isn't a homepage
        if (!homepage) {
            packageDetailsPanel.homepage_exists = false;
        } else {
            packageDetailsPanel.homepage_exists = true;
        }
    }

    ComboBox {
        id: prefixSwitcher

        onActivated: function (index) {
            Config.set_prefix(Config.get_prefixes()[index]);
            installedPackagesModel.changeToCurrentPrefix();
        }

        Component.onCompleted: function () {
            model = Config.get_prefixes(); // Prevents error when closing window
            currentIndex = Config.get_prefixes().indexOf(Config.get_current_prefix());
        }
    }

    RowLayout {
        Layout.fillWidth: true

        TextField {
            id: filterField
            placeholderText: L10n.tr("manage-filter-field-placeholder-text")
            Layout.fillWidth: true

            Keys.onReturnPressed: installedPackagesModel.setFilterFixedString(text)
        }
        Button {
            id: filterButton
            text: L10n.tr("manage-filter-button-text")
            onClicked: installedPackagesModel.setFilterFixedString(filterField.text)
        }
    }

    SplitView {
        orientation: Qt.Horizontal
        Layout.fillWidth: true
        Layout.fillHeight: true

        // handle: Rectangle {
        //     implicitWidth: 4
        //     implicitHeight: 4
        //     color: SplitHandle.pressed ? "#81e889"
        //         : (SplitHandle.hovered ? Qt.lighter("#c2f4c6", 1.1) : "#c2f4c6")
        // }

        InstalledPackagesPanel {
            id: installedPackagesPanel
            onSelectedRowChanged: manageTab.updateDetailsPanel(selectedRow)

            SplitView.preferredWidth: root.width * 2/3
            SplitView.minimumWidth: root.width / 4

            Connections {
                target: installedPackagesModel
                function onPrefixChanged() {
                    // TODO: This feels messy
                    updateDetailsPanel(0);
                    installedPackagesPanel.selectedRow = 0;
                    // TODO: Reset the scroll position
                }
            }
        }

        PackageDetailsPanel {
            id: packageDetailsPanel

            SplitView.preferredWidth: root.width * 1/3
            SplitView.minimumWidth: root.width / 6

            Component.onCompleted: function() {
                // TODO: Don't do this if there are no packages installed
                manageTab.updateDetailsPanel(0);
            }
        }
    }
}
