from setuptools import setup, find_packages

setup (
    name="audiomr",
    version="0.1",
    author="Matheus Rodrigo",
    description="Audio for systems",
    packages=find_packages(),
    install_requires=[
        "PyAudio",
        "SpeechRecognition",
        "pyttsx3"
    ]
)