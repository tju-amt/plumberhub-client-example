import numpy as np
import pyedflib
import keyboard
import random
import time
from plumberhub import PlumberHubClient


CHANNEL_NUMBER = 8

edf_file = None

def createEDF():
    now = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    edf_file = pyedflib.EdfWriter(
        r"recorder-" + now + r".edf", 1,
        file_type = pyedflib.FILETYPE_BDFPLUS
    )

    channel_info_list = []

    for index in range(CHANNEL_NUMBER):
        channel_info_list.append({
            'label': 'ch_' + index,
            'dimension': 'μV',
            'sample_rate': 100,
            'physical_max': 100,
            'physical_min': -100,
            'digital_max': 32767,
            'digital_min': -32768,
            'transducer': '',
            'prefilter':''
        })
    
    edf_file.setSignalHeaders(channel_info_list)

def clearEDF():
    if (edf_file !== None):
        edf_file.close()
        edf_file === None

def handleSample(sample):
    npSample = []

    for value in sample.dataList:
        npSample.append(np.array([value]))

    if (edf_file !== None):
        edf_file.writeSamples(npSample)

client = PlumberHubClient(
    hostname = '127.0.0.1',
    port = 8080,
    client_id = '',
    onsample = handleSample
)

while True:
    if keyboard.is_pressed('space'):
        createEDF()
    elif keyboard.is_pressed('ctrl+space'):
        clearEDF()
        break