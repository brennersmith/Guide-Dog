import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QTimer, Qt
from PyQt5.QtQuick import QQuickView
from PyQt5.QtGui import QGuiApplication, QKeyEvent
from PyQt5.QtQml import QQmlApplicationEngine, QQmlProperty
from geopy.distance import geodesic
import pyttsx3
import math
import geocoder
import googlemaps  # Add this import
import threading  # Add this import

# Simulated path (lat, lon)
path = [
    (42.672, -83.215),
    (42.6725, -83.2155),
    (42.673, -83.216),
    (42.6735, -83.2165)
]

def get_arrow_emoji(start, end):
    dx = end[1] - start[1]  # longitude difference
    dy = end[0] - start[0]  # latitude difference
    angle = math.degrees(math.atan2(dy, dx))  # angle in degrees

    if -22.5 < angle <= 22.5:
        return "→"
    elif 22.5 < angle <= 67.5:
        return "⇗"
    elif 67.5 < angle <= 112.5:
        return "↑"
    elif 112.5 < angle <= 157.5:
        return "⇖"
    elif angle > 157.5 or angle <= -157.5:
        return "←"
    elif -157.5 < angle <= -112.5:
        return "⇙"
    elif -112.5 < angle <= -67.5:
        return "↓"
    elif -67.5 < angle <= -22.5:
        return "⇘"
    else:
        return "↑"
    
