import os
import requests
import speech_recognition as sr
import openai
import gtts
from pydub import AudioSegment
from pydub.generators import Sine

def generate_sound(frequencies, duration_ms, output_file):
    song = AudioSegment.silent(duration=0)
    for frequency in frequencies:
        sine_wave = Sine(frequency)
        note = sine_wave.to_audio_segment(duration=duration_ms)
        song += note
    song.export(output_file, format="wav")

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