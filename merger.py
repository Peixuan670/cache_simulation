import pandas as pd
import numpy as np
import os

path = "E:\\trace\\MSR-Cambridge2"
files = os.listdir(path)
index = 0.5  # 比例系数

df = pd.read_csv(path + '/CAMRESSDPA01-lvm1.csv')   # 选一个较大的trace，获取截止时间点
df.columns = ['Timestamp', 'Hostname', 'DiskNumber', 'Type', 'Offset', 'Size', 'ResponseTime']
df['Timestamp'] = df['Timestamp'].astype(np.int64)
df = df.sort_values(by='Timestamp')
request_count = df.shape[0]
time_line = df['Timestamp'][int(index * request_count)]  # 截止时间点

for file in files:   # 合并
    df = pd.read_csv(os.path.join(path, file), header=None)
    df.columns = ['Timestamp', 'Hostname', 'DiskNumber', 'Type', 'Offset', 'Size', 'ResponseTime']
    df['Timestamp'] = df['Timestamp'].astype(np.int64)
    df = df.sort_values(by='Timestamp')
    print(file)
    print(df.shape[0])
    df = df[df['Timestamp'] < time_line]       # 保留截止时间点之前的请求
    print(df.shape[0])
    df.to_csv("C:\\Users\\46065\\Desktop\\trace.csv", header=None, mode='a', index=0)

df = pd.read_csv("C:\\Users\\46065\\Desktop\\trace.csv", header=None)            # 将生成的trace按时间排序
df.columns = ['Timestamp', 'Hostname', 'DiskNumber', 'Type', 'Offset', 'Size', 'ResponseTime']
df['Timestamp'] = df['Timestamp'].astype(np.int64)
df = df.sort_values(by='Timestamp')
print(df.head(10))






