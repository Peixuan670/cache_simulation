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
print("total request byte", total_request_byte)
print("total request count", total_request_count)


def make_requests():
    for row in df.itertuples():
        yield getattr(row, 'Offset'), getattr(row, 'Size')


class Server:  # 服务器(cache)
    def __init__(self, space):
        self.space = space  # cache大小
        self.remain = space  # cache剩余空间
        self.cache = OrderedDict()  # OrderDict() 模拟cache LRU方法
        self.hit_count = 0  # 命中次数
        self.hit_byte = 0
        self.miss_count = 0  # 未命中次数
        self.miss_byte = 0

    def _hit(self, fid, size):
        self.hit_count += 1
        self.hit_byte += size
        self.cache.move_to_end(fid)

    def _miss(self, fid, size):
        self.miss_count += 1
        self.miss_byte += size
        while self.remain < size:
            self.remain += self.cache.popitem(last=False)[-1]  # pop出第一个item
        self.cache[fid] = size
        self.remain -= size

    def handle(self, fid, size):  # 处理一次请求
        if fid in self.cache.keys():
            self._hit(fid, size)
        else:
            self._miss(fid, size)


class Dispatcher:
    def __init__(self, cache_size, cache_number, simple=True):
        self.cache_number = cache_number
        self.big_cache = Server(cache_size * cache_number)
        self.small_caches = []
        for i in range(cache_number):
            server = Server(cache_size)
            self.small_caches.append(server)
        self.small_caches_heat = [0] * cache_number
        if simple:
            self.handle_requests = self.simple_hash
        else:
            self.handle_requests = self.load_balance
            self.file_mapper = {}
            for row in df.drop_duplicates(['Offset']).itertuples():
                fid = getattr(row, 'Offset')
                self.file_mapper[fid] = (fid // 10000 % 1000000) & 0b11111 % cache_number

    def load_balance(self, fid, size):
        server = self.file_mapper[fid]
        if fid in self.small_caches[server].cache.keys():
            self.small_caches[server].handle(fid, size)
            self.small_caches_heat[self.file_mapper[fid]] += size
        else:
            server = self.small_caches_heat.index(min(self.small_caches_heat))
            self.small_caches[server].handle(fid, size)
            self.file_mapper[fid] = server
        self.big_cache.handle(fid, size)

    def simple_hash(self, fid, size):
        self.small_caches[(fid // 10000 % 1000000) & 0b11111 % self.cache_number].handle(fid, size)


dispatcher_small_server_hit_count_ratio = []
dispatcher_small_server_hit_byte_ratio = []
hasher_small_server_hit_count_ratio = []
hasher_small_server_hit_byte_ratio = []
big_server_hit_count_ratio = []
big_server_hit_byte_ratio = []
time_array = []

CACHE_NUMBER = 4
cache_size = 16000000000

dispatcher = Dispatcher(cache_size, CACHE_NUMBER, False)

pre_request_bytes = 0
pre_dispatcher_small_server_hit_count = 0
pre_dispatcher_small_server_hit_byte = 0
pre_dispatcher_small_server_miss_count = 0
pre_dispatcher_small_server_miss_byte = 0

pre_big_server_hit_count = 0
pre_big_server_hit_byte = 0
pre_big_server_miss_count = 0
pre_big_server_miss_byte = 0

time = 0
step = int(total_request_count/20)

"""
for fid, size in make_requests():
    time += 1
    dispatcher.handle_requests(fid, size)
    if time % step == 0:
        time_array.append(time)
        dispatcher_small_server_hit_count = sum([i.hit_count for i in dispatcher.small_caches]) - \
                                            pre_dispatcher_small_server_hit_count
        pre_dispatcher_small_server_hit_count = sum([i.hit_count for i in dispatcher.small_caches])

        dispatcher_small_server_hit_byte = sum([i.hit_byte for i in dispatcher.small_caches]) - \
                                            pre_dispatcher_small_server_hit_byte
        pre_dispatcher_small_server_hit_byte = sum([i.hit_byte for i in dispatcher.small_caches])

        dispatcher_small_server_miss_count = sum([i.miss_count for i in dispatcher.small_caches]) - \
                                            pre_dispatcher_small_server_miss_count
        pre_dispatcher_small_server_miss_count = sum([i.miss_count for i in dispatcher.small_caches])

        dispatcher_small_server_miss_byte = sum([i.miss_byte for i in dispatcher.small_caches]) - \
                                            pre_dispatcher_small_server_miss_byte
        pre_dispatcher_small_server_miss_byte = sum([i.miss_byte for i in dispatcher.small_caches])

        big_server_hit_count = dispatcher.big_cache.hit_count - pre_big_server_hit_count
        pre_dispatcher_big_server_hit_count = dispatcher.big_cache.hit_count

        big_server_hit_byte = dispatcher.big_cache.hit_byte - pre_big_server_hit_byte
        pre_dispatcher_big_server_hit_byte = dispatcher.big_cache.hit_byte

        big_server_miss_count = dispatcher.big_cache.miss_count - pre_big_server_miss_count
        pre_dispatcher_big_server_miss_count = dispatcher.big_cache.miss_count

        big_server_miss_byte = dispatcher.big_cache.miss_byte - pre_big_server_miss_byte
        pre_dispatcher_big_server_miss_byte = dispatcher.big_cache.miss_byte

        dispatcher_small_server_hit_count_ratio.append\
        (dispatcher_small_server_hit_count / (dispatcher_small_server_hit_count + dispatcher_small_server_miss_count))
        dispatcher_small_server_hit_byte_ratio.append\
        (dispatcher_small_server_hit_byte / (dispatcher_small_server_hit_byte + dispatcher_small_server_miss_byte))

        big_server_hit_count_ratio.append(big_server_hit_count / (big_server_hit_count + big_server_miss_count))
        big_server_hit_byte_ratio.append(big_server_hit_byte / (big_server_hit_byte + big_server_miss_byte))

"""

for fid, size in make_requests():
    time += 1
    dispatcher.handle_requests(fid, size)
    if time % 100 == 0:
        time_array.append(time)
        dispatcher_small_server_hit_count_ratio.append(sum([i.hit_count for i in dispatcher.small_caches]) / time)
        dispatcher_small_server_hit_byte_ratio.append(sum([i.hit_byte for i in dispatcher.small_caches]) /
                                                      (dispatcher.big_cache.hit_byte + dispatcher.big_cache.miss_byte))

        big_server_hit_count_ratio.append(dispatcher.big_cache.hit_count / time)
        big_server_hit_byte_ratio.append(dispatcher.big_cache.hit_byte /
                                         (dispatcher.big_cache.hit_byte + dispatcher.big_cache.miss_byte))



plt.figure(figsize=(15,8))
plt.plot(time_array, dispatcher_small_server_hit_count_ratio, color='red', label='dispatcher')
plt.plot(time_array, big_server_hit_count_ratio,color='black', label='big cache')
plt.xlabel("time")
plt.ylabel("count hit ratio")
plt.legend()
plt.show()

plt.figure(figsize=(15,8))
plt.plot(time_array, dispatcher_small_server_hit_byte_ratio, color='red', label='dispatcher')
plt.plot(time_array, big_server_hit_byte_ratio, color='black', label='big cache')
plt.xlabel("time")
plt.ylabel("byte hit ratio")
plt.legend()
plt.show()