import sounddevice as sd
import numpy as np
import speech_recognition as sr

recognizer = sr.Recognizer()

print("JARVIS is listening... 🎙️")

sample_rate = 16000
duration = 5

audio_data = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="int16"
)

sd.wait()

audio = sr.AudioData(audio_data.tobytes(), sample_rate, 2)

try:
    text = recognizer.recognize_google(audio)
    print("You:", text)

except sr.UnknownValueError:
    print("JARVIS: I couldn't understand you.")

except sr.RequestError:
    print("JARVIS: Speech service is unavailable.")