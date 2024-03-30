import cv2
import numpy as np
import time
import os
import tracker as htm

folderPath = "Header"
myList = os.listdir(folderPath)
#print(myList)
overlayList = []
for inPath in myList:
    image = cv2.imread(f'{folderPath}/{inPath}')
    overlayList.append(image)
#print(len(overlayList))

header = overlayList[0]
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.HandDetector(detectionCon=0.85)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmlist = detector.findPosition(img, draw=False)
    if len(lmlist) != 0:
        #print(lmlist)
        x1, y1 = lmlist[8][1:]
        x2, y2 = lmlist[12][1:]
    
    fingers = detector.fingersUp()
    #print(fingers)

    if len(fingers) >= 3:
        if fingers[1] and fingers[2]:
            cv2.rectangle(img, (x1, y1-25), (x2, y2+25), (255, 0, 255), cv2.FILLED)
            print("Selection Mode")
            if y1 < 125:
                if 250 < x1 < 450:
                    header = overlayList[0]
                elif 550 < x1 < 750:
                    header = overlayList[1]
                elif 800 < x1 < 950:
                    header = overlayList[2]
                elif 1050 < x1 < 1200:
                    header = overlayList[3]

    if len(fingers) >= 2:
        if fingers[1] and not fingers[2]:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            print("Drawing Mode")


    img[0:120, 0:1280] = header
    cv2.imshow("Image", img)
    cv2.waitKey(1)

    