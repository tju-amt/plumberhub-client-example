import numpy as np
import pandas as pd
import sys
import os

#FileToMerge
FileDate = '2022-05-28_21_04_31'
RootDir = os.getcwd()+'\\recorder-'+ FileDate

EEGData = pd.read_csv(RootDir+'\\eeg.csv')
EventData = pd.read_csv(RootDir+'\\event.csv')

#遍历事件并插入EEGData
#step1 读取EEGDATA首个样本的时间戳
StartTimestamp = EEGData['TimeStamp'][0].astype(int)
SampleRate = int(1e6/(EEGData['TimeStamp'][1].astype(int)-EEGData['TimeStamp'][0].astype(int)))
#step2 遍历事件时间戳并赋值
i = 0
for evt in EventData['TimeStamp']:
    idx = int((evt-StartTimestamp)*SampleRate/1e6)
    print(idx)
    EEGData.iloc[idx,16]=EventData['LABEL'][i].astype(int)
    i+=1
#Step3 转存
EEGData.to_csv(RootDir+'\\EEGdataset.csv',index=False)
