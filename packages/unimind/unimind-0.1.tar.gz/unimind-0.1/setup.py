from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='unimind',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'openai',
        'sounddevice',
        'wavio',
        'pyautogui',
        'numpy',
        'python-dotenv',
        'google-cloud-texttospeech',
        'google-cloud-speech',
        'pyaudio',
        'pycaw',
        'asyncio',
        'tkinter'
    ],
    entry_points={
        'console_scripts': [
            'unimind = unimind.__main__:main',
            'unimind-gui = unimind.tk_gui:launch_app'
        ],
    },
    author="Rade Ilijev",
    author_email="rade.ilijev8@gmail.com",
    description="description",
    long_description=long_description,
    long_description_content_type="text/markdown"
)
