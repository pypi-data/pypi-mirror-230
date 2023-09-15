from setuptools import setup
import codecs
import os

# Ubuntu: sudo apt install espeak ffmpeg
install_requires = [
    'comtypes; platform_system == "Windows"',
    'pypiwin32; platform_system == "Windows"',
    'pywin32; platform_system == "Windows"',
    'pyobjc>=2.4; platform_system == "Darwin"',
    'six'
]

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


setup(
    name='rlvoice-1',
    packages=['rlvoice', 'rlvoice.drivers'],
    version='1.2.1',
    description='Text to Speech (TTS) library for Python 3. Works without internet connection or delay. Supports multiple TTS engines, including Sapi5, nsss, and espeak.',
    long_description=long_description,
    summary='Offline Text to Speech library with multi-engine support',
    author='AkulAI',
    long_description_content_type="text/markdown",
    url='https://github.com/Akul-AI/rlvoice-1',
    author_email='akulgoel2010@gmail.com',
    install_requires=install_requires,
    keywords=['rlvoice', 'pyttsx' , 'ivona','pyttsx for python3' , 'TTS for python3' , 'rlvoice' ,'text to speech for python','tts','text to speech','speech','speech synthesis','offline text to speech','offline tts','gtts'],
    classifiers = [
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
    ],
)
