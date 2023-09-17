import os
import requests
import speech_recognition as sr
import openai
import gtts
import numpy as np
import pyaudio
import wave
import librosa

def generate_sound(frequencies, duration, volume, output_file):
    audio_data = np.zeros(int(44100 * duration), dtype=np.float32)

    for frequency in frequencies:
        t = np.linspace(0, duration, int(44100 * duration), endpoint=False)  
        waveform = volume * np.sin(2 * np.pi * frequency * t)  

        audio_data += waveform

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    output=True)
    stream.start_stream()
    stream.write(audio_data.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(4)
        wf.setframerate(44100)
        wf.writeframes(audio_data.tobytes())

def transcribe_audio(lang, audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data, language=lang)
        return text

def ask_question(key,question):
    openai.api_key = key
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=question
    )

    answer = response.choices[0].text.strip()
    return answer

def text_to_speech(text, lang, filename):
    audio = gtts.gTTS(text=text, lang=lang, slow=False).save(filename)
    return True