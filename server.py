from collections import OrderedDict


# 服务器(cache)
class Server:
    def __init__(self, space):
        self.space = space      # cache size
        self.remain = space     # cache remaining free space
        self.cache = OrderedDict()  # OrderDict() simulate LRU cache
        self.hit_count = 0      # 命中次数
        self.hit_byte = 0
        self.miss_count = 0     # 未命中次数
        self.miss_byte = 0

    def _hit(self, fid, size):
        self.hit_count += 1
        self.hit_byte += size
        self.cache.move_to_end(fid)

    def _miss(self, fid, size):
        self.miss_count += 1
        self.miss_byte += size
        if size <= self.space:
            while self.remain < size:
                self.remain += self.cache.popitem(last=False)[-1]  # pop出第一个item
            self.cache[fid] = size
            self.remain -= size

    # handle on request
    def handle(self, fid, size):
        if fid in self.cache.keys():
            self._hit(fid, size)
        else:
            self._miss(fid, size)

    def hit_rate(self):
        try:
            return self.hit_count / (self.hit_count + self.miss_count)
        except:
            return 0

    def byte_hit_rate(self):
        try:
            return self.hit_byte / (self.hit_byte + self.miss_byte)
        except:
            return 0