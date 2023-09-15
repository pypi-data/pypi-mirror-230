from moviepy.editor import VideoFileClip

def extract_audio(input_video, output_audio, audio_stream=None):
    """
    Extract audio from a video file and save it as a standalone audio file.

    Args:
        input_video (str): Path to the input video file.
        output_audio (str): Path to save the output audio file.
        audio_stream (int, optional): Index of the audio stream to extract (useful for videos with multiple audio streams).
    """
    video_clip = VideoFileClip(input_video)
    
    if audio_stream is not None:
        # Select a specific audio stream if specified
        audio_clip = video_clip.audio.subclip()
    else:
        # Use the default audio stream
        audio_clip = video_clip.audio

    audio_clip.write_audiofile(output_audio, codec='pcm_s16le')

