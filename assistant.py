import sounddevice as sd
import speech_recognition as sr
import pyttsx3

from brain import ask_jarvis
from vision import detect_objects
from automation import open_application


recognizer = sr.Recognizer()
engine = pyttsx3.init()

sample_rate = 16000
duration = 5


def speak(text):
    print("\nJARVIS:", text)

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as error:
        print("TTS Error:", error)


def listen():
    print("\nJARVIS is listening... 🎙️")

    try:
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio = sr.AudioData(
            audio_data.tobytes(),
            sample_rate,
            2
        )

        text = recognizer.recognize_google(audio)

        print("You:", text)

        return text.strip()

    except sr.UnknownValueError:
        print("JARVIS could not understand.")
        return ""

    except sr.RequestError:
        print("Speech recognition service unavailable.")
        return ""

    except Exception as error:
        print("Microphone Error:", error)
        return ""


def is_vision_command(text):
    text = text.lower()

    commands = [
        "what do you see",
        "what can you see",
        "what are you seeing",
        "look at this",
        "look at that",
        "use camera",
        "open camera",
        "check camera",
        "camera dekho",
        "camera se dekho",
        "kya dikh raha hai",
        "kya nazar aa raha hai",
        "mere samne kya hai",
        "samne kya hai"
    ]

    return any(command in text for command in commands)


def get_vision_answer(user_message):

    print("\nJARVIS Vision: Checking camera... 👁️")

    vision_result = detect_objects()

    print("Vision Result:", vision_result)

    prompt = f"""
You are JARVIS.

The camera detected:
{vision_result}

The user asked:
{user_message}

Answer ONLY using the detected information.

Language rules:
- English question = English answer.
- Roman Urdu question = Roman Urdu answer.
- Do not randomly switch languages.
- Do not invent objects.
- Keep the answer short.
"""

    return ask_jarvis(prompt)


def get_application_name(text):

    text = text.lower().strip()

    commands = {
        "calculator": [
            "open calculator",
            "start calculator",
            "launch calculator",
            "calculator kholo",
            "calculator open karo"
        ],

        "notepad": [
            "open notepad",
            "start notepad",
            "launch notepad",
            "notepad kholo",
            "notepad open karo"
        ],

        "paint": [
            "open paint",
            "start paint",
            "launch paint",
            "paint kholo",
            "paint open karo"
        ],

        "chrome": [
            "open chrome",
            "start chrome",
            "launch chrome",
            "chrome kholo",
            "chrome open karo",
            "google chrome kholo"
        ],

        "vs code": [
            "open vs code",
            "start vs code",
            "launch vs code",
            "open vscode",
            "vscode kholo",
            "vs code kholo"
        ]
    }

    for app_name, phrases in commands.items():

        for phrase in phrases:

            if phrase in text:
                return app_name

    return None


def handle_automation(user_message):

    app_name = get_application_name(user_message)

    if app_name is None:
        return None

    print("\nJARVIS Automation:", app_name)

    return open_application(app_name)


def main():

    print("=" * 55)
    print("JARVIS AI ASSISTANT")
    print("=" * 55)

    print("Voice: ONLINE")
    print("AI Brain: ONLINE")
    print("Vision: ONLINE")
    print("Automation: ONLINE")

    print("=" * 55)

    speak("JARVIS is online.")

    while True:

        user_message = listen()

        if not user_message:
            continue

        lower_message = user_message.lower().strip()

        # EXIT
        if lower_message in [
            "exit",
            "quit",
            "goodbye",
            "stop jarvis",
            "shutdown"
        ]:

            speak("Goodbye.")
            break

        # VISION
        if is_vision_command(user_message):

            speak("Let me check.")

            answer = get_vision_answer(user_message)

            speak(answer)

            continue

        # AUTOMATION
        automation_result = handle_automation(user_message)

        if automation_result:

            speak(automation_result)

            continue

        # NORMAL AI
        answer = ask_jarvis(user_message)

        speak(answer)


if __name__ == "__main__":
    main()