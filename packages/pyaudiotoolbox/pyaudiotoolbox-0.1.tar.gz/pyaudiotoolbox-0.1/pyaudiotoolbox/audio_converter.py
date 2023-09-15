from pydub import AudioSegment

def convert_audio(input_path, output_path, output_format):
    """
    Convert an audio file to a specified format and save it to the output path.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Path to save the output audio file.
        output_format (str): Desired output format (e.g., "mp3", "wav", "ogg", "flac").
    """
    # Load the input audio file
    audio = AudioSegment.from_file(input_path)
    
    # Export the audio to the specified format and save to the output path
    audio.export(output_path, format=output_format)

def batch_convert_audio(input_dir, output_dir, output_format):
    """
    Batch convert audio files in a directory to a specified format and save them to the output directory.

    Args:
        input_dir (str): Path to the directory containing input audio files.
        output_dir (str): Path to save the output audio files.
        output_format (str): Desired output format (e.g., "mp3", "wav", "ogg", "flac").
    """
    import os

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Loop through input files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith((".mp3", ".wav", ".ogg", ".flac")):
            input_path = os.path.join(input_dir, filename)
            output_filename = f"{os.path.splitext(filename)[0]}.{output_format}"
            output_path = os.path.join(output_dir, output_filename)

            # Convert and save the audio file
            convert_audio(input_path, output_path, output_format)
