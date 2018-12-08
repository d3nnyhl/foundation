## Stationary Camera "Classifier"

The `camera_stationary` module has the goal of classifying a video into stationary camera or moving camera based on different heuristics. After setting a threshold for each mode, if the video gets a score lower than the threshold, it's classified as `stationary`, otherwise, it is `moving`. 

### Frames Extraction

Since we eventually need to sample every video, it is computationally more efficient to extract frames from every video that has a corresponding `composite_json` once, and save it in secondary storage. This way, whenever we run some sort of classification algorithm, we simply need to read the images, rather than sample from the video over and over.

In `Rugby`, the frames of each video will be stored in the directory `/data1/Data/ig_raw/frames/lift_type/video_name`. For example, for a `deadlift` video corresponding to the name `111_n.mp4`, the frames of this video will be stored in `/data1/Data/ig_raw/frames/deadlift/111_n`. Each frame will be in `.jpg` format and have a filename that is always a number (which is monotonically increasing). So frame `0001.jpg` occurs earlier in the video than `0003.jpg`.

### Classification

Two modes of classification were implemented.

* Take the bitwise-AND of the difference in pixel values in consecutive frames. Find the mean value across the whole image. 
* Find the median frame (pixel values) of the whole video. Subtract each frame from the median frame.

