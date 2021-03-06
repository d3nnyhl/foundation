## Lift Classification

In the lift classification we used transfer learning where we started with a model that was already trained on Google’s ImageNet. We retrained the last layer of the neural network in order to classify the three lift types (Bench Press, Deadlift, Squat). We decided to use mobilenet architecture that has been trained on the ImageNet dataset as it is a small efficient convolutional neural network. We modified their retrain.py code which split the dataset for us and changed it to take our train, test, and validation data frames split instead. Near the end of the code, we also included a verbose/detailed results.json file to show all the predicted frames for each video. This is useful for future debugging purposes to understand why our model performs a particular way. 

We then trained our set of images/frames that has been extracted from the videos to teach the model about the new classes that we wanted it to recognize. The three classes are bench press, deadlift, and squat. We decided to use 0.01 learning rate for the classification, with 4000 iterations. The overall accuracy for all frames were 77% while the accuracy for classifying the videos were 80%. The method we used to classify the video is to find the max of the labels predicted. If most of the frames of a video were classified as bench press, then bench press is the winner. 

Portions of these codes are reproduced from work created and shared by Google and used according to terms described in the Apache 2.0 License.
Source: https://www.tensorflow.org/hub/tutorials/image_retraining

