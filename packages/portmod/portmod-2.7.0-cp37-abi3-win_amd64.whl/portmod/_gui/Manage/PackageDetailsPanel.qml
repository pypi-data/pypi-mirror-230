import QtQuick 6.0
import QtQuick.Controls.Basic 6.0
import QtQuick.Layouts 6.0
import io.portmod 1.0

ColumnLayout {
    id: detailsPanel

    property string atom
    property string name
    property string author
    property string version
    property string size
    property string license
    property string description
    property string homepage
    property var flags_model
    property bool author_exists
    property bool homepage_exists

    // TODO: Reset index to first tab on updateDetailsPanel
    TabBar {
        id: bar

        TabButton {
            text: L10n.tr("details-panel-details-tab-label")
            width: implicitWidth
        }

        TabButton {
            text: L10n.tr("details-panel-flags-tab-label")
            width: implicitWidth
        }
    }

    StackLayout {
        currentIndex: bar.currentIndex

        ScrollView {

            contentWidth: availableWidth
            clip: true

            ColumnLayout {
                anchors.top: parent.top

                Text {
                    text: detailsPanel.name
                    font.pointSize: 16
                }

                Text {
                    text: detailsPanel.author
                    visible: detailsPanel.author_exists
                }

                Frame {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    RowLayout {
                        // TODO: Make these never go off the screen, and elide if they get to small.
                        spacing: detailsPanel.width / 8
                        anchors.horizontalCenter: parent.horizontalCenter

                        Layout.maximumWidth: detailsPanel.width

                        DetailsLabel {
                            title: L10n.tr("details-panel-version-label")
                            text: detailsPanel.version
                        }
                        DetailsLabel {
                            title: L10n.tr("details-panel-size-label")
                            text: detailsPanel.size
                        }
                        DetailsLabel {
                            title: L10n.tr("details-panel-license-label")
                            text: detailsPanel.license
                        }

                    }
                }

                Frame {
                    Layout.preferredWidth: detailsPanel.width

                    Text {
                        id: descriptionBoxLabel
                        text: detailsPanel.description
                        wrapMode: Text.WordWrap
                        width: parent.width
                    }
                }


                Button {
                    id: homepageButton
                    text: L10n.tr("details-panel-homepage-button-label")
                    onClicked: Qt.openUrlExternally(detailsPanel.homepage)
                    enabled: detailsPanel.homepage_exists
                }

            }
        }

        GroupBox {
            title: L10n.tr("details-window-local-flags-title")

            Layout.preferredWidth: parent.width

            // TODO: Have a little '?' or 'i' icon to show this information. People won't know
            // to hover to get this information
            ToolTip.text: L10n.tr("details-window-local-flags-use-info-tooltip")
            ToolTip.delay: 1000
            ToolTip.timeout: 5000
            ToolTip.visible: hovered

            ListView {
                id: useListView
                clip: true
                model: detailsPanel.flags_model
                width: parent.width
                height: parent.height
                delegate: CheckDelegate {
                    text: model.display
                    checkState: model.checkState
                    width: detailsPanel.width - 20
                    // TODO: Remove once flag setting is implemented
                    enabled: false
                }

                ScrollBar.vertical: ScrollBar {}
            }
        }
    }
}
