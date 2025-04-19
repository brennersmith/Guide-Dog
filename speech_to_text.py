# Python program to translate
# speech to text and text to speech


import speech_recognition as sr
import pyttsx3
import threading
import keyboard

# Initialize the recognizer
r = sr.Recognizer()

startSet = {"start", "start walk", "starts"}
endSet = {"end", "end walk", "ends"}
yesSet = {"yes", "ye"}
noSet = {"no"}
weatherSet = {"what's the weather", "what is the weather"}

# Initialize the TTS engine
tts_engine = pyttsx3.init()
tts_lock = threading.Lock()  # Lock to prevent overlapping TTS

def speakText(command):
    with tts_lock:  # Ensure only one TTS runs at a time
        tts_engine.say(command)
        tts_engine.runAndWait()

def userCommand(input):
    if input in yesSet:
        print("Yes command has been confirmed")

        speakText("Yes received")

    elif input in noSet:
        print("No command has been confirmed")
        speakText("No received")

    else:
        print("Invalid command")
        # speakText("Invalid command")

    """
    if input in startSet:
        print("Walk has been started.")
        speakText("Walk has been started.")

    elif input in endSet:
        print("Walk has ended.")
        speakText("Walk has been ended.")

    elif input in weatherSet:
        print("Relaying weather...")
        speakText("The weather is currently...")

    else:
        print("Invalid command.")
        speakText("Please try again.")
    """

# Loop infinitely for user to
# speak

#Takes user keyboard input to start listening 
def startListening():

    while True:
        if keyboard.is_pressed('l'):

            # Exception handling to handle
            # exceptions at the runtime
            try:

                # use the microphone as source for input.
                with sr.Microphone() as source2:

                    # wait for a second to let the recognizer
                    # adjust the energy threshold based on
                    # the surrounding noise level
                    r.adjust_for_ambient_noise(source2, duration=1)

                    # listens for the user's input
                    audio2 = r.listen(source2)

                    # Using google to recognize audio
                    MyText = r.recognize_google(audio2)
                    MyText = MyText.lower()


                    print(f"Did you say: {MyText}")
                    userCommand(MyText)


            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

            except sr.UnknownValueError:
                print("Unknown error encountered.")

startListening()