import cv2
import numpy as np
import pdb
import json
from timeit import default_timer as timer
import os, sys
import glob
from extract_frames import FrameExtractor
from cam_stationary_config import get_config

def get_camera_stationary_frame_difference_skeleton(threshold, sampling_rate): 
    """
    Returns JSON object to be written to file.
    """
    return {
        'result': [],
        'hyperparameters': {
            'threshold': threshold,
            'sampling_rate': sampling_rate
        }
    }

def get_result_json(filename, folder, score, threshold):
    """
    Returns JSON that goes inside the 'result' array.
    """
    assert(isinstance(filename, str))
    assert(isinstance(folder, str))
    assert(isinstance(score, float))
    assert(isinstance(threshold, float))
    
    return {
        'filename': filename,
        'folder': folder,
        'score': score,
        'decision': 1 if score <= threshold else 0
    }


class StationaryCameraClassifier:
    def __init__(self, step_size, threshold):
        config = get_config()
        # Folder that will contain the results of the classification
        self.output_folder = config.stationary_results_dir
        
        self.threshold = threshold
        # List of heuristic modes.
        self.modes = config.stationary_cam_classify_mode

        self.frame_list = []
        self.results = []
        self.current_index = 0
        self.step_size = step_size

    def get_next_frame(self):
        im = cv2.imread(self.frame_list[self.current_index], 0)
        self.current_index += self.step_size
        return im

    def update_threshold(self, threshold):
        self.threshold = threshold

    def reset_index(self):
        self.current_index = 0

    def update_step_size(self, step_size):
        self.step_size = step_size
                
    def diffImg(self, t0, t1, t2):
        d1 = cv2.absdiff(t2, t1)
        d2 = cv2.absdiff(t1, t0)
        return cv2.bitwise_and(d1, d2)

    def avg_diff_img(self, n, curr_avg, new_data):
        '''
        Return running average of the video.
        '''
        return (n - 1) / n * curr_avg + new_data / n

    def mean_of_bitwise_and_of_consecutive_frames(self, frames_dir):
        self.frame_list = sorted(glob.glob('{}/*.jpg'.format(frames_dir)))
        t_minus = self.get_next_frame()
        t = self.get_next_frame()
        t_plus = self.get_next_frame()
        arithmetic_avg = 0.0
        processed = False

        if not (t_minus is None or t is None or t_plus is None):
            processed = True
            n = 1.0
            while self.current_index + self.step_size < len(self.frame_list):
                diff_img = self.diffImg(t_minus, t, t_plus)
                arithmetic_avg = self.avg_diff_img(n, arithmetic_avg, np.mean(diff_img))
                n += 1.0
                t_minus, t, t_plus = t, t_plus, self.get_next_frame()
                if t_plus is None:
                    break
        if processed:
            return arithmetic_avg
        else:
            return -1

    def median_frame_diff(self, frames_dir):
        # Get all frames from frames_dir
        self.frame_list = sorted(glob.glob('{}/*.jpg'.format(frames_dir)))

        frames = [] # Store samples.
        while self.current_index + self.step_size < len(self.frame_list):
            frames.append(self.get_next_frame())

        median_frame = np.median(frames, axis=0).astype(dtype=np.uint8) 

        median_diff_mtx = np.zeros(median_frame.shape)
        for frame in frames:
            median_diff_mtx = np.add(median_diff_mtx, cv2.absdiff(frame, median_frame))
        return np.mean(median_diff_mtx)

    def get_classifier_function(self, mode=0):
        classifier_fn = None
        if mode == 0:
            classifier_fn = self.mean_of_bitwise_and_of_consecutive_frames
        elif mode == 1:
            classifier_fn = self.median_frame_diff
        else:
            print('Invalid mode entered. Use: \
                    \n 0 for mean of difference between consecutive frames\n \
                    1 for median difference')
        return classifier_fn

    def write_results(self):
        with open('{}/{}_{}_{}.json'.format(self.output_folder, self.modes[mode], \
                                 self.threshold, self.step_size), 'w+') as file:
            out_json = get_camera_stationary_frame_difference_skeleton(self.threshold, self.step_size)
            out_json['result'] = self.results
            json.dump(out_json, file)
        self.results = []


def classify_stationary_camera(step_size, threshold, mode=0):
    """
    Classifies each video in the `composite_json` folder.
    @type  step_size: int
    @param step_size: Sample rate.
    @type  threshold: float
    @param threshold: Maximum value for videos with stationary cameras.

    @rtype:   boolean
    @return:  True if successful, False otherwise

    """
    scc = StationaryCameraClassifier(step_size, threshold)
    fr = FrameExtractor()

    classifier_fn = scc.get_classifier_function(mode)

    if not classifier_fn:
        return False

    if len(sys.argv) > 2:
        lift_type_list = sys.argv[2:]
    else:
        lift_type_list = fr.lift_type_list

    for lt in lift_type_list:
        json_filenames = fr.get_composite_json_filenames(lt)

        for filename in json_filenames:
    
            video_metadata = fr.get_video_metadata(filename)
            frames_dir = fr.images_dir.format(video_metadata['folder'], video_metadata['filename'])

            start_time = timer()
            score = classifier_fn(frames_dir)
            end_time = timer()

            scc.reset_index()
            scc.frame_list = []

            print('Done processing {}\nTime elapsed: {:.2f}s'.format(video_metadata['filename'], end_time - start_time))
            print('Score:', score)
            result = get_result_json(video_metadata['filename'], video_metadata['folder'], score, scc.threshold)

            scc.results.append(result)

    scc.write_results()
    return True

            
if __name__ == "__main__":
    mode = 0
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if not mode.isdigit():
            print('1st argument must be a non-negative integer: heuristic mode {0, 1}')
            exit(-1)
        else:
            mode = int(mode)
    # Hyperparameters.
    # Default Hyperparameters
    step_size = 1
    threshold = 1.2
    if mode == 1:
        step_size = 3
        threshold = 7000.0
    classify_stationary_camera(step_size, threshold, int(mode))
