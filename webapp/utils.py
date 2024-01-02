import simpleaudio as sa

def play_wav(file_path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        wave_obj.play()

    except Exception as e:
        print(f"Error playing sound: {e}")

