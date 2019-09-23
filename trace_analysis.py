import numpy as np
import pandas as pd
from collections import OrderedDict
import matplotlib.pyplot as plt

df = pd.read_csv('C:\\Users\\XPS\\Desktop\\cache_simulation\\CAMRESSDPA01-lvm0.csv', header=None)
df.columns = ['Timestamp', 'Hostname', 'DiskNumber', 'Type', 'Offset', 'Size', 'ResponseTime']
df['Timestamp'] = df['Timestamp'].astype(np.int64)
df = df.sort_values(by='Timestamp')

file_pool_size = df.drop_duplicates(['Offset'])['Size'].sum()
total_request_byte = df['Size'].sum()
total_request_count = df.shape[0]

print(total_request_count)
print(total_request_byte)


def make_requests():
    for row in df.itertuples():
        yield getattr(row, 'Offset'), getattr(row, 'Size')


existed_file = {}
have_not_exist_file_count = 0
have_not_exist_file_byte = 0
step = int(total_request_count / 20)
time = 0

time_array = []
have_not_exist_file_count_array = []
have_not_exist_file_byte_array = []

for fid, size in make_requests():
    time += 1
    flag = 0
    try:
        flag = existed_file[fid]
    except:
        flag = 0
    if flag == 0:
        have_not_exist_file_count += 1
        have_not_exist_file_byte += size
        existed_file[fid] = 1
    if time % step == 0:
        print(time)
        time_array.append(time)
        have_not_exist_file_count_array.append(have_not_exist_file_count)
        have_not_exist_file_byte_array.append(have_not_exist_file_byte)
        have_not_exist_file_count = 0
        have_not_exist_file_byte = 0

plt.figure(figsize=(15, 8))
plt.plot(time_array, have_not_exist_file_count_array, marker='o')
plt.xlabel("time")
plt.ylabel("counts of first request")
plt.show()

plt.figure(figsize=(15, 8))
plt.plot(time_array, have_not_exist_file_byte_array, marker='o')
plt.xlabel("time")
plt.ylabel("bytes of first request")
plt.show()