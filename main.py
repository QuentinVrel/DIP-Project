#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 13:47:58 2019

@author: quentinvrel
"""

##Libraries
import cv2                               #to process to videos
import tkinter as tk                     #to chose the video file to process
from tkinter import filedialog
import ntpath                            #to process the file names

##Parameters


##Functions
def convert_video(path, fps, size):
    cap = cv2.VideoCapture(path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out_path='./videos/'+ntpath.basename(path)
    out = cv2.VideoWriter(out_path,fourcc, fps, size)
    ret, frame = cap.read()
    while ret:
        
        frame=cv2.cvtColor(cv2.resize(frame,size,fx=0,fy=0, interpolation = cv2.INTER_CUBIC), cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame',frame)
    
        out.write(frame)
        ret, frame = cap.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return out_path
        
    

##Main
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

size=int(input("width?")),int(input("height?"))
fps=int(input("frames per second?"))

cap = cv2.VideoCapture(convert_video(file_path,fps,size))

cap.release()
cv2.destroyAllWindows()