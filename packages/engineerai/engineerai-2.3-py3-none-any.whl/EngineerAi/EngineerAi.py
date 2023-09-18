import os
from typing import List
import requests
import openai
import gtts
import pyaudio
import numpy as np
import wave

from pydub import AudioSegment
from pydub.generators import Sine
import speech_recognition as sr

char_to_freq = {
    'a': 440.00, 'b': 493.88, 'c': 523.25, 'd': 587.33, 'e': 659.26,
    'f': 698.46, 'g': 783.99, 'h': 880.00, 'i': 987.77, 'j': 1046.50,
    'k': 1174.66, 'l': 1318.51, 'm': 1396.91, 'n': 1567.98, 'o': 1760.00,
    'p': 1975.53, 'q': 2093.00, 'r': 2349.32, 's': 2637.02, 't': 2793.83,
    'u': 3135.96, 'v': 3520.00, 'w': 3951.07, 'x': 4186.01, 'y': 4698.63,
    'z': 5274.04,

    'أ': 440.00, 'ب': 493.88, 'ت': 523.25, 'ث': 587.33, 'ج': 659.26,
    'ح': 698.46, 'خ': 783.99, 'د': 880.00, 'ه': 987.77, 'و': 1046.50,
    'ز': 1174.66, 'ح': 1318.51, 'ط': 1396.91, 'ي': 1567.98, 'ك': 1760.00,
    'ل': 1975.53, 'م': 2093.00, 'ن': 2349.32, 'س': 2637.02, 'ع': 2793.83,
    'غ': 3135.96, 'ف': 3520.00, 'ق': 3951.07, 'ر': 4186.01, 'ش': 4698.63,

    'а': 440.00, 'б': 493.88, 'в': 523.25, 'г': 587.33, 'д': 659.26,
    'е': 698.46, 'ё': 783.99, 'ж': 880.00, 'з': 987.77, 'и': 1046.50,
    'й': 1174.66, 'к': 1318.51, 'л': 1396.91, 'м': 1567.98, 'н': 1760.00,
    'о': 1975.53, 'п': 2093.00, 'р': 2349.32, 'с': 2637.02, 'т': 2793.83,
    'у': 3135.96, 'ф': 3520.00, 'х': 3951.07, 'ц': 4186.01, 'ч': 4698.63,
}

class EngineerAi:
    def __init__(self) -> None:
        super().__init__()

    def text_to_frequencies(
            self,
            text: str
    ) -> list:
        """
        Args:
            text (str):  query

        Returns:
            list: list of frequencies
        """
        word = text.lower()
        sound_frequencies = []

        for c in word:
            frequency = char_to_freq.get(c, 0)
            sound_frequencies.append(frequency)
        return sound_frequencies

    def generate_sound(
            self,
            frequencies: List["float"],
            duration_ms: int,
            output_file: str
        ) -> None:
        """generate sound from frequencies

        Args:
            frequencies (List[&quot;float&quot;]): List of frequencies
            duration_ms (int): Duration
            output_file (str): output path
        """
        song = AudioSegment.silent(duration=0)
        for frequency in frequencies:
            sine_wave = Sine(frequency)
            note = sine_wave.to_audio_segment(duration=duration_ms)
            song += note
        song.export(output_file, format="wav")

    def text_to_sound(
            self,
            text: str,
            duration_ms: int,
            output_file: str
        ) -> None:
        """Text to sound 

        Args:
            text (str): query
            duration_ms (int): duration
            output_file (str): output path
        """
        freqs = self.text_to_frequencies(text)
        self.generate_sound(freqs, duration_ms, output_file)

    def frequencies_to_text(
            self,
            frequencies: List["float"]
        ) -> str:
        """frequencies to text

        Args:
            frequencies (List[&quot;float&quot;]): List of frequencies

        Returns:
            str: text
        """
        text = ""
        for freq in frequencies:
            if freq == 0:
                text += ' '
            else:
                closest_char = None
                closest_diff = float('inf')

                for char, char_freq in char_to_freq.items():
                    diff = abs(char_freq - freq)
                    if diff < closest_diff:
                        closest_diff = diff
                        closest_char = char

                text += closest_char

        return text

    def transcribe_audio(
            self,
            lang: str,
            audio_file: str
        ) -> str:
        """Audio to text using google service

        Args:
            lang (str): ISO 639-1 Language code ( ar-SA , en-US , etc ... )
            audio_file (str): audio path

        Returns:
            str: text
        """
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language=lang)
            return text

    def chatai(
            self,
            key: str,
            question: str
        ) -> str:
        """Ask CHAT GPT

        Args:
            key (str): Open AI Key
            question (str): The question

        Returns:
            str: The answer
        """
        openai.api_key = key
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=question
        )

        answer = response.choices[0].text.strip()
        return answer

    def text_to_speech(
            self,
            text: str,
            lang: str,
            filename: str
        ) -> bool:
        """Text to speech using google service

        Args:
            text (str): Text to speech query
            lang (str): ISO 639-2 language code ( en, ar, etc.. )
            filename (str): Output path

        """
        gtts.gTTS(text=text, lang=lang, slow=False).save(filename)
        return True