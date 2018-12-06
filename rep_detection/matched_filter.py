import json
import os
import glob as glob
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from scipy import signal
from scipy.signal import find_peaks

class RepMatchedFilter:

    def __init__(self, templates_json_path):
        self.results = {}
        self.openpose_res_folder = '/data0/Results/lifting_openpose/{}/{}'
        self.templates_json_path = templates_json_path
        self.load_templates()
        self.thresholds = {
            'deadlift': 0.7,
            'squat': 0.7,
            'benchpress': 0.7
        }

    def load_templates(self):
        with open(self.templates_json_path, 'r') as file:
            self.templates = json.load(file)
            

    def get_signal(self, keypoint_index, path, lift_type, plot=True):
        list_jsons = sorted(glob.glob('{}/*.json'.format(path)))
        arr = []
        window = []
        cnt = 0
        for jso in list_jsons:
            with open(jso) as f:
                data = json.load(f)
                if data['people']:
                    window.append(data['people'][0]['pose_keypoints_2d'][keypoint_index])
                if cnt % 5 == 0:
                    arr.append(np.mean(window))
                    window = []
            cnt += 1
            
        mean = np.mean(arr)
        std = np.std(arr)

        for i, val in enumerate(arr):
            if (val - mean) / std < -2 or (val - mean) / std > 2:
                if i > 0 and i < len(arr) - 2:
                    arr[i] = (arr[i - 1] + arr[i + 1]) / 2
                elif i == 0:
                    arr[i] = arr[1]
                else:
                    arr[i] = arr[-2]

        
        # Normalize the data.
        if not arr:
            return arr
        
        minimum = min(arr)
        maximum = max(arr)
        
        arr = [(x - minimum) / (maximum - minimum) for x in arr]
        
        if plot:
            self.plot_signal([i * 5 for i in range(len(arr))], arr, lift_type)
        
        return arr

    def get_template_signal(self, lift_type, keypoint_index, plot=False, view=None, reversed=False):
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
        if plot:
            self.plot_signal([i * 5 for i in range(len(tmp))], tmp, lift_type)
        if reversed:
            return tmp[::-1]
        return tmp

    def apply_filter(self, lift_type, filename, keypoint_index, use_template=False, plot=True):
        
        if filename in self.results:
            return self.results[filename]

        path = self.openpose_res_folder.format(lift_type, filename)

        kpts = self.get_signal(keypoint_index, path, lift_type, plot=plot)
        
        signal_len = len(glob.glob('{}/*.json'.format(path)))

        if not use_template:
            peaks = signal.find_peaks(kpts, self.thresholds[lift_type], 0.0001)
            peaks = [i * 5 for i in peaks[0]]

            reps = self.get_rep_frames(signal_len, peaks)
            
            self.results[filename] = reps
            return reps
        else:
            tmp_signal = self.get_template_signal(lift_type, 
                keypoint_index, plot, view='back')

            lfi = np.correlate(tmp_signal, kpts, mode='same')
            lfi = lfi * lfi

            peaks = signal.find_peaks(lfi, 0, 0.001)
            peaks = [i * 5 for i in peaks[0]]
            reps = self.get_rep_frames(signal_len, peaks)
            self.results[filename] = reps
            return reps
    

    def get_rep_frames(self, signal_len, peaks):
        if len(peaks) == 1:
            if peaks[0] < signal_len // 2:
                return [{'start': 0, 'mid': int(peaks[0]), 'end': 2* int(peaks[0])}]
            return [{'start': int(peaks[0]) - int(signal_len - peaks[0]), 'mid': int(peaks[0]), 'end': signal_len}]
        
        reps = [{} for i in range(len(peaks))]
                    
        for i in range(len(peaks)):
            reps[i]['mid'] = int(peaks[i])
            if i == len(peaks) - 1:
                start = peaks[i - 1] + (peaks[i] - peaks[i - 1]) // 2
                end = min(signal_len, peaks[i] + (peaks[i] - start))
                reps[i]['start'] = int(start)
                reps[i]['end'] = int(end)
            elif i == 0:
                end = peaks[i] + (peaks[i + 1] - peaks[i]) // 2
                start = max(0, peaks[i] - (end - peaks[i]))
                reps[i]['start'] = int(start)
                reps[i]['end'] = int(end)
            else:        
                reps[i]['start'] = int(peaks[i - 1] + (peaks[i] - peaks[i - 1]) // 2)
                reps[i]['end'] = int(peaks[i] + (peaks[i + 1] - peaks[i]) // 2)
            
        filtered_reps = []
        for rep in reps:
            if rep['end'] - rep['start'] > 40:
                filtered_reps.append(rep)
                
        return filtered_reps
            
    def plot_signal(self, x, y, lt):
        keypoint_name = 'Mid-Hip'
        if lt == 'squat':
            keypoint_name = 'Mid-Hip'
        elif lt == 'deadlift':
            keypoint_name = 'Left Shoulder'
        elif lt == 'benchpress':
            keypoint_name = 'Wrist'
        plt.figure(figsize=(20,12))
        markerline, stemlines, baseline = plt.stem(x, y, '-.')
        plt.title('{} Relative Location vs Frame Number'.format(keypoint_name))
        plt.xlabel('Frame Number')
        plt.ylabel('{} Location'.format(keypoint_name))
        plt.show()