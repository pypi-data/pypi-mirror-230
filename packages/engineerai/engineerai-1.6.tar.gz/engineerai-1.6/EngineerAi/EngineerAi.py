from .api import text_to_speech, transcribe_audio, ask_question, generate_sound

class EngineerAi():
	def __init__(self):
		pass
	def transcribe_audio(self, lang, audio_file):
		return transcribe_audio(lang, audio_file)
	def text_to_speech(self, text, lang, filename):
		text_to_speech(text, lang, filename)
		return True
	def chatai(self, key, question):
		return ask_question(key, question)
	def generate_sound(self, frequencies, duration_ms, output_file):
		return generate_sound(frequencies, duration_ms, output_file)
