from collections import OrderedDict


class Server:  # 服务器(cache)
    def __init__(self, space):
        self.space = space  # cache大小
        self.remain = space  # cache剩余空间
        self.cache = OrderedDict()  # OrderDict() 模拟cache LRU方法
        self.hit_count = 0  # 命中次数
        self.miss_count = 0  # 未命中次数

    def _hit(self, key):
        self.hit_count += 1
        self.cache.move_to_end(key)

    def _miss(self, file):
        self.miss_count += 1
        while self.remain < file.size:
            self.remain += self.cache.popitem(last=False)[-1]  # pop出第一个item
        self.cache[file.fid] = file.size
        self.remain -= file.size

    def handle(self, file):  # 处理一次请求
        if file.fid in self.cache.keys():
            self._hit(file.fid)
        else:
            self._miss(file)

    def hit_rate(self):
        try:
            return self.hit_count / (self.hit_count + self.miss_count)
        except:
            return "Server has not been requested yet!"
