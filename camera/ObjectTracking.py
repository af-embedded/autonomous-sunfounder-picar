import os
import cv2
import numpy as np
import imutils

device = cv2.VideoCapture(0)

while True:
    ret, frame = device.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    l_range = np.array([110,50,50])
    u_range = np.array([130,255,255])

    mask = cv2.inRange(hsv,l_range,u_range)
    final = cv2.bitwise_and(frame,frame,mask=mask)

    cnts =  cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x,y), radius) = cv2.minEnclosingCircle(c)
        #M= cv2.moments(c)
        #center = (int(M["m10"]/M["m00"]), (M["m01"]/M["m00"]))

        if radius > 10:
            cv2.circle(frame,(int(x),int(y)),int(radius), (0, 255, 255), 2)
            #cv2.circle(frame, center,5,(0,0,255), -1)

    if cv2.waitKey(1) == 27:
        break
    cv2.imshow("image", frame)
device.release()
cv2.destroyAllWindows()
