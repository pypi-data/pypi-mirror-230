import unittest
import os
from unittest.mock import Mock, patch
from pyaudiotoolbox.audio_converter import convert_audio, batch_convert_audio

class TestAudioConverter(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_input_dir = 'tests/test_input'
        self.test_output_dir = 'tests/test_output'
        os.makedirs(self.test_input_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary directory after testing
        for root, dirs, files in os.walk(self.test_input_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        for root, dirs, files in os.walk(self.test_output_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(self.test_input_dir)
        os.rmdir(self.test_output_dir)

    @patch('pydub.AudioSegment.from_file')
    @patch('pydub.AudioSegment.export')
    def test_convert_audio(self, mock_export, mock_from_file):
        # Mock the pydub AudioSegment and export methods
        mock_audio = Mock()
        mock_export.return_value = None
        mock_from_file.return_value = mock_audio

        input_audio = os.path.abspath('tests/test_input/input.wav')
        output_audio = os.path.join(self.test_output_dir, 'output.mp3')
        output_format = 'mp3'

        # Test the convert_audio function
        convert_audio(input_audio, output_audio, output_format)

        # Assert that the export method was called
        mock_audio.export.assert_called_with(output_audio, format=output_format)

    @patch('os.makedirs', return_value=None)
    @patch('os.listdir')
    @patch('pydub.AudioSegment.from_file')
    @patch('pydub.AudioSegment.export')
    def test_batch_convert_audio(self, mock_export, mock_from_file, mock_listdir, mock_makedirs):
        # Mock the os.listdir function to return a list of test input files
        mock_listdir.return_value = ['input1.mp3', 'input2.wav', 'input3.flac']

        # Mock the pydub AudioSegment and export methods
        mock_audio = Mock()
        mock_export.return_value = None
        mock_from_file.return_value = mock_audio

        output_format = 'ogg'

        # Test the batch_convert_audio function
        batch_convert_audio(self.test_input_dir, self.test_output_dir, output_format)

        # Assert that the export method was called for each input file
        expected_output_files = [
            os.path.join(self.test_output_dir, 'input1.ogg'),
            os.path.join(self.test_output_dir, 'input2.ogg'),
            os.path.join(self.test_output_dir, 'input3.ogg'),
        ]
        for output_file in expected_output_files:
            mock_audio.export.assert_any_call(output_file, format=output_format)

if __name__ == '__main__':
    unittest.main()
