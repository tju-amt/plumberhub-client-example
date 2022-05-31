import numpy as np
import pandas as pd
import keyboard
import random
import time
import sys
sys.path.append('../')
from plumberhub import PlumberHubClient
import datetime
import os

# montage
CHANNEL_NUMBER = 16
CHANNEL_NAME = ['FZ','FCZ','CZ','P5','P3','PZ','P4','P6','PO5','PO3','POZ','PO4','PO6','O1','OZ','O2']
SAMPLE_RATE = 1000

# file param    
eegCSV_file = None
eventCSV_file = None

Header = CHANNEL_NAME.copy()
Header.append('LABEL')
Header.append('TimeStamp')

index = 0

# buffer
SampleBuffer = np.zeros(shape=(SAMPLE_RATE,len(Header)))
EventBuffer = np.zeros(shape=(1,2))
#%%
def createCSV(type):  
    global eegCSV_file
    global eventCSV_file

    now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
    savePath = os.getcwd()+'\\recorder-'+ now
    if(os.path.exists(savePath)!=True):
        os.mkdir(savePath)
    
    if(type == 'eeg'):
        filename =  type + r".csv"
        eegCSV_file = savePath+'\\'+filename
        
        df = pd.DataFrame(columns=Header)
        df.to_csv(eegCSV_file,index=False)
        print("File: " + filename + " created!")
        
    elif(type == 'event'):
        filename = type + r".csv"
        eventCSV_file = savePath+'\\'+filename
        
        df = pd.DataFrame(columns=['LABEL','TimeStamp'])
        df.to_csv(eventCSV_file,index=False)
        print("File: " + filename + " created!")


def clearCSV():
    global eegCSV_file
    global eventCSV_file

    if (eegCSV_file != None):
        eegCSV_file = None
        
    if (eventCSV_file != None):
        eventCSV_file = None
        


def handleSample(sample):
    global eegCSV_file
    global index
    
    if (eegCSV_file != None):
        
        if(index<SAMPLE_RATE-1):
            SampleBuffer[index,0:16] = np.array(sample.dataList)
            SampleBuffer[index,17] = np.array(sample.microsecond)
            index+=1  
        else:
            SampleBuffer[index,0:16] = np.array(sample.dataList)
            SampleBuffer[index,17] = np.array(sample.microsecond)
            
            nSample = pd.DataFrame(SampleBuffer)
            nSample.to_csv(eegCSV_file,mode='a',index=False,header=False)
            index = 0
    

def handleEvent(event): 
    global eventCSV_file
    
    if (eventCSV_file != None):
        EventBuffer = np.array([event.microsecond,event.event]) 
        nEvent = pd.DataFrame(EventBuffer)
        nEvent.to_csv(eventCSV_file,mode='a',index=False,header=False)                                


client = PlumberHubClient(
    hostname = '127.0.0.1',
    port = 8080,
    client_id = '1d0dc7881d7c16a706b517f333ea826fe889411a574dc3d90e8b2a002cc6ce4d',
    onsample = handleSample,  
    onevent = handleEvent
)
 
while True:  

    if keyboard.is_pressed('space'):
        if (eegCSV_file == None) and (eventCSV_file == None):
            createCSV('eeg')
            createCSV('event')
            print('Begin to Acquire...') 
        
    elif keyboard.is_pressed('ctrl'):
        if (eegCSV_file != None) and (eventCSV_file != None):
            clearCSV()
            print('Finished!') 
            os._exit(0)