
""" sending OSC with pyOSC
https://trac.v2.nl/wiki/pyOSC
example by www.ixi-audio.net based on pyOSC documentation
"""
import cv2
import time, random
import os, sys
import numpy as np
from main import tabStateToColor
DOT_SIZE = 100

class DEBUG_WINDOW:
    def __init__(self):
        self.frame = np.ones((100,200,3))*255
        self.frames = {}
        self.framesIdx = {}
        return
    def setDataRaw(self,name,data):
        self.frames[name] = data
        return
    def getData(self,name):
        return self.framesIdx[name]
    def setData(self,name,data):
        self.framesIdx[name] = data
        buf = np.ones((DOT_SIZE,DOT_SIZE*len(data),3),dtype = np.uint8)
        for i,j in enumerate(data):
            buf[:,i*DOT_SIZE:(i+1)*DOT_SIZE,:] = 255
            c = tabStateToColor(j)
            #buf[2:-2,i*DOT_SIZE+2:(i+1)*DOT_SIZE-2,0] = int(max(0,min((j-20) * 25.5,255,(50-j)*25.5)))
            #buf[2:-2,i*DOT_SIZE+2:(i+1)*DOT_SIZE-2,1] = int(max(0,min((j-10) * 25.5,255,(40-j)*25.5)))
            #buf[2:-2,i*DOT_SIZE+2:(i+1)*DOT_SIZE-2,2] = int(max(0,min(j * 25.5,255,(30-j)*25.5)))
            buf[2:-2,i*DOT_SIZE+2:(i+1)*DOT_SIZE-2,0] = c[0]
            buf[2:-2,i*DOT_SIZE+2:(i+1)*DOT_SIZE-2,1] = c[1]
            buf[2:-2,i*DOT_SIZE+2:(i+1)*DOT_SIZE-2,2] = c[2]
        self.setDataRaw(name,buf)
        return
    def clear(self):
        cv2.destroyAllWindows()
        self.__init__()
        key = cv2.waitKey(1)
    def update(self):
        cv2.imshow('HydroPumper',self.frame)
        for i in self.frames.keys():
            cv2.imshow(i,self.frames[i])
        key = cv2.waitKey(1)
        return key
    def close(self):
        cv2.destroyAllWindows()


def main():
    pass


if __name__=='__main__':
    argvs=sys.argv
    print argvs
    main()