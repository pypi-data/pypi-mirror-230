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
duration = 3  
volume = 0.5  
output_file = "output.wav"  
ai.generate_sound(frequencies, duration, volume, output_file)
```

### Installing

``` bash
pip3 install -U engineerai
```

### Community

- Join the telegram channel: https://t.me/tshreb_programming
