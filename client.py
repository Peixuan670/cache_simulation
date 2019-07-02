import numpy as np


class File:
    def __init__(self, fid, size):
        self.fid = fid  # 文件惟一id, 从0开始
        self.size = size  # 文件大小


class Client:  # 用户端 请求文件
    def __init__(self, file_num, request_num, balenced=True):
        self.file_num = file_num  # 文件池数量
        self.request_num = request_num  # trace请求数
        self.file_pool = []  # 文件池
        self.file_pool_size = 0  # 文件池总文件大小
        self.trace = np.zeros(shape=(file_num, request_num), dtype=np.int32)  # trace
        self.balenced = balenced  # 是否负载均衡
        self.__make_files__()
        self.__make_trace__()

    def __make_files__(self):  # 生成文件池
        for i in range(self.file_num):
            file = File(i, int(np.random.exponential(scale=100)))  # 文件大小负指数分布
            self.file_pool.append(file)
            self.file_pool_size += file.size

    @staticmethod
    def __frac_exp__(self, s=0.5):
        res = np.random.rand() * np.random.exponential(scale=s)
        while res >= 1:
            res = np.random.rand() * np.random.exponential(scale=s)
        return res
    
    def __make_trace__(self):  # 生成trace
        for file in range(self.file_num):
            request_peaks = int(np.random.randint(1, self.request_num // 100) * np.random.exponential(scale=0.2))
            if request_peaks <= 1:
                continue
            gap = self.request_num // request_peaks
            for peak in range(request_peaks):
                # front 和 back 分别是上下限
                front = peak * gap
                back = front + gap
                mid = np.random.randint(front, back)
                if self.balenced:
                    start = mid - int(self.__frac_exp__(0.5) * (mid - front))
                    end = mid + int(self.__frac_exp__(0.5) * (back - mid))
                else:
                    if file & 0b01: # 小 cache a 的工作量大一些
                        start = mid - int(self.__frac_exp__(0.7) * (mid - front))
                        end = mid + int(self.__frac_exp__(0.7) * (back - mid))
                    else:
                        start = mid - int(self.__frac_exp__(0.4) * (mid - front))
                        end = mid + int(self.__frac_exp__(0.4) * (back - mid))
                start = mid - int(self.__frac_exp__(0.5) * (mid - front))
                end = mid + int(self.__frac_exp__(0.5) * (back - mid))
                for time in range(start, end):
                    self.trace[file][time] = 1
        self.trace = self.trace.reshape((self.request_num, self.file_num))

    def make_requests(self):  # 迭代器 产生文件请求流
        for time in self.trace:
            for i in range(self.file_num):
                if time[i]:
                    yield self.file_pool[i]

    def show_files(self):
        odd_size = 0
        even_size = 0
        for i in self.file_pool:
            print(i.fid, i.size)
            if i.fid % 2:
                odd_size += i.size
            else:
                even_size += i.size
        print("odd", odd_size, "even", even_size)
