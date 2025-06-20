"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
import time
from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
count = 0
currLx, currLy = 0, 0
currRx, currRy = 0, 0
while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    print("left side: "+str(left_pupil))
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    print("right side: "+str(right_pupil))


    #Calculating the left side & right side
    if(str(left_pupil) != "None" and str(right_pupil) != "None"):
        leftx, lefty= str(left_pupil).split(",")
        rightx, righty = str(right_pupil).split(",")
        leftx = int(leftx[1:])
        lefty = int(lefty[:-1])
        rightx= int(rightx[1:])
        righty= int(righty[:-1])

        if((leftx-4<currLx<leftx+4) and (lefty-4<currLy<lefty+4) and (rightx-4<currRx<rightx+4) and (righty-4<currRy<righty+4)):
            count +=1
        else:
            count =0
            currLx, currLy = leftx, lefty
            currRx, currRy = rightx, righty

        if(count==10):
            print("The user is zoned out")
            time.sleep(5)




    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break
   
webcam.release()
cv2.destroyAllWindows()
