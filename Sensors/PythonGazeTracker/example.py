"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
import time
from gaze_tracking import GazeTracking


# ADHD Zoned out detection vars
frametime = 0.1 # How long between each frame (in sec)
distractCounter = 0 # Counts how many consecutive frames eyes havent moved +- 4px
frameCounter = 0 # Counts frames, reset on threshhold or distraction
lookThreshold = 6 # How many pixels do eyes have to move for it to count as moving (1-3 px too small)
zonedOutThreshhold = 20 # How many consecutive frames count as being 'zoned out' ?
currLx, currLy = 0, 0 # eye position trackers
currRx, currRy = 0, 0

camNum = 9 # CamNum set by making a virtual cam via v4l2loopback
gaze = GazeTracking()
webcam = cv2.VideoCapture(camNum)

while True:
    # We get a new frame from the webcam
    
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking(): text = "Blinking"
    elif gaze.is_right(): text = "Looking right"
    elif gaze.is_left(): text = "Looking left"
    elif gaze.is_center(): text = "Looking center"

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    #print("left side: "+str(left_pupil))
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    #print("right side: "+str(right_pupil))


    #Calculating the left side & right side
    if(str(left_pupil) != "None" and str(right_pupil) != "None"):
        leftx, lefty= str(left_pupil).split(",")
        rightx, righty = str(right_pupil).split(",")
        leftx = int(leftx[1:])
        lefty = int(lefty[:-1])
        rightx= int(rightx[1:])
        righty= int(righty[:-1])


        ### ADHD Zoned out detection
        time.sleep(frametime)
        # Increment count if eyes havent moved, else reset
        frameCounter += 1 # Increment frame (always) and distract (if eyes havent moved, else reset)
        distractCounter = distractCounter + 1 if((leftx-lookThreshold<currLx<leftx+lookThreshold) and (lefty-lookThreshold<currLy<lefty+lookThreshold)) else 0

        # Update eye positions
        currLx, currLy = leftx, lefty
        currRx, currRy = rightx, righty

        if frameCounter >= zonedOutThreshhold: # Reach threshold: print status
            frameCounter = 0 # Reset frameCounter
            if distractCounter >= zonedOutThreshhold:
                print("GazeTracker: The user is zoned out", flush=True)
                distractCounter = 0
            else: print("GazeTracker: The user is focused", flush=True)

    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27: break
   
webcam.release()
cv2.destroyAllWindows()
