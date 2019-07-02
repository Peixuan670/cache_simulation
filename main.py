import matplotlib.pyplot as plt

from client import Client
from server import Server

FILE_NUM = int(1e2)
REQUEST_NUM = int(1e4)
client_balenced = Client(FILE_NUM, REQUEST_NUM)
client_imbalenced = Client(FILE_NUM, REQUEST_NUM, False)

print(FILE_NUM)
print(REQUEST_NUM)

plt.figure(figsize=(15, 8))
plt.xlabel("time")
plt.ylabel("file id")
plt.title("trace(yellow is requested)")
plt.imshow(client_balenced.trace.reshape((FILE_NUM, REQUEST_NUM)), aspect='auto')
plt.show()

plt.figure(figsize=(15, 8))
plt.xlabel("time")
plt.ylabel("file id")
plt.title("trace(yellow is requested)")
plt.imshow(client_imbalenced.trace.reshape((FILE_NUM, REQUEST_NUM)), aspect='auto')
plt.show()

little_server_a_hit_rate = []
little_server_b_hit_rate = []
big_server_hit_rate = []
# 横轴，cache的大小 0 - 50%
cache_size_array = []
for cache_size in range(client_balenced.file_pool_size // 10, client_balenced.file_pool_size // 2, client_balenced.file_pool_size // 100):
    cache_size_array.append(cache_size / client_balenced.file_pool_size)
    little_server_a = Server(cache_size)
    little_server_b = Server(cache_size)
    big_server = Server(cache_size * 2)
    for request_file in client_balenced.make_requests():
        if request_file.fid & 0b10:
for cache_size in range(client.file_pool_size // 20, client.file_pool_size // 3, client.file_pool_size // 100):
    cache_size_array.append(cache_size / client.file_pool_size)
    little_server_a = Server(cache_size)
    little_server_b = Server(cache_size)
    big_server = Server(cache_size * 2)

    for request_file in client.make_requests():
        if request_file.fid % 2:
            little_server_a.handle(request_file)
        else:
            little_server_b.handle(request_file)

    little_server_a_hit_rate.append(little_server_a.hit_rate())
    little_server_b_hit_rate.append(little_server_b.hit_rate())

    for request_file in client.make_requests():
        big_server.handle(request_file)
    big_server_hit_rate.append(big_server.hit_rate())

# print(little_server_a_hit_rate)
# print(little_server_b_hit_rate)
average_hit_rate = []
for i in range(len(little_server_a_hit_rate)):
    average_hit_rate.append((little_server_a_hit_rate[i] + little_server_b_hit_rate[i]) / 2)

plt.figure(figsize=(15, 8))
plt.plot(cache_size_array, little_server_a_hit_rate, color='green', label='little cache A')
plt.plot(cache_size_array, little_server_b_hit_rate, color='red', label='little cache B')
plt.plot(cache_size_array, big_server_hit_rate, color='yellow', label='big cache')
plt.plot(cache_size_array, average_hit_rate, color='blue', label='average of A and B')
plt.xlabel("little cache size / file pool total size")
plt.ylabel("hit rate")
plt.legend()
plt.show()


little_server_a_hit_rate = []
little_server_b_hit_rate = []
big_server_hit_rate = []
cache_size_array = []
for cache_size in range(client_imbalenced.file_pool_size // 10, client_imbalenced.file_pool_size // 2, client_imbalenced.file_pool_size // 100):
    cache_size_array.append(cache_size / client_imbalenced.file_pool_size)
    little_server_a = Server(cache_size)
    little_server_b = Server(cache_size)
    big_server = Server(cache_size * 2)
    for request_file in client_imbalenced.make_requests():
        if request_file.fid & 0b10:
            little_server_a.handle(request_file)
        else:
            little_server_b.handle(request_file)
    little_server_a_hit_rate.append(little_server_a.hit_rate())
    little_server_b_hit_rate.append(little_server_b.hit_rate())
    for request_file in client.make_requests():
        big_server.handle(request_file)
    big_server_hit_rate.append(big_server.hit_rate())

plt.figure(figsize=(15, 8))
plt.plot(cache_size_array, little_server_a_hit_rate, color='green', label='little cache A')
plt.plot(cache_size_array, little_server_b_hit_rate, color='red', label='little cache B')
plt.plot(cache_size_array, big_server_hit_rate, color='yellow', label='big cache')
plt.xlabel("little cache size / file pool total size")
plt.ylabel("hit rate")
plt.legend()
plt.show()