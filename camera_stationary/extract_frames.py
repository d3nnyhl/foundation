import os, sys
import platform
import glob
import json
from cam_stationary_config import get_config

def read_json(filename):
	"""
	Reads filename and returns content as JSON.
	Assumes correctly formatted JSON file.
	"""
	with open(filename, 'r') as file:
		data = json.load(file)
	return data

class FrameExtractor:
	def __init__(self):
		# Configure the paths were composite JSONs, videos, and destination folders 
		# are/will be located.
		config = get_config()

		self.lift_type_list = config.lift_type_list
		self.json_dir = config.json_dir
		self.vid_dir = config.vid_dir
		self.images_dir = config.frames_save_dir
		self.composite_json_filename = {}
		for lt in self.lift_type_list:
			self.composite_json_filename[lt] = self.json_dir.format(lt, '{}')

	def get_composite_json_filenames(self, lt):
		"""
		Returns a list of composite JSON filenames located in the folder corresponding
		to the `lt` lift-type.
		"""
		if lt not in self.composite_json_filename:
			return []
		return glob.glob(self.composite_json_filename[lt].format('*'))

	def get_video_metadata(self, json_filename):
		json_content = read_json(json_filename)
		return {
			'folder': json_content['metadata']['folder'],
			'filename': json_content['metadata']['filename'],
			'extension': json_content['metadata']['extension']
		}

	def extract_frames(self, video_filename, frames_dir):
		"""
		Uses ffmpeg to extract frames given a video.
		If frames do not exist for the specific video, we make a new directory to store its frames.
		"""
		if not os.path.exists(frames_dir):
			os.makedirs(frames_dir)
			os.system('ffmpeg -i {} -vsync vfr -qscale:v 2 {}/%04d.jpg'.format(video_filename, frames_dir))
			self.frame_list = sorted(glob.glob('{}/*.jpg'.format(frames_dir)))
		else:
			print('Frames already extracted for {}'.format(video_filename.split('/')[-1]))

def extract_frames():
	fr = FrameExtractor()
	if len(sys.argv) > 1:
		lift_type_list = sys.argv[1:]
	else:
		lift_type_list = fr.lift_type_list

	for lt in lift_type_list:
		json_filenames = fr.get_composite_json_filenames(lt)

		for filename in json_filenames:
			# Get map containing {'folder', 'filename', 'extension'} of the video.
			video_metadata = fr.get_video_metadata(filename)
			# Get video filename i.e. 37086037_2057206874527075_8306873058665168896_n.mp4
			video_filename = '{}.{}'.format(video_metadata['filename'], video_metadata['extension'])
			video_full_path = fr.vid_dir.format(video_metadata['folder'], video_filename)
			print('Now extracting frames for {}'.format(video_filename))
			# Get path to directory where frames will be saved.
			frames_dir = fr.images_dir.format(video_metadata['folder'], video_metadata['filename'])
			# Extract frames from video at VID_PATH and save them in frames_dir
			fr.extract_frames(video_full_path, frames_dir)


if __name__ == "__main__":
	extract_frames()
