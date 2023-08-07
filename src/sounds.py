import os
import multiprocessing
from enum import Enum

class SoundConfig:
    file_name: str
    volume: float

    def __init__(self, file_name: str, volume: float):
        self.file_name = file_name
        self.volume = volume

class SoundEffect(Enum):
    STAR_POWER = SoundConfig("star_power.mp3", 20)
    MARIO_DIE = SoundConfig("mario_die.mp3", 6)
    MARIO_JUMP = SoundConfig("mario_jump.mp3", 2)
    FIRE_BALL = SoundConfig("fireball.mp3", 2)
    MARIO_COIN = SoundConfig("mario_coin.mp3", 6)
    IM_A_WAITING = SoundConfig("imawaiting.mp3", 25)
    LETSA_GO = SoundConfig("mario_letsa_go.mp3", 12)
    PIPE = SoundConfig("mario_pipe.mp3", 3)
    JUST_WHAT_I_NEEDED = SoundConfig("mario_just_what_i_needed.mp3", 8)
    FREE_GUY = SoundConfig("mario_1up.mp3", 6)
    YEAHOO = SoundConfig("yeahoo.mp3", 6)
    POWER_UP = SoundConfig("mario_power_up.mp3", 4)
    MAMA_MIA = SoundConfig("mama_mia.mp3", 4)
    WORLD_CLEAR = SoundConfig("mario_world_clear.mp3", 4)
    FIREWORK = SoundConfig("mario_firework.mp3", 16)
    UNDERGROUND = SoundConfig("mario_underground.mp3", 18)
    PLAY = SoundConfig("mario_play.mp3", 12)

class Sounds:
    volume = 0.5

    def __init__ (self):
        self.message_q = multiprocessing.Queue()

    def play_sound(self, sound: SoundEffect):
        os.system(f"mpg321 -g {sound.value.volume * self.volume} /home/johnmartin/Documents/src/assets/{sound.value.file_name} &")

    def volume_up(self):
        self.volume = min(2.5, self.volume + 0.25)
        self.play_sound(SoundEffect.FIRE_BALL)

    def volume_down(self):
        self.volume = max(0.5, self.volume - 0.25)
        self.play_sound(SoundEffect.FIRE_BALL)