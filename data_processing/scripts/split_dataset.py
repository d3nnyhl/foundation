import pandas as pd
import numpy as np
import json

'''
Reads usable files from the path specified by input_path and splits the dataset into
train/test/val and writes in the path specified by the output_path.
'''

input_path = "/home/emilyh/composite_jsons/usable_micro_labeled_video_list.json"
output_path = "/home/manoj/train_test_val_splits/{}"
output_files = ["train.json", "valid.json", "test.json"]
TRAIN_PERCENT = 0.75
VALID_PERCENT = 0.85


def train_val_test_splits(df, train_percent, valid_percent):
	'''
	Splits the dataframe into train , val and test dataframes.
	'''
	train, val, test = np.split(df.sample(frac=1), \
					[int(train_percent*len(df)), int(valid_percent*len(df))])
	print("Train dataset size: ", train.shape)
	print("Val dataset size: ", val.shape)
	print("Test dataset size: ", test.shape)
	return [train, val, test]

def write_splits(df, train_percent, valid_percent):
	'''
	Calls train_val_test_splits() to split the dataframe and writes the splits 
        to the location as specified by the output path
	'''
	print("Creating train, val, test splits")
	splits = train_val_test_splits(df, train_percent, valid_percent)
	for i in range(0, 3):
		splits[i].to_json(output_path.format(output_files[i]), orient = 'records')


if __name__ == '__main__':
	df = pd.read_json(input_path, orient = 'records')
	write_splits(df, TRAIN_PERCENT, VALID_PERCENT)
	print("Completed writing files.")
