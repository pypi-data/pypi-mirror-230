from setuptools import setup, find_packages

requirements = [
    "numpy",
    "librosa",
    "soundfile",
    "pydub"
]


setup(
    name="audio-slicer",
    version="1.0.1",
    description="Automatically segregates audio and cleans up muted parts",
    author="leochen",
    author_email="markchen0312@gmail.com",
    url="https://github.com/ai-forks/audio-slicer",
    license="MIT",
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "audio-slicer = src.main:main",
        ]
    },
)
