import numpy as np
import pyedflib
import keyboard
import random
import time
from plumberhub import PlumberHubClient

CHANNEL_NUMBER = 8
SAMPLE_RATE = 100

edf_file = None

class SampleBuffer:
    cache = []
    length = 0

    def __init__(self):
        self.flush()

    def flush(self):
        self.cache.clear()
        self.length = 0

        for index in range(8):
            self.cache.append([])

    def append(self, dataList):
        index = 0

        while index < CHANNEL_NUMBER:
            self.cache[index].append(dataList[index])
            index += 1
        
        self.length += 1

sample_buffer = SampleBuffer()

def createEDF():
    global edf_file

    now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
    filename = r"recorder-" + now + r".edf"
    print("File: " + filename)
    edf_file = pyedflib.EdfWriter(filename, CHANNEL_NUMBER, file_type = pyedflib.FILETYPE_BDFPLUS)

    channel_info_list = []

    for index in range(CHANNEL_NUMBER):
        channel_info_list.append({
            'label': 'ch_' + str(index),
            'dimension': 'μV',
            'sample_rate': SAMPLE_RATE,
            'physical_max': 100,
            'physical_min': -100,
            'digital_max': 32767,
            'digital_min': -32768,
            'transducer': '',
            'prefilter':''
        })
    
    edf_file.setSignalHeaders(channel_info_list)

def clearEDF():
    global edf_file

    if (edf_file != None):
        edf_file.close()
        edf_file == None


def handleSample(sample):
    global edf_file

    if (edf_file != None):
        if sample_buffer.length < SAMPLE_RATE:
            sample_buffer.append(sample.dataList)
        else:
            npSample = []

            for channel in sample_buffer.cache:
                npSample.append(np.array(channel))

            edf_file.writeSamples(npSample)
            sample_buffer.flush()

client = PlumberHubClient(
    hostname = '127.0.0.1',
    port = 8080,
    client_id = '314dee1f82e82106c8ab4d51ee933c9a4c09209dfebc35b2f2f5fd55be73302e',
    onsample = handleSample
)

while True:
    if keyboard.is_pressed('space'):
        if (edf_file == None):
            createEDF()

    elif keyboard.is_pressed('ctrl'):
        if (edf_file != None):
            clearEDF()
            print('Finished!')