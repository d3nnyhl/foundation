import json
import os
import glob as glob
import os
import sys
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from scipy import signal
from scipy.signal import find_peaks

class RepMatchedFilter:

	def __init__(self, templates_json_path):
		self.openpose_res_folder = '/Users/dennyhl/Projects/dxf/dennyh/sandbox/data/openpose/{}/{}'
		self.templates_json_path = templates_json_path
		self.interesting_keypoint_index = {
			'squat': [13, 22, 28, 37],
			'deadlift': [13, 22],
			'benchpress': [10, 13, 19, 22] # Elbows and Wrists.
		}
		self.load_templates()

		self.thresholds = {

		}

	def load_templates(self):
		with open(self.templates_json_path, 'r') as file:
			self.templates = json.load(file)
			

	def get_signal(self, keypoint_index, path):
		list_jsons = sorted(glob.glob('{}/*.json'.format(path)))
		arr = []
		cnt = 0
		for jso in list_jsons[230: 400]:
			with open(jso) as f:
				data = json.load(f)
				if cnt % 5 == 0:
					if data['people']:
						arr.append(data['people'][0]['pose_keypoints_2d'][keypoint_index])
					else:
						arr.append(arr[-1])
			cnt += 1

		mean = np.mean(arr)
		std = np.std(arr)
		for i, val in enumerate(arr):
			if (val - mean) / std < -2:
				if i > 0 and i < len(arr) - 2:
					arr[i] = (arr[i - 1] + arr[i + 1]) / 2
				elif i == 0:
					arr[i] = arr[1]
				else:
					arr[i] = arr[-2]

		
		# Normalize the data.
		minimum = min(arr)
		maximum = max(arr)
		print(minimum, maximum)
		
		arr = [(x - minimum) / (maximum - minimum) for x in arr]
		self.plot_signal([i for i in range(len(arr))], arr)
		return arr

	def get_template_signal(self, lift_type, keypoint_index, view=None, reversed=False):
		'''
		This only works for this particular template, which has a repetition between frames 25 - 126.
		Need to generalize for all templates.

		'''
		default_view = {
			'squat': 'right',
			'deadlift': 'front',
			'benchpress': 'right'
		}

		if not view:
			view = default_view[lift_type]
		template = self.templates[lift_type][view]


		template_folder = self.openpose_res_folder.format(template['folder'], template['filename'])

		template_jsons = sorted(glob.glob('{}/*.json'.format(template_folder)))
		tmp = []
		cnt = 0
		for jso in template_jsons[template['start_frame']: template['end_frame']]:
			with open(jso) as f:
				data = json.load(f)
				if cnt % 5 == 0:
					if data['people']:
						tmp.append(data['people'][0]['pose_keypoints_2d'][keypoint_index])
					else:
						tmp.append(tmp[-1])
				cnt += 1

		mean = np.mean(tmp)
		std = np.std(tmp)

		for i, val in enumerate(tmp):
			if (val - mean) / std < -2:
				if i > 0 and i < len(tmp) - 2:
					tmp[i] = (tmp[i - 1] + tmp[i + 1]) / 2
				elif i == 0:
					tmp[i] = tmp[1]
				else:
					tmp[i] = tmp[-2]

		minimum = min(tmp)
		maximum = max(tmp)


		tmp = [(x - minimum) / (maximum - minimum) for x in tmp]
		self.plot_signal([i for i in range(len(tmp))], tmp)
		if reversed:
			return tmp[::-1]
		return tmp

	def apply_filter(self, lift_type, filename, keypoint_index):

		path = self.openpose_res_folder.format(lift_type, filename)

		kpts = self.get_signal(keypoint_index, path)

		
		tmp_signal = self.get_template_signal(lift_type, 
			keypoint_index, view='front2')

		# lfi = signal.lfilter(tmp_signal, 1, kpts)
		lfi = np.correlate(tmp_signal, kpts, mode='same')
		lfi = lfi * lfi

		markerline, stemlines, baseline = plt.stem([i * 5 for i in range(len(lfi))], lfi, '-.')
		plt.show()

		peaks = signal.find_peaks(lfi, 0, 0.005)
		print([i * 5 for i in peaks[0]])

	def plot_signal(self, x, y):
		markerline, stemlines, baseline = plt.stem(x, y, '-.')
		plt.show()

	def prepare_eval(self, labels):
		
	def eval(self):
		pass 



rmf = RepMatchedFilter('./templates.txt')

rmf.apply_filter('squat', '35569936_185584258805289_2302590439070367744_n', 25)