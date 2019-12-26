##Libraries
import cv2                               #to process to videos
import tkinter as tk                     #to chose the video file to process
from tkinter import filedialog
import os                                #to process the file names

##Parameters
fps=10              #number of frames per second on the converted video
avgListSize=5       #number of consecutive images used to have an average reference image

##Functions
"""
converts the input video to a smoothed, grey, croped video

Takes the path of the file as an argument
"""
def convert_video(path):
    #input raw video
    cap = cv2.VideoCapture(path)
    
    #read the first fram
    ret, frame = cap.read()

    #resize the first frame of the video to chose the door position more easily
    select_size=int(cap.get(3)/4), int(cap.get(4)/4) 
    resize_frame=cv2.resize(frame,select_size,fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
    r = cv2.selectROI("Select the door",resize_frame, False, False)
    r=tuple(4*x for x in r)
    cv2.destroyAllWindows()

    #output  writer
    out_path='./videos/g'+os.path.basename(path)
    size=int(r[2]),int(r[3])
    out = cv2.VideoWriter(out_path,cv2.VideoWriter_fourcc('M','J','P','G'), fps, size,0)
    
    while ret:
        # Crop image
        frame = frame[r[1]:r[1]+r[3], r[0]:r[0]+r[2]]
        
        #from color to grey scale
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        
        #remove the noise
        frame=cv2.medianBlur(frame,11)
        
        #export the frame
        out.write(frame)
        
        #loop
        ret, frame = cap.read()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    out.release()
    return out_path

"""
converts the smoothed grey cropped video to a movement sensitive video

Takes the path of the file as an argument
"""
def difference_video(path):
    #input grey video
    cap = cv2.VideoCapture(path)
    
    #output writer
    size=int(cap.get(3)),int(cap.get(4))
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    out_path='./videos/m'+os.path.basename(path)
    out = cv2.VideoWriter(out_path,fourcc, fps, size, 0)
    
    #initialization of the average blank frame and the corresponding list
    ret, frame = cap.read()
    avgList=[frame]
    avg=cv2.subtract(frame,frame)
    avg=cv2.addWeighted(avg,avgListSize/(avgListSize+1),frame,1/(avgListSize+1),0)
    while len(avgList)!=avgListSize:
        frame=cap.read()[1]
        avg=cv2.addWeighted(avg,avgListSize/(avgListSize+1),frame,1/(avgListSize+1),0)
        avgList.append(frame)
    
    while(ret):
        #make and write a picture
        diff_frame=cv2.absdiff(frame,avg)
        diff_frame=cv2.medianBlur(diff_frame,9)
        out.write(cv2.cvtColor(diff_frame, cv2.COLOR_BGR2GRAY))
        
        #updating avgList
        avgList.append(frame)
        
        #updating avg
        avg=cv2.addWeighted(avg,avgListSize/(avgListSize+1),frame,1/(avgListSize+1),0)
        ret, frame = cap.read()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    out.release()
    return out_path
    

    
"""
evaluate the direction and the movement rate

takes to pictures to compare
"""    
def compare(frame1, frame2):
    #gets the dimensions of the first frame
    height, width = frame1.shape[:2]
    
    #decides of the number of positions to compare the two frames
    n=20
    subwidth=width//n
    subframes=[]
    
    #creates a frame with black borders to crop
    black=cv2.subtract(frame1,frame1)
    frame1_border=cv2.hconcat([black,frame1,black])
    
    #creates the 2*n-1 cropped pictures to compare to frame2
    for i in range(1,2*n):
        subframes.append(frame1_border[:,i*subwidth:i*subwidth+width])
    
    #choose the position with the minimum difference
    min_id=0
    min=255
    for i in range(len(subframes)):
        if cv2.mean(cv2.mean(cv2.absdiff(subframes[i],frame2))[:2])[0]<min:
            min=cv2.mean(cv2.mean(cv2.absdiff(subframes[i],frame2))[:2])[0]
            min_id=i
    
    #returns a value proportionnal to the "movement rate"
    return -(min_id+2-n)*cv2.mean(cv2.mean(frame1))
        
"""
evaluate number of persons getting in and out

takes the path of the movement video as argumen
"""         
def overall_mvt(path):
    #input movement video
    cap = cv2.VideoCapture(path)
    ret, frame=cap.read()
    
    #overall result
    r=0
    
    #intermediate counter
    cpt=0
    
    while ret:
        #ignore black frames
        if cv2.mean(cv2.mean(frame)[:2])[0]>5:
            
            cv2.imshow("",frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            ret,next_frame=cap.read()
            
            if ret!=True:
                break
            
            #get the movement of the current frame
            comparaison=compare(frame,next_frame)
            r+=comparaison
            
        #update the counter from a rate to an int
        elif r!=0:
            cpt+=r//1000
            r=0
            ret, frame=cap.read()
        
        else:
            ret, frame=cap.read()
    cap.release()
    return cpt+r//1000
    
##Main
root = tk.Tk()
root.withdraw()



file_path = filedialog.askopenfilename()



grey=convert_video(file_path)
diff=difference_video(grey)

print(overall_mvt(diff))
cv2.destroyAllWindows()