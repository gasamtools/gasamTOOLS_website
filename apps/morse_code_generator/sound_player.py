from pydub import AudioSegment
import os


class SoundPlayer():

    def __init__(self):
        # Load the .wav files
        file_path_dot_wav = os.path.join('apps', 'morse_code_generator', 'static', 'dot.wav')
        file_path_dash_wav = os.path.join('apps', 'morse_code_generator', 'static', 'dash.wav')
        file_path_silence_wav = os.path.join('apps', 'morse_code_generator', 'static', 'silence.wav')
        self.file_path_output_wav = os.path.join('apps', 'morse_code_generator', 'generated_sound')

        # Delete previous wav files
        self.delete_all_files(self.file_path_output_wav)

        # Load sounds using Pydub
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

        # Ensure output directory exists
        os.makedirs(self.file_path_output_wav, exist_ok=True)

        combined_sound.export(f'{self.file_path_output_wav}/{output_file}', format="wav")

    def delete_all_files(self, directory):
        # List all files in the directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            # Check if it's a file (and not a directory)
            if os.path.isfile(file_path):
                os.remove(file_path)
                # print(f"Deleted file: {file_path}")