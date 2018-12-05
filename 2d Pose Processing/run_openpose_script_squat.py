import json
import os
import sys
import pdb
from glob import glob
import os.path as osp
import logging
from os import system


lift_type_list = []
video_dir = '/data0/Data/ig_raw/{}/{}.{}'
json_dir = '/data0/Data/composite_jsons/{}/{}'
outdir = '/data0/Results/openpose/{}/{}'
squat_dir = '/data0/Results/openpose/squat'
deadlift_dir = '/data0/Results/openpose/deadlift'
cleanandjerk_dir = '/data0/Results/openpose/cleanandjerk'
snatch_dir = '/data0/Results/openpose/snatch'
benchpress_dir = '/data0/Results/openpose/benchpress'
directories = {"squat": squat_dir,"deadlift": deadlift_dir, "cleanandjerk": cleanandjerk_dir, "snatch": snatch_dir, "benchpress": benchpress_dir}
splits = '/home/emilyh/train_test_val_splits'
input_liftype = False


command_input = sys.argv
if len(sys.argv) < 2:
        sys.exit("Please specify lift type by adding -[lift type] or -all to get all lift types")
else:
        command = sys.argv[1]
if command == "-squat":
        lift_type_list = ['squat']
        input_liftype = True
elif command == "-deadlift":
        lift_type_list = ['deadlift']
        input_liftype = True
elif command == "-cleanandjerk":
        lift_type_list = ['cleanandjerk']
        input_liftype = True
elif command == "-snatch":
        lift_type_list = ['snatch']
        input_liftype = True
elif command == "-benchpress":
        lift_type_list = ['benchpress']
        input_liftype = True
elif command == "-all":
        #temp
        lift_type_list = ['squat','deadlift','benchpress']
        #lift_type_list = ['squat','deadlift','cleanandjerk','snatch','benchpress']
        input_liftype = True
elif command == "-train" or "-test" or "-val":
        split_json = splits + "/" + command[1:] + ".json"
else:
        sys.exit("Command not recognized. Please choose from available lift types or choose -all for all lift types.")

# logic for customizable specification of which type to run
# Note: To run one specific type: add  -typename at the end of script command
#       To run all types: add  -all
if input_liftype == False:
    print(split_json)
    with open(split_json, 'r') as f:
        split_data = json.load(f)
    for object in split_data:
        filename = str(object["composite_json"])
        lift_type = str(object["macro"])
        lift_type_dir = directories[lift_type]
	lift_type_name_len = len(lift_type)
	json_path = json_dir.format(lift_type, filename)
        with open(json_path,'r') as f:
            json_data = json.load(f)
        video_path = video_dir.format(json_data['metadata']['folder'],
                                      json_data['metadata']['filename'],
                                      json_data['metadata']['extension'])
        save_path = outdir.format(lift_type,json_data['metadata']['filename'])
        # Check if the file already exists in the save_path folder
        # if the output folder does not contain this file
        entities = os.listdir(lift_type_dir)
        filename = os.path.basename(f.name)[:-5]
        print(filename)
        # This need to be adjusted for each lift type
        # e.g: filename = 19052734_116523725609494_8073158174120607744_n_squat
        filename = filename[:-(lift_type_name_len+1)]
        string = '/data0/Code/pose/openpose/build/examples/openpose/openpose.bin --video {} --write_video {}/'+ filename +'.avi --write_json {} --display 0'
        avi_save_path = lift_type_dir + "/videos"
        if not filename in entities:
                #system('/data0/Code/pose/openpose/build/examples/openpose/openpose.bin --video {} --write_video {}/result.avi --write_json {} --display 0'.format(video_path,save_path,save_path))
                system(string.format(video_path,avi_save_path,save_path))
else:
    for lift_type in lift_type_list:
        json_list = sorted(glob(json_dir.format(lift_type,'*.json')))
        lift_type_dir = directories[lift_type]
        lift_type_name_len = len(lift_type)
        for json_path in json_list[0:1000]:
            with open(json_path,'r') as f:
                json_data = json.load(f)
            video_path = video_dir.format(json_data['metadata']['folder'],
                                          json_data['metadata']['filename'],
                                          json_data['metadata']['extension'])
            save_path = outdir.format(lift_type,json_data['metadata']['filename'])
            # Check if the file already exists in the save_path folder
            # if the output folder does not contain this file
            entities = os.listdir(lift_type_dir)
            filename = os.path.basename(f.name)[:-5]
            print(filename)
            # This need to be adjusted for each lift type
            # e.g: filename = 19052734_116523725609494_8073158174120607744_n_squat
            filename = filename[:-(lift_type_name_len+1)]
            string = '/data0/Code/pose/openpose/build/examples/openpose/openpose.bin --video {} --write_video {}/'+ filename +'.avi --write_json {} --display 0'
            avi_save_path = lift_type_dir + "/videos"
            if not filename in entities:
                    #system('/data0/Code/pose/openpose/build/examples/openpose/openpose.bin --video {} --write_video {}/result.avi --write_json {} --display 0'.format(video_path,save_path,save_path))
                    system(string.format(video_path,avi_save_path,save_path))
            #if osp.isdir(outdir.format(json_data['metadata']['folder'],json_data['metadata']['filename'])):
            #    command('mkdir {}'format(outdir.format(json_data['metadata']['folder'],json_data['metadata']['filename'])))
	
