import numpy as np
import pyedflib
import keyboard
import random
import time
import sys
sys.path.append('../')
from plumberhub import PlumberHubClient
import datetime

# montage
CHANNEL_NUMBER = 16
CHANNEL_NAME = ['FZ','FCZ','CZ','P5','P3','PZ','P4','P6','PO5','PO3','POZ','PO4','PO6','O1','OZ','O2']

SAMPLE_RATE = 1000

# file param    
eegEdf_file = None
eventEdf_file = None
sampleStartTime = 0
times = 0

class SampleBuffer:
    cache = []
    length = 0

    def __init__(self):
        self.flush()

    def flush(self):
        self.cache.clear()
        self.length = 0

        for index in range(CHANNEL_NUMBER):
            self.cache.append([])

    def append(self, dataList):
        index = 0

        while index < CHANNEL_NUMBER:
            self.cache[index].append(dataList[index])
            index += 1
        
        self.length += 1

sample_buffer = SampleBuffer()

def createEDF(type):  
    global eegEdf_file
    global eventEdf_file

    now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
    filename = r"recorder-" + now + type + r".bdf"
    
    print("File: " + filename + " created!")
    
    if(type == 'eeg'):
        eegEdf_file = pyedflib.EdfWriter(filename, CHANNEL_NUMBER, file_type = pyedflib.FILETYPE_BDFPLUS)
    elif(type == 'event'):
        eventEdf_file = pyedflib.EdfWriter(filename, CHANNEL_NUMBER, file_type = pyedflib.FILETYPE_BDFPLUS)


    channel_info_list = []

    for index in range(CHANNEL_NUMBER):
        channel_info_list.append({
            'label': CHANNEL_NAME[index],
            'dimension': 'μV',
            'sample_rate': SAMPLE_RATE,
            'physical_max': 5000,    #5000uV
            'physical_min': -5000,   #-5000uV
            'digital_max': 32767,
            'digital_min': -32768,
            'transducer': '',
            'prefilter':''
        })

    if(type == 'eeg'):    
        eegEdf_file.setSignalHeaders(channel_info_list)


def clearEDF():
    global eegEdf_file
    global sampleStartTime

    if (eegEdf_file != None):
        eegEdf_file.close()
        eegEdf_file == None
    
    if (eventEdf_file !=None):
        eventEdf_file.close()
        eventEdf_file == None       

    sampleStartTime = 0 


def handleSample(sample):
    global eegEdf_file
    global sampleStartTime
    global times
    
    
    if (eegEdf_file != None):
            
        if sample_buffer.length < SAMPLE_RATE-1:
            sample_buffer.append(sample.dataList) 
        else:
            npSample = []
            sample_buffer.append(sample.dataList)
            for channel in sample_buffer.cache:
                npSample.append(np.array(channel)) 
               
            eegEdf_file.writeSamples(npSample)
            sample_buffer.flush()
    

def handleEvent(event): 
    global eventEdf_file
    global sampleStartTime

    if (eventEdf_file != None): 
        event_second = event.at
        offset = (event_second - sampleStartTime)/1000  
        print(offset) 
        eventEdf_file.writeAnnotation(offset,0,'1s event')

client = PlumberHubClient(
    hostname = '127.0.0.1',
    port = 8080,
    client_id = 'ba42f834e21980f008ca82110d89a9b4154ef13880d8b0d827eecaf759699d44',
    onsample = handleSample,  
    onevent = handleEvent
)
 
while True:  

    if keyboard.is_pressed('space'):
        if (eegEdf_file == None):
            createEDF('eeg')
        
        if (eventEdf_file == None):
            createEDF('event')
        
        
    elif keyboard.is_pressed('ctrl'):
        if ((eegEdf_file != None) and (eventEdf_file != None)):
            clearEDF()
            print('Finished!') 