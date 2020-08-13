#!/usr/bin/env python
# coding: utf-8

# In[37]:


import numpy as np
import cv2
import time
import math
import imutils
from imutils.video import FileVideoStream, VideoStream
import keyboard
from pynput.keyboard import Key, Controller
#keyboard=Controller()
import numpy as np


# In[38]:


size_height = 600
size_width = 600
last = 0 #last extreme of steer
chng = 3 #change in last, to remove small changes fulucations
chngt = 3 #to restart change to 0, if moved towards centre by some value

COLOR_RED = (0, 0, 255)
COLOR_BLACK = (0, 0, 0)

THRESH_ACTION = 60 # t

def get_centroid(bbox): #center point of rectangle
    x, y, w, h = bbox
    centx = (2*x+w)//2
    centy = (2*y+h)//2
    return (centx, centy)


def draw_circle(frame, center, radius=THRESH_ACTION, color=COLOR_BLACK, thickness=3):
    cv2.circle(frame, center, radius, color, thickness)
 

def drawbox(ret, bbox, frame): #draws rectangle from bbox
    global q
    if ret:
        #Tracking Success
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)

    if p1[0] < 10: #quits program if taken hand to left top corner
        q = True # quit


# In[39]:


color = {"blue":(255,0,0), "red":(0,0,255), "green":(0,255,0), "white":(255,255,255)}

