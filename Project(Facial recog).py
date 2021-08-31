# -*- coding: utf-8 -*-
"""
Created on Tue May 11 22:27:58 2021

@author: ACER
"""

import cv2
import numpy as np
import pandas as pd
import face_recognition
import os
from datetime import datetime
import email_to
import cred_mail 

date=datetime.now()
dateStr=date.strftime('%m-%d-%Y')
name_list=[]
path = 'Images'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def send_mail(lst,nme,roll):
     for i in range(len(lst)):
        mail_server = email_to.EmailServer('smtp.gmail.com', 587,cred_mail.email, cred_mail.password)
        mail_server.quick_email(lst[i], 'Absent in Class',
                   ["# Your ward "+nme[i]+" ,Roll No: " +str(roll[i])+  " did not Attend Today's class", 'Dear '+lst[i]+' you are hereby informed that your ward did not attend English class scheduled today.'],
                   style='h1 {color: Green}')
        print("Mail sent!")
     return 1


def return_Encodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
                df=pd.read_csv("Attendance.csv")
                df1=pd.read_csv("Student_Info.csv")
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                dtString2=now.strftime('%m-%d-%Y')
                det=name.split("_")
                print(det)
                df.loc[df['Roll_No_University'] == int(det[1]), ['Attendance','Date','Time']] = 'Present',dtString,dtString2
                print(df)
                print(df1)
                df.to_csv("Attendance.csv",index=False)
                if(det[0] not in name_list):
                    df1.loc[df1['Roll_No_University'] == int(det[1]), 'Classes_Attended'] +=1 
                    df1.to_csv("Student_Info.csv",index=False)
                    name_list.append(det[0])


encodeListKnown = return_Encodings(images)
print('Encoding Complete')
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
while True:
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
 
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        matchIndex = np.argmin(faceDis)
 

        if faceDis[matchIndex]< 0.50:
            name = classNames[matchIndex].upper()
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendance(name)
        else: 
            name = 'Unknown'
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

data=pd.read_csv("Attendance.csv")
data1=pd.read_csv("Student_Info.csv")
Present= data.loc[(data["Attendance"] =='Present')]
Absent=data.loc[data["Attendance"]!='Present']
data1['Total_Classes']=data1['Total_Classes']+1
data1.to_csv("Student_Info.csv",index=False)
data.loc[data['Attendance'] != 'Present', ['Attendance']] = 'Absent'
data.to_csv("Attendance"+dateStr+".csv",index=False)
data["Attendance"]=""
data["Date"]=""
data["Time"]=""
data.to_csv("Attendance.csv",index=False)
Email_list=Absent["P_E-mail"].tolist()
Names=Absent["Name"].tolist()
Roll=Absent['Roll_No_University'].tolist()
x=send_mail(Email_list,Names,Roll)
if(x==1):
    print("All mail sent!!!")
