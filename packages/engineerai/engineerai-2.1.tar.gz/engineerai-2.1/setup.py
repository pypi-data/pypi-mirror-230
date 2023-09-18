from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '2.1'
DESCRIPTION = 'Ai Tools for developers'

setup(
    name="engineerai",
    version=VERSION,
    author="Engineer Man",
    author_email="MrAws.developer@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests', 'SpeechRecognition','openai'],
    keywords=['python', 'ai', 'speech', 'text','eng-tools','eng-ai','pydub','pyaudio','numpy'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires="~=3.6",
)
