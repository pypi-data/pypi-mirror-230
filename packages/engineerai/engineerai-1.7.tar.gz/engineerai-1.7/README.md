## Ai Tools

> Transcribe Audio

``` python
from EngineerAi import *
ai = EngineerAi()
print(ai.transcribe_audio(lang="en", audio_file="simple.mp3"))
```

> Text To Speech
```python
from EngineerAi import *
ai = EngineerAi()
print(ai.text_to_speech(text="Hello Ai", lang="en", filename="simple.mp3"))
```

> Chat With Ai
```python
from EngineerAi import *
ai = EngineerAi()
print(ai.chatai(key='your openai key', question="Hi"))
```

> Generate sound
```python
from EngineerAi import *
ai = EngineerAi()
frequencies = [440.0, 523.25, 659.26]  
duration_ms = 1000 # 1s=1000
output_file = "output.wav"  
ai.generate_sound(frequencies, duration_ms, output_file)
```

> Text to frequencies
```python
from EngineerAi import *
ai = EngineerAi()
print(ai.text_to_frequencies(text='hi'))
```

### Installing

``` bash
pip3 install -U engineerai
```

### Community

- Join the telegram channel: https://t.me/tshreb_programming