class GPSNavigator(QObject):
    def __init__(self, engine):
        super().__init__()
        self.engine = None  # Remove TTS engine initialization
        self.qml_engine = engine
        self.gmaps_client = googlemaps.Client(key="API_KEY_HERE")  # Replace with your API key

        root_objects = engine.rootObjects()
        if not root_objects:
            raise RuntimeError("Failed to load QML file or root object is missing.")

        self.map_obj = root_objects[0].findChild(QObject, "mapObj")
        if not self.map_obj:
            raise RuntimeError("mapObj not found in QML file.")

        self.current_location = None
        self.start_point = None
        self.path_to_home = []
        self.route_index = 0  # Track the user's progress along the route
        self.path_to_home_steps = []  # Initialize as an empty list
        self.no_route_message_shown = False  # Track if "No route to follow" has been shown
        self.last_announced_direction = None  # Track the last announced direction

    @pyqtSlot()
    def start_walk(self):
        """Mark the starting point on the map."""
        if not self.current_location:
            self.fetch_current_location()  # Fetch the current location if not already set
        if self.current_location:
            self.start_point = self.current_location
            print(f"Start point marked at: {self.start_point}")
            self.map_obj.setProperty("latitude", self.start_point[0])
            self.map_obj.setProperty("longitude", self.start_point[1])
        else:
            print("Failed to fetch current location. Cannot start walk.")

    @pyqtSlot()
    def bring_me_home(self):
        """Use Google Maps API to calculate a walking route to the start point and display it on the map."""
        if not self.start_point:
            print("Start point is not set. Cannot bring you home.")
            return

        if not self.current_location:
            print("Current location is not available.")
            return

        print(f"Fetching directions from {self.current_location} to {self.start_point}...")
        try:
            directions = self.gmaps_client.directions(
                origin=self.current_location,
                destination=self.start_point,
                mode="walking"
            )
        except Exception as e:
            print(f"Error fetching directions: {e}")
            return

        if not directions or "legs" not in directions[0]:
            print("Failed to fetch valid directions.")
            return

        # Extract the path (list of lat/lng points) and steps from the directions response
        self.path_to_home = [
            (step["end_location"]["lat"], step["end_location"]["lng"])
            for step in directions[0]["legs"][0]["steps"]
        ]
        self.path_to_home_steps = directions[0]["legs"][0]["steps"]

        # Print the directions step-by-step
        print("Directions:")
        for i, step in enumerate(self.path_to_home_steps):
            distance = step["distance"]["text"]
            duration = step["duration"]["text"]
            instructions = step["html_instructions"].replace("<b>", "").replace("</b>", "").replace("<div style=\"font-size:0.9em\">", "").replace("</div>", "")
            print(f"Step {i + 1}: {instructions} ({distance}, {duration})")

        # Send the path to the QML map for visual display
        self.map_obj.setProperty("path", [{"latitude": lat, "longitude": lon} for lat, lon in self.path_to_home])

        # Reset the route index
        self.route_index = 0
        print("Route calculated. Follow the directions.")
        self.update_directions()  # Provide the first direction immediately

    def provide_directions(self):
        """Provide step-by-step directions along the path to the start point."""
        if not self.path_to_home:
            print("No path to follow.")
            return

        for i in range(len(self.path_to_home) - 1):
            start = self.path_to_home[i]
            end = self.path_to_home[i + 1]

            # Extract road name and maneuver from the Google Maps API response
            step = self.path_to_home_steps[i]
            road_name = step.get("html_instructions", "").replace("<b>", "").replace("</b>", "")
            maneuver = step.get("maneuver", "continue straight")

            # Determine the direction text
            if maneuver == "turn-left":
                direction = f"Turn left onto {road_name}"
            elif maneuver == "turn-right":
                direction = f"Turn right onto {road_name}"
            elif maneuver == "continue":
                direction = f"Continue straight on {road_name}"
            else:
                direction = f"{maneuver.capitalize()} on {road_name}"

            # Calculate distance to the next step
            distance = int(geodesic(start, end).feet)
            text = f"{direction}. Walk {distance} feet."
            print(text)

            # Move the marker to the next point
            self.current_location = end
            self.map_obj.setProperty("latitude", end[0])
            self.map_obj.setProperty("longitude", end[1])
            QTimer.singleShot(500, lambda: None)  # Simulate delay for each step

        print("You have arrived at the start point.")

    def simulate_path(self, start, end):
        """Simulate a path from the current location to the start point."""
        steps = 10  # Number of steps in the path
        lat_step = (end[0] - start[0]) / steps
        lon_step = (end[1] - start[1]) / steps
        return [(start[0] + i * lat_step, start[1] + i * lon_step) for i in range(steps + 1)]

    
    def move_location(self, dx, dy):
        """Simulate movement by updating the current location."""
        if self.current_location:
            new_lat = self.current_location[0] + dy
            new_lon = self.current_location[1] + dx
            self.current_location = (new_lat, new_lon)
            self.map_obj.setProperty("latitude", new_lat)
            self.map_obj.setProperty("longitude", new_lon)

            # Center the map on the marker
            self.map_obj.setProperty("center", {"latitude": new_lat, "longitude": new_lon})

            # Check if the user is near the next point on the route
            self.update_directions()

    def update_directions(self):
        """Update directions based on the user's current location."""
        if not self.path_to_home_steps:  # Check if the route exists
            if not self.no_route_message_shown:  # Ensure the message is printed only once
                print("No route to follow.")
                self.no_route_message_shown = True
            return

        self.no_route_message_shown = False  # Reset when a route exists

        if self.route_index >= len(self.path_to_home_steps):
            print("You have arrived at the start point.")
            return

        # Get the next step in the route
        next_step = self.path_to_home_steps[self.route_index]
        next_point = self.path_to_home[self.route_index]

        # Check if the user is close to the next point
        distance_to_next = geodesic(self.current_location, next_point).feet
        if distance_to_next < 20:  # Threshold for reaching the next point
            print(f"Reached step {self.route_index + 1}. Moving to the next step.")
            self.route_index += 1
            if self.route_index < len(self.path_to_home_steps):
                next_step = self.path_to_home_steps[self.route_index]
                self.announce_turn(next_step)
        elif distance_to_next < 100:  # Notify the user when close to a turn
            print(f"Approaching turn in {int(distance_to_next)} feet.")
        else:
            # Notify the user of the current direction only if it changes
            self.announce_turn(next_step)

    def announce_turn(self, step):
        """Announce the next turn or direction."""
        road_name = step.get("html_instructions", "").replace("<b>", "").replace("</b>", "")
        maneuver = step.get("maneuver", "continue straight")

        if maneuver == "turn-left":
            direction = f"Turn left onto {road_name}"
        elif maneuver == "turn-right":
            direction = f"Turn right onto {road_name}"
        elif maneuver == "continue":
            direction = f"Continue straight on {road_name}"
        else:
            direction = f"{maneuver.capitalize()} on {road_name}"

        # Only print the direction if it has changed
        if direction != self.last_announced_direction:
            print(direction)
            self.last_announced_direction = direction

    def fetch_current_location(self):
        """Fetch the current GPS location."""
        g = geocoder.ip('me')  # Replace with a GPS module for real hardware
        if g.ok:
            self.current_location = (g.latlng[0], g.latlng[1])
            print(f"Current location: {self.current_location}")
            self.map_obj.setProperty("latitude", self.current_location[0])
            self.map_obj.setProperty("longitude", self.current_location[1])
        else:
            print("Failed to fetch current location.")

class KeyHandler(QObject):
    def __init__(self, gps_nav):
        super().__init__()
        self.gps_nav = gps_nav

    def eventFilter(self, obj, event):
        if event.type() == QKeyEvent.KeyPress:
            step_size = 0.000005  # Reduced movement step size
            if event.key() == Qt.Key_Up:
                self.gps_nav.move_location(0, step_size)  # Move north
            elif event.key() == Qt.Key_Down:
                self.gps_nav.move_location(0, -step_size)  # Move south
            elif event.key() == Qt.Key_Left:
                self.gps_nav.move_location(-step_size, 0)  # Move west
            elif event.key() == Qt.Key_Right:
                self.gps_nav.move_location(step_size, 0)  # Move east
        return super().eventFilter(obj, event)

# ---------- MAIN APP ----------
if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile("map_view.qml"))

    gps_nav = GPSNavigator(engine)
    engine.rootContext().setContextProperty("gpsNav", gps_nav)

    key_handler = KeyHandler(gps_nav)
    app.installEventFilter(key_handler)

    gps_nav.fetch_current_location()  # Fetch and display the current location

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
