from pydub import AudioSegment

def trim_audio(input_audio, output_audio, start_time_ms, end_time_ms):
    """
    Trim an audio segment from the input audio file and save it to the output file.

    Args:
        input_audio (str): Path to the input audio file.
        output_audio (str): Path to save the trimmed audio file.
        start_time_ms (int): Start time in milliseconds.
        end_time_ms (int): End time in milliseconds.
    """
    audio = AudioSegment.from_file(input_audio)
    trimmed_audio = audio[start_time_ms:end_time_ms]
    trimmed_audio.export(output_audio, format="mp3")

def split_audio(input_audio, output_prefix, split_points_ms):
    """
    Split an audio file into multiple segments at specified split points and save each segment to separate files.

    Args:
        input_audio (str): Path to the input audio file.
        output_prefix (str): Prefix for the output file names.
        split_points_ms (list): List of split points in milliseconds.
    """
    audio = AudioSegment.from_file(input_audio)

    for i, split_point_ms in enumerate(split_points_ms):
        if i < len(split_points_ms) - 1:
            start_time_ms = split_point_ms
            end_time_ms = split_points_ms[i + 1]
            segment = audio[start_time_ms:end_time_ms]
            output_file = f"{output_prefix}_{i + 1}.mp3"
            segment.export(output_file, format="mp3")

def concatenate_audio(input_files, output_audio):
    """
    Concatenate multiple audio files into a single audio file.

    Args:
        input_files (list): List of paths to input audio files in the desired order.
        output_audio (str): Path to save the concatenated audio file.
    """
    audio_segments = [AudioSegment.from_file(file) for file in input_files]
    concatenated_audio = sum(audio_segments)
    concatenated_audio.export(output_audio, format="mp3")

def apply_fade_in(input_audio, output_audio, duration_ms):
    """
    Apply a fade-in effect to an audio file and save it to the output file.

    Args:
        input_audio (str): Path to the input audio file.
        output_audio (str): Path to save the faded audio file.
        duration_ms (int): Duration of the fade-in effect in milliseconds.
    """
    audio = AudioSegment.from_file(input_audio)
    faded_audio = audio.fade_in(duration_ms)
    faded_audio.export(output_audio, format="mp3")

def apply_fade_out(input_audio, output_audio, duration_ms):
    """
    Apply a fade-out effect to an audio file and save it to the output file.

    Args:
        input_audio (str): Path to the input audio file.
        output_audio (str): Path to save the faded audio file.
        duration_ms (int): Duration of the fade-out effect in milliseconds.
    """
    audio = AudioSegment.from_file(input_audio)
    faded_audio = audio.fade_out(duration_ms)
    faded_audio.export(output_audio, format="mp3")
