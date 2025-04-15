import QtQuick 2.12
import QtQuick.Window 2.12
import QtLocation 5.12
import QtPositioning 5.12
import QtQuick.Controls 2.12

Window {
    visible: true
    width: 640
    height: 480
    title: qsTr("Route Planner")

    Plugin {
        id: mapPlugin
        name: "osm" // OpenStreetMap
    }

    Map {
        id: mapObj
        objectName: "mapObj"
        anchors.fill: parent
        plugin: mapPlugin
        center: QtPositioning.coordinate(mapObj.latitude, mapObj.longitude) // Center on marker
        zoomLevel: 16

        MapPolyline {
            id: routePolyline
            line.width: 5
            line.color: "blue"
            path: [] // Initialize with an empty path
        }

        MapQuickItem {
            id: currentLocationMarker
            anchorPoint.x: 12
            anchorPoint.y: 12
            coordinate: QtPositioning.coordinate(mapObj.latitude, mapObj.longitude)
            sourceItem: Rectangle {
                width: 24
                height: 24
                color: "green"
                radius: 12
                border.color: "black"
                border.width: 2
            }
        }

        property real latitude: 42.672
        property real longitude: -83.215
        property var path: [] // Property to hold the path for the polyline

        onLatitudeChanged: currentLocationMarker.coordinate.latitude = latitude
        onLongitudeChanged: currentLocationMarker.coordinate.longitude = longitude

        onPathChanged: {
            routePolyline.path = path.map(function(coord) {
                return QtPositioning.coordinate(coord.latitude, coord.longitude);
            });
        }
    }

    Column {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10

        Button {
            text: "Create Route"
            onClicked: routePlanner.create_route(42.672, -83.215, 42.6735, -83.2165)
        }

        Button {
            text: "Start Walk"
            onClicked: gpsNav.start_walk()
        }

        Button {
            text: "Bring Me Home"
            onClicked: gpsNav.bring_me_home()
        }
    }
}