def detect_center(img, hand):
    
     # convert image to gray-scale
    # drawing rectangle around the feature and labeling it
    (x, y, w, h) = [int(v) for v in hand]
    #  cv2.rectangle(img, (x,y), (x+w, y+h),  color['green'], 2)  #uncomment if you want to see face boundary
    cv2.circle(img, ((2*x+w)//2,(2*y+h)//2), 2, color['green'], 2) 
    hand = ((2*x+w)//2,(2*y+h)//2)
    return img, hand
#cord  value will be decided by uh by assigning the cirle on screen
def draw_controller_left(img, cords):
    size = 40
    #x1 = cords[0] - size
    y1 = cords[1] - size
    #x2 = cords[0] + size
    y2 = cords[1] + size
    cv2.circle(img, cords,  size, color['blue'],2) 
    return (y1,y2)

def draw_controller_right(img, cords):
    size = 40
    x1 = cords[0] - size
    #y1 = cords[1] - size
    x2 = cords[0] + size
    #y2 = cords[1] + size
    cv2.circle(img, cords,  size, color['red'], 2) 
    return (x1,x2)

def keyboard_events_l(lcord,cord_left, cmd):
    try:
        #x1,x2 = cord_right
        y1,y2 = cord_left
        xl,yl=lcord
        #xr,yr=rcord
    except Exception as e: 
        print(e)
        return
    #if xr < x1:
    #    cmd = "left"
    #elif(xr > x2):
    #    cmd = "right"
    if(yl<y1):
        cmd = "w"
    elif(yl > y2):
        cmd = "s"
    if cmd:
        print("Detected movement: ", cmd,  "\n")
        #if cmd=="left":
        #  keyboard.press(cmd)
        #elif cmd=="right":
        #   keyboard.press(cmd)
        keyboard.press(cmd)
       
        #keyboard.press(cmd)
    return cmd

def keyboard_events_r(rcord,cord_right, cmd2):
    try:
        x1,x2 = cord_right
        #y1,y2 = cord_left
        #xl,yl=lcord
        xr,yr=rcord
    except Exception as e: 
        print(e)
        return
    if xr < x1:
        cmd2 = "a"
    elif(xr > x2):
        cmd2 = "d"
    #elif(yl<y1):
    #    cmd = "up"
    #elif(yl > y2):
    #    cmd = "down"
    if cmd2:
        print("Detected another movement: ", cmd2,  "\n")
        keyboard.press(cmd2)
        #elif cmd=="up":
        #   keyboard.press(cmd2)
        #elif cmd=="down":
        #   keyboard.press(cmd2)
        
        #keyboard.press(cmd)
    return cmd2


def reset_press_flag(lcord,rcord,cord_left,cord_right,cmd,cmd2):
    try:
        x1,x2 = cord_right
        y1,y2 = cord_left
        xl,yl=lcord
        xr,yr=rcord
        #xc, yc = nose_cords
    except: 
        return True,cmd,cmd2
    if x1<xr<x2 or y1<yl<y2:
        if x1<xr<x2 and (cmd2!=None and cmd2!=""):
            keyboard.release(cmd2)
        if y1<yl<y2 and (cmd!=None and cmd!=""):
            keyboard.release(cmd)
        if x1<xr<x2 and y1<yl<y2:
            #keyboard.release(cmd)
            return True,None,None
        elif x1<xr<x2:
            return True,cmd,None
        elif y1<yl<y2:
            return True,None,cmd2
    return False,cmd,cmd2

def get_frame(): # to get frame by reading fvs, init fvs first
    res,frame = fvs.read()
    if frame is None:
        raise Exception("Frame Not Found")
        return
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=size_width, height=size_height) 
    return frame


# In[40]:




fvs = cv2.VideoCapture(0) #0 for web cam
time.sleep(2.0) #to allow web cam to open

TIMER_SETUP = 3 # timer for capturing base image
t = time.time()

while True:
    frame = get_frame()
    curr = (time.time() - t)
    if curr > TIMER_SETUP:
        break
    cv2.putText(frame, str(int(TIMER_SETUP - curr)+1), (225,255), cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLOR_RED, 4)
    cv2.imshow("Setup", frame)
    cv2.waitKey(1)

FRAME = frame.copy()
cv2.destroyAllWindows()

#Make box around hand
frame = FRAME.copy()
cv2.putText(frame, 'Select Left Hand for steering', (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
bboxleft = cv2.selectROI(frame, False) # bounding box for left hand 

frame = FRAME.copy()
cv2.putText(frame, 'Select Right Hand for acceleration', (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
bboxright = cv2.selectROI(frame, False) # bounding box for right hand

#centleft = get_centroid(bboxleft)
#centright = get_centroid(bboxright)

#draw_circle(frame, centleft) # circle, outside this movements will happend
#draw_circle(frame, centright)

BBL, BBR = bboxleft, bboxright # saving it for later

cv2.destroyAllWindows()
#fvs.release()

# In[41]:


#BBR
'''
cv2.destroyAllWindows()

'''


# In[ ]:





# In[42]:


#fvs = cv2.VideoCapture(0) #0 for web cam
#time.sleep(2.0) 

bboxleft, bboxright = BBL, BBR 

# Creating the CSRT Tracker
trackerleft = cv2.TrackerCSRT_create() # left hand for steering
trackerright = cv2.TrackerCSRT_create() # right hand for acceleration (acc)

# Initialize tracker with first frame and bounding box
trackerleft.init(FRAME, bboxleft)
trackerright.init(FRAME, bboxright)

#cv2.putText(frame.copy(), 'Put both your hands in Postion', (100,70), \
cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_BLACK, 2


press_flag = False
cmd = ""
cmd2= ""

while True:
    frame = get_frame()
    #if curr > TIMER_SETUP or frame is None:
    #    break
    #cv2.putText(frame, str(int(TIMER_SETUP - curr)+1), (225,255), cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLOR_RED, 4)
    if BBL is not None:
        # grab the new bounding box coordinates of the object
        (success, box) = trackerleft.update(frame)
        (success1, box1) = trackerright.update(frame)
        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                (0, 255, 0), 2)
            (a,b,c,d)= [int(f) for f in box1]
            cv2.rectangle(frame, (a, b), (a + c, b + d),
                (0, 255, 0), 2)
        
        #cv2.putText(img, cmd, (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, color['red'], 1, cv2.LINE_AA)
        frame,lcord=detect_center(frame,box)
        frame,rcord=detect_center(frame,box1)
        #print("detect_center func called...")
        #draw boundary circle
        cord_left = draw_controller_left(frame, (110,189) )
        cord_right = draw_controller_right(frame, (479,189) )
        #print("circle draw done")
        if press_flag and (cmd==None or cmd==""):
            #print("calling keyboard event")
            cmd = keyboard_events_l(lcord,cord_left, cmd)
        
        if  press_flag and (cmd2==None or cmd2==""):
            
            cmd2= keyboard_events_r(rcord,cord_right, cmd2)
        press_flag,cmd,cmd2 = reset_press_flag(lcord,rcord,cord_left,cord_right,cmd,cmd2)
        #print("press flag: ",press_flag)
        
        # Writing processed image in a new window
        
    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1)==13:
        break
    

cv2.destroyAllWindows()
fvs.release()


# In[43]:


#fvs.release()


# In[44]:


#BBL



