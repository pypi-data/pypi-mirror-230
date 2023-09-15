# PyAudioToolBox

PyAudioToolBox is a Python library for audio format conversion and manipulation.

## Installation

You can install PyAudioToolBox using pip:

```bash
pip install pyaudiotoolbox
```

## Usage

### Audio Format Conversion

To convert an audio file to a different format, use the convert_audio function:

```python
from pyaudiotoolbox.audio_converter import convert_audio

input_file = 'input.wav'
output_file = 'output.mp3'
output_format = 'mp3'

convert_audio(input_file, output_file, output_format)
```

### Batch Conversion

To perform batch audio format conversion, use the batch_convert_audio function:

```python
from pyaudiotoolbox.audio_converter import batch_convert_audio

input_directory = 'input_folder'
output_directory = 'output_folder'
output_format = 'ogg'

batch_convert_audio(input_directory, output_directory, output_format)

```

### Audio Extraction

To extract audio from a video file, use the `extract_audio` function:

```python
from pyaudiotoolbox.audio_extractor import extract_audio

input_video = 'input.mp4'
output_audio = 'output.wav'

# Extract audio from the video
extract_audio(input_video, output_audio)
```
### Audio Trimming

Trim an audio file to a specified duration and save the trimmed portion to an output file.

- `input_audio` (str): Path to the input audio file.
- `output_audio` (str): Path to save the trimmed audio file.
- `start_time_ms` (int): Start time in milliseconds for the trim.
- `end_time_ms` (int): End time in milliseconds for the trim.

```python
from pyaudiotoolbox.audio_editor import trim_audio

# Trim audio from 10 seconds to 30 seconds
- `input_audio` = "input.mp3"
- `output_audio` = "trimmed_output.mp3"
- `start_time_ms` = 10000  # 10 seconds
- `end_time_ms` = 30000    # 30 seconds

trim_audio(input_audio, output_audio, start_time_ms, end_time_ms)
```
### Audio Splitting

Split an audio file into multiple segments at specified split points and save each segment to separate files.

- `input_audio` (str): Path to the input audio file.
- `output_prefix` (str): Prefix for the output file names.
- `split_points_ms` (list): List of split points in milliseconds.

```python
from pyaudiotoolbox.audio_editor import split_audio

# Split audio into segments at 10 seconds and 20 seconds
input_audio = "input.mp3"
output_prefix = "segment"
split_points_ms = [10000, 20000]

split_audio(input_audio, output_prefix, split_points_ms)
```
### Concatenate audio

Concatenate multiple audio files into a single audio file.

- `input_files` (list): List of paths to input audio files in the desired order.
- `output_audio` (str): Path to save the concatenated audio file.

```python
from pyaudiotoolbox.audio_editor import concatenate_audio

# Concatenate two audio files into one
input_files = ["file1.mp3", "file2.mp3"]
output_audio = "concatenated_output.mp3"

concatenate_audio(input_files, output_audio)
```

### Apply fade in to audio

Apply a fade-in effect to an audio file and save it to the output file.

- `input_audio` (str): Path to the input audio file.
- `output_audio` (str): Path to save the faded audio file.
- `fade_duration_ms` (int): Duration of the fade-in effect in milliseconds.

```python
from pyaudiotoolbox.audio_editor import apply_fade_in

# Apply a 3-second fade-in effect to an audio file
input_audio = "input.mp3"
output_audio = "faded_intput.mp3"
fade_duration_ms = 3000  # 3 seconds

apply_fade_in(input_audio, output_audio, fade_duration_ms)
```

### Apply fade out to audio

Apply a fade-out effect to an audio file and save it to the output file.

- `input_audio` (str): Path to the input audio file.
- `output_audio` (str): Path to save the faded audio file.
- `fade_duration_ms` (int): Duration of the fade-out effect in milliseconds.

```python
from pyaudiotoolbox.audio_editor import apply_fade_out

# Apply a 2-second fade-out effect to an audio file
input_audio = "input.mp3"
output_audio = "faded_output.mp3"
fade_duration_ms = 2000  # 2 seconds

apply_fade_out(input_audio, output_audio, fade_duration_ms)
```

### Normalize audio volume

You can use this function to normalize the volume of an audio file by specifying the input audio file path and the target volume level in dBFS.

```python
input_audio_file = 'input.mp3'
target_volume_level = -15  # Set your target volume level in dBFS

normalized_audio = normalize_audio(input_audio_file, target_volume_level)

# Export the normalized audio to a new file
normalized_audio.export('output_normalized_audio.mp3', format='mp3')
```