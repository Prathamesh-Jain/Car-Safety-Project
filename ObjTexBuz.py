import cv2
import numpy as np
import time
import pygame
import smtplib
from email.message import EmailMessage
import os
import FaceCat

path = 'ImageAttendance'
images = []
classNames2 = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames2.append(os.path.splitext(cl)[0])
print(classNames2)

encodeListKnown = FaceCat.findEncodings(images)
print('Encoding Complete')

pygame.init()
pygame.mixer.init()
sound = pygame.mixer.Sound("BuzzerSound.ogg")

cap = cv2.VideoCapture(0)
whT = 320
confThreshold = 0.5
nmsThreshold = 0.3

classesFile = 'coconames.txt'
classNames = []
with open(classesFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')
    print(classNames)
print(len(classNames))

modelConfiguration = 'yolov3-320.cfg.txt'
modelWeights = 'yolov3.weights'

net = cv2.dnn.readNetFromDarknet(modelConfiguration,modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
#
def findObjects(outputs,img):
    hT,wT,cT = img.shape
    bbox = []
    classIds = []
    confs = []

    for outputs in outputs:
        for det in outputs:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                w,h = int(det[2]*wT) , int(det[3]*hT)
                x,y = int((det[0]*wT)-w/2), int((det[1]*hT)-h/2)
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))

        indices = cv2.dnn.NMSBoxes(bbox,confs,confThreshold,nmsThreshold)
        print(indices)
        for i in indices:
            i = i[0]
        box = bbox[i]
    x,y,w,h = box[0],box[1],box[2],box[3]
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),2)
    cv2.putText(img,f'{classNames[classIds[i]].upper()}  {int(confs[i]*100)}%',
                (x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,255),2)
    return classIds

def email_alert(to,name):
    msg = EmailMessage()
    str = name+' is using mobile phone while driving.'
    print(str)
    msg.set_content(str)
    msg['subject'] = 'Mobile Usage Alert'
    msg['to'] = to

    user = #<your email>
    msg['from'] = user
    password = #<password>

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

while True:
    success, img = cap.read()

    blob = cv2.dnn.blobFromImage(img,1/255,(whT,whT),[0,0,0],1, crop=False)
    net.setInput(blob)

    layerNames = net.getLayerNames()
    #print(layerNames)
    outputNames = [layerNames[i[0]-1] for i in net.getUnconnectedOutLayers()]
    #print(outputNames)
    #print(net.getUnconnectedOutLayers())

    outputs = net.forward(outputNames)
    # print(outputs[0].shape)
    # print(outputs[1].shape)
    # print(outputs[2].shape)
    # print(outputs[0][0])

    classIds = findObjects(outputs,img)
    if(67 in classIds):
        sound.play()
        pygame.time.delay(500)
        name = FaceCat.findName(encodeListKnown, classNames2, cap)
        print(name)
        email_alert('pajainbsl@gmail.com',name)
    cv2.imshow('Image',img)
    cv2.waitKey(1)
    sound.stop()