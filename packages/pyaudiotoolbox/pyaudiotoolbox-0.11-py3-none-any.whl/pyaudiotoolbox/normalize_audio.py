from pydub import AudioSegment

def normalize_audio(input_audio, target_volume):
    # Load the input audio file
    audio = AudioSegment.from_file(input_audio)

    # Calculate the current volume of the audio
    current_volume = audio.dBFS

    # Calculate the gain required to reach the target volume
    gain = target_volume - current_volume

    # Apply the gain to normalize the audio
    normalized_audio = audio + gain

    return normalized_audio
