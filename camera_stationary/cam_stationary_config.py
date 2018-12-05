#!/usr/bin/env python

from absl import flags
import sys
import platform

# Directories where data is located.
jsondirs = {'Jerk': '/home/heather/foundation/sandbox/data/{}{}.json',
            'Rugby': '/data0/Data/composite_jsons/{}/{}.json',
            'DennyHL-MBP.local': '/Users/dennyhl/Projects/dxf/dennyh/sandbox/data/composite_json/{}/{}.json'}

# Directories where images should be saved.
frame_save_dirs = {'Rugby': '/data1/Data/ig_raw/frames/{}/{}',
			'DennyHL-MBP.local': '/Users/dennyhl/Projects/dxf/dennyh/sandbox/data/ig_raw/frames/{}/{}'}


# Directories where videos are saved.
viddirs = {'Rugby': '/data0/Data/ig_raw/{}/{}',
'DennyHL-MBP.local': '/Users/dennyhl/Projects/dxf/dennyh/sandbox/data/ig_raw/{}/{}'}


# Directories where the results of stationary camera classification are stored.
# Used by StationaryCameraClassifier objects in stationary_camera_classifier.py
stationary_results_dir = {
	'Rugby': '/data0/Code/dxf/results',
	'DennyHL-MBP.local': '/Users/dennyhl/Projects/dxf/results'
}


# Gets the computer network name and saves the corresponding directories.
LIFT_TYPE_LIST = ['squat','benchpress','deadlift','snatch','cleanandjerk']
STATIONARY_CAM_CLASSIFIER_MODE = ['mean_consec', 'median_diff']
JSON_DIR = jsondirs.get(platform.node()) or ''
FRAMES_SAVE_DIR = frame_save_dirs.get(platform.node()) or ''
VID_DIR = viddirs.get(platform.node()) or ''
STATIONARY_RESULTS_DIR = stationary_results_dir.get(platform.node()) or ''

# Flags to access from the config file.
flags.DEFINE_string('json_dir', JSON_DIR, 'Where composite JSON files are stored')
flags.DEFINE_string('frames_save_dir', FRAMES_SAVE_DIR, 'Where to save extracted frames')
flags.DEFINE_string('vid_dir', VID_DIR, 'Where ig_raw videos are located')
flags.DEFINE_string('stationary_results_dir', STATIONARY_RESULTS_DIR, 'Where the stationary camera classification results are stored')
flags.DEFINE_list('lift_type_list', LIFT_TYPE_LIST, 'Available macro lift types')
flags.DEFINE_list('stationary_cam_classify_mode', STATIONARY_CAM_CLASSIFIER_MODE, 'Available classification modes for stationary camera')

def get_config():
	config = flags.FLAGS
	config(sys.argv)
	return config