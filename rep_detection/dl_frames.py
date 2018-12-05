ssh_command = 'rugby' ### Change this to whatever command you use to ssh to rugby.
input_file = './frames1.txt' ### Put name of the given .txt file with the frames to be downloaded.
output_folder = './tmp' ### Make a directory where frames will be stored and rename this string.

import os 

with open(input_file, 'r') as f:
	files = f.read().splitlines() 

	for file in files:
		cmd = 'scp -r {}:{} {}'.format(ssh_command, file, output_folder)
		os.system(cmd)
