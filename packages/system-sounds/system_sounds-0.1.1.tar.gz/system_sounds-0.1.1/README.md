# system-sounds

## Table of Contents
1. [Description](#description)
2. [Installation](#installation)
   - [pip](#pip)
   - [poetry](#poetry)
3. [Usage](#usage)
   - [Listing System Sounds](#listing-system-sounds)
   - [Listing User's Music](#listing-users-music)
   - [Listing Both System Sounds and Music](#listing-both-system-sounds-and-music)
   - [Playing a Sound](#playing-a-sound)
   - [Advanced Usage - Custom Directory and Extensions](#advanced-usage---custom-directory-and-extensions)
4. [Alternatives for Playback](#alternatives-for-playback)
   - [sounddevice + soundfile](#sounddevice--soundfile)
   - [playsound](#playsound)
   - [pyaudio](#pyaudio)

---

### Description
The System Sounds library provides a straightforward interface to list and play system and user music sounds. It is cross-platform, supporting macOS, Linux, and Windows. 

### Installation

To install the library, use one of the following package managers:

#### pip
```
pip install system-sounds
```

#### poetry
```
poetry add system-sounds
```

### Usage

#### Listing System Sounds:
To retrieve a list of available system sounds, use:
```python
from system_sounds import list_system_sounds

sounds = list_system_sounds()
print(sounds)
```

#### Listing User's Music:
To retrieve a list of music from the user's default music directory, use:
```python
from system_sounds import list_music

music = list_music()
print(music)
```

#### Listing Both System Sounds and Music:
To retrieve a combined list of system sounds and user music, use:
```python
from system_sounds import list_all

all_sounds = list_all()
print(all_sounds)
```

#### Playing a Sound:
To play a sound, use the `play_sound` function:
```python
from system_sounds import play_sound

play_sound("path_to_sound_file.wav")
```

#### Advanced Usage - Custom Directory and Extensions:
If you'd like to list files from a custom directory or look for sound files with specific extensions, utilize the `list_files_from_directory` function:

```python
from system_sounds import list_files_from_directory

custom_sounds = list_files_from_directory("/path/to/directory", extensions={'.wav', '.ogg'})
print(custom_sounds)
```

### Alternatives for Playback

The library uses system commands to play sounds, which might not be optimal or available for every scenario. For fallback or alternative methods, consider using:

#### sounddevice + soundfile:
This combination allows for playback and reading of sound files in various formats.
  
  Installation:
  ```
  pip install sounddevice soundfile
  ```

  Example usage:
  ```python
  import soundfile as sf
  import sounddevice as sd

  data, samplerate = sf.read('path_to_sound_file.wav')
  sd.play(data, samplerate)
  sd.wait()
  ```

#### playsound:
A pure Python solution without dependencies.

  Installation:
  ```
  pip install playsound
  ```

  Example usage:
  ```python
  from playsound import playsound

  playsound('path_to_sound_file.mp3')
  ```

#### pyaudio:
Allows you to play and record audio on various platforms.

  Installation:
  ```
  pip install pyaudio
  ```

  Example usage requires reading the sound file with a library like `wave` and then playing it with `pyaudio`.

Remember, while these alternatives provide more features or flexibility, they might also introduce additional dependencies or complexities to your application.