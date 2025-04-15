import sys
import subprocess
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap
import pyttsx3
import threading
import os

class GuideDogApp(QWidget):
    def __init__(self):
        super().__init__()
        self.tts_engine = pyttsx3.init(driverName='sapi5')
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)  # Use the first available voice
        self.tts_engine.setProperty('volume', 1.0)
        self.tts_engine.setProperty('rate', 150)
        self.initUI()


    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Guide Dog")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #D3D3D3;")

        # Create a vertical layout for the main window
        layout = QVBoxLayout()

        # Create a horizontal layout for the title and image
        horizontal_layout = QHBoxLayout()
        # spacer to the left
        horizontal_layout.addSpacerItem(QSpacerItem(180, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))    

        # Add a title label
        title = QLabel("Guide Dog")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 56px; font-weight: bold; margin: 20px;")
        horizontal_layout.addWidget(title)  # Align title to the left

        # spacer between title and image
        horizontal_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Minimum))


        # Add an image
        image = QLabel(self)
        logo_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(logo_dir, 'guideDog-removebg-preview.png')
        pixmap = QPixmap(logo_path)

       
        # Scale the image to a smaller size
        scaled_pixmap = pixmap.scaled(175, 175, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.setPixmap(scaled_pixmap)
        image.setStyleSheet("margin: 20px;")
        horizontal_layout.addWidget(image)  # Align image to the right

        # Add a spacer to the right
        horizontal_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Add the horizontal layout to the main vertical layout
        layout.addLayout(horizontal_layout)

        # self.speak("Welcome to Guide Dog")

        self.start_timer()

        # Add the rest of the widgets (e.g., buttons) to the vertical layout

        # Add a button to launch the weather app
        weather_button = QPushButton("Open Weather")
        weather_button.setStyleSheet("""
            padding: 10px 20px;
            font-size: 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        """)
        weather_button.clicked.connect(self.launch_weather)
        layout.addWidget(weather_button)

        # Set the layout for the main window
        self.setLayout(layout)

    def launch_weather(self):
        try:
            self.close
            dir_name = os.path.dirname(os.path.abspath(__file__))
            weather_path = os.path.join(dir_name, 'Weather.py')
            # Launch the Weather.py script
            subprocess.Popen(['python', weather_path], shell=True)
        except Exception as e:
            print(f"Failed to launch weather app: {e}")

    def start_timer(self):
        # Timer to say the welcome message
        startup_timer = threading.Timer(2, self.speak, args=("Welcome to Guide Dog",))
        startup_timer.start()

        # Timer to launch the weather app
        timer = threading.Timer(4, self.launch_weather)
        timer.start()

    def speak(self, text):  
        self.tts_engine.say(text)  
        self.tts_engine.runAndWait()

# Main entry point
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = GuideDogApp()
    main_window.show()
    sys.exit(app.exec_())
    