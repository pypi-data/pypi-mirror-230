import cv2
import os
import json

class Frame2Vid:
    def __init__(self, input_folder, output_file, format='mp4'):
        """
        Initialize the Frame2Vid class.

        :param input_folder: Path to the folder containing the frames.
        :param output_file: Path where the output video should be saved.
        :param format: Output video format, default is 'mp4'.
        """
        self.input_folder = input_folder
        self.output_file = output_file
        self.format = format
        self.framerate = self._load_framerate()

    def _load_framerate(self):
        """
        Load the framerate from the metadata.json file.

        :return: framerate
        """
        try:
            with open(os.path.join(self.input_folder, 'metadata.json'), 'r') as f:
                metadata = json.load(f)
            return metadata['framerate']
        except FileNotFoundError:
            raise FileNotFoundError("metadata.json not found in the input folder.")
        except KeyError:
            raise KeyError("Framerate not found in metadata.json")

    def create_video(self):
        """
        Create a video from frames in the input folder.
        """
        # Define the codec
        if self.format == 'mp4':
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        elif self.format == 'mkv':
            fourcc = cv2.VideoWriter_fourcc(*'mkv1')

        # Initialize video writer
        out = cv2.VideoWriter(self.output_file, fourcc, self.framerate, (640, 480))

        for frame_name in sorted(os.listdir(self.input_folder)):
            if frame_name.endswith('.jpg'):
                frame = cv2.imread(os.path.join(self.input_folder, frame_name))
                out.write(frame)

        out.release()
