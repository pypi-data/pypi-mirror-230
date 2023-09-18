import QtQuick 6.0
import QtQuick.Controls.Basic 6.0
import QtQuick.Layouts 6.0

ColumnLayout {
    id: detailsLabel

    property string title
    property string text

    Layout.alignment: Qt.AlignHCenter

    Label {
        text: detailsLabel.title
        font.weight: Font.Medium

        Layout.alignment: Qt.AlignHCenter
    }

    Label {
        text: detailsLabel.text
        wrapMode: Text.Wrap
        maximumLineCount: 1
        elide: Text.ElideRight
    }
}
