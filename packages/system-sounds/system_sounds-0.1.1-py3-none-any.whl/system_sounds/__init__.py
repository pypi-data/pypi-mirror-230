import os
import platform
import subprocess
from dataclasses import dataclass


@dataclass
class Paths:
    system: str
    music: str

path_configurations = {
    'Darwin': Paths(
        system='/System/Library/Sounds/',
        music=os.path.expanduser('~/Music/')
    ),
    'Linux': Paths(
        system='/usr/share/sounds/',
        music=os.path.expanduser('~/Music/')
    ),
    'Windows': Paths(
        system='C:\\Windows\\Media\\',
        music=os.path.expanduser('~/Music/')
    )
}

def get_system() -> str:
    return platform.system()

def list_files_from_directory(directory: str, extensions: set[str] = None) -> list[str]:
    if extensions is None:
        extensions = {'.wav', '.mp3', '.aiff'}
    
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and os.path.splitext(f)[1] in extensions]

def list_system_sounds(extensions: set[str] = None) -> list[str]:
    system = get_system()
    sound_dir = path_configurations.get(system, Paths('', '')).system
    return list_files_from_directory(sound_dir, extensions)

def list_music(extensions: set[str] = None) -> list[str]:
    system = get_system()
    music_dir = path_configurations.get(system, Paths('', '')).music
    return list_files_from_directory(music_dir, extensions)

def list_all(extensions: set[str] = None) -> list[str]:
    return list_system_sounds(extensions) + list_music(extensions)

def play_sound(sound_path: str, background: bool = True) -> None:
    system = get_system()

    if system == 'Darwin':
        cmd = ['afplay', sound_path]
    elif system == 'Linux':
        cmd = ['aplay', sound_path]
    elif system == 'Windows':
        cmd = ['start', 'wmplayer', sound_path]
    else:
        raise Exception('Unsupported OS')

    if background:
        process = subprocess.Popen(cmd)
        code = process.poll()
        if code:
            raise Exception(f"Command {' '.join(cmd)} returned non-zero status: {code}")
    else:
        code = subprocess.call(cmd)
        if code:
            raise Exception(f"Command {' '.join(cmd)} returned non-zero status: {code}")

if __name__ == '__main__':
    from pprint import pprint
    print('\nsystem')
    pprint(list_system_sounds())
    print('\nmusic')
    pprint(list_music())
    print('\nall')
    pprint(list_all())

    sounds = list_all()
    for sound in sounds:
        print(f'Playing {sound}')
        play_sound(sound, background=False)
