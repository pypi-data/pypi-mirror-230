import QtQuick 6.0
import QtQuick.Controls.Basic 6.0
import QtQuick.Layouts 6.0
import "Manage"
import "Search"
import io.portmod 1.0

// TODO: Why does scroll intertia not work with a trackpad?

// TODO: Have a notification bell in the header that shows news, and pending merges,
// among other things that might fit.

ApplicationWindow {
    id: root

    title: "Portmod"
    width: Screen.width / 2
    height: Screen.height / 2
    visible: true

    // TODO: Maybe have a seperator between the tabs and content, because the tabs look
    // weird without one when they don't take up the full width.

    header: TabBar {
        id: mainTabBar
        width: parent.width

        TabButton {
            text: L10n.tr("manage-tab-label")
            // width: root.width / 10
        }
        TabButton {
            text: L10n.tr("search-tab-label")
            // width: root.width / 10
        }
    }

    StackLayout {
        id: mainStackLayout
        currentIndex: mainTabBar.currentIndex
        anchors.fill: parent

        ManageTab {}

        SearchTab {}
    }
}
