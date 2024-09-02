import pygame
import os
from pydub import AudioSegment

class SoundPlayer():

    def __init__(self):
        pygame.mixer.init()  # Initialize the mixer once
        # Load the .wav file
        file_path_dot_wav = os.path.join('apps', 'morse_code_generator', 'static', 'dot.wav')
        file_path_dash_wav = os.path.join('apps', 'morse_code_generator', 'static', 'dash.wav')
        file_path_silence_wav = os.path.join('apps', 'morse_code_generator', 'static', 'silence.wav')
        self.file_path_output_wav = os.path.join('apps', 'morse_code_generator', 'generated_sound')
        self.sound_dot = AudioSegment.from_wav(file_path_dot_wav)
        self.sound_dash = AudioSegment.from_wav(file_path_dash_wav)
        self.sound_silence = AudioSegment.from_wav(file_path_silence_wav)

    def play_and_save_sound(self, morse_code, output_file='file.wav'):
        combined_sound = AudioSegment.empty()

        for char in morse_code:

            if char == '.':
                combined_sound += self.sound_dot + self.sound_silence

            elif char == '-':
                combined_sound += self.sound_dash + self.sound_silence

            else:
                combined_sound += self.sound_silence * 3

        combined_sound.export(f'{self.file_path_output_wav}/{output_file}', format="wav")  # Export the combined sound to MP3
