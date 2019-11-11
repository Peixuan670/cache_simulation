#!/usr/bin/env python

# encoding: utf-8

# @author: Durand Wang

# @file: dispatcher.py

# @time: 2019/11/10 14:24

from server import Server
from window import Window

"""
Heat: the sum of file size in a given duration

Caution: call cache function to get the attribute of small cache (such as self.small_cache[0].hit_byte)

"""


class DispatcherTotalHeatNoCountMiss:
    def __init__(self, trace_df, cache_size, cache_number, simple=True):
        '''

        :param trace_df: trace in the form of dataframe
        :param cache_size: the size of each little cache
        :param cache_number: the number of caches in the dispatcher system
        :param simple: True: simple hash strategy, False: load balance strategy
        '''
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
            # Initialize file mapping dictionary with hash
            for row in trace_df.drop_duplicates(['Offset']).itertuples():
                fid = getattr(row, 'Offset')
                self.file_mapper[fid] = (fid // 10000 % 1000000) & 0b11111 % cache_number

    def load_balance(self, fid, size):
        '''

        :param fid: unique file id
        :param size: file size
        :return: none
        '''
        server = self.file_mapper[fid]
        # little caches handle
        if fid in self.small_caches[server].cache.keys():
            self.small_caches[server].handle(fid, size)
            self.small_caches_heat[self.file_mapper[fid]] += size
        else:
            server = self.small_caches_heat.index(min(self.small_caches_heat))
            self.small_caches[server].handle(fid, size)
            self.file_mapper[fid] = server
        # big cache handle
        self.big_cache.handle(fid, size)

    def simple_hash(self, fid, size):
        self.small_caches[(fid // 10000 % 1000000) & 0b11111 % self.cache_number].handle(fid, size)


class DispatcherTotalHeatCountMiss:
    def __init__(self, trace_df, cache_size, cache_number, simple=True):
        '''

        :param trace_df: trace in the form of dataframe
        :param cache_size: the size of each little cache
        :param cache_number: the number of caches in the dispatcher system
        :param simple: True: simple hash strategy, False: load balance strategy
        '''
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
            # Initialize file mapping dictionary with hash
            for row in trace_df.drop_duplicates(['Offset']).itertuples():
                fid = getattr(row, 'Offset')
                self.file_mapper[fid] = (fid // 10000 % 1000000) & 0b11111 % cache_number

    def load_balance(self, fid, size):
        '''

        :param fid: unique file id
        :param size: file size
        :return: none
        '''
        server = self.file_mapper[fid]
        # little caches handle
        if fid in self.small_caches[server].cache.keys():
            self.small_caches[server].handle(fid, size)
        else:
            server = self.small_caches_heat.index(min(self.small_caches_heat))
            self.small_caches[server].handle(fid, size)
            self.file_mapper[fid] = server
        self.small_caches_heat[server] += size
        # big cache handle
        self.big_cache.handle(fid, size)

    def simple_hash(self, fid, size):
        self.small_caches[(fid // 10000 % 1000000) & 0b11111 % self.cache_number].handle(fid, size)


class DispatcherHeatNoCountMissMovingWindow:
    def __init__(self, trace_df, cache_size, cache_number, window_size=10000, simple=True):
        """

        :param trace_df: trace in the form of dataframe
        :param cache_size: the size of each little cache
        :param cache_number: the number of caches in the dispatcher system
        :param window_size: only reserve the heat in the last window_size requests
        :param simple: True: simple hash strategy, False: load balance strategy
        """
        self.cache_number = cache_number
        self.big_cache = Server(cache_size * cache_number)
        self.small_caches = []
        self.small_caches_window = []
        self.small_caches_heat = [0] * cache_number

        for i in range(cache_number):
            server = Server(cache_size)
            self.small_caches.append(server)

        if simple:
            self.handle_requests = self.simple_hash
        else:
            self.handle_requests = self.load_balance
            self.file_mapper = {}
            # Initialize file mapping dictionary with hash
            for row in trace_df.drop_duplicates(['Offset']).itertuples():
                fid = getattr(row, 'Offset')
                self.file_mapper[fid] = (fid // 10000 % 1000000) & 0b11111 % cache_number
            for i in range(cache_number):
                window = Window(window_size)
                self.small_caches_window.append(window)

    def load_balance(self, fid, size):
        server = self.file_mapper[fid]
        if fid in self.small_caches[server].cache.keys():
            self.small_caches[server].handle(fid, size)
            self.small_caches_window[server].put(size)
            self.small_caches_heat[server] = self.small_caches_window[server].sum
        else:
            server = self.small_caches_heat.index(min(self.small_caches_heat))
            self.small_caches[server].handle(fid, size)
            self.file_mapper[fid] = server

        self.big_cache.handle(fid, size)

    def simple_hash(self, fid,  size):
        self.small_caches[(fid // 10000 % 1000000) & 0b11111 % self.cache_number].handle(fid, size)


class DispatcherHeatNoCountMissDecayRate:
    def __init__(self, trace_df, cache_size, cache_number, alpha=0.9999, simple=True):
        '''

        :param trace_df: trace in the form of dataframe
        :param cache_size: the size of each little cache
        :param cache_number: the number of caches in the dispatcher system
        :param alpha: the decay rate of heat for each cache
        :param simple: True: simple hash strategy, False: load balance strategy
        '''
        self.alpha = alpha
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
            # Initialize file mapping dictionary with hash
            for row in trace_df.drop_duplicates(['Offset']).itertuples():
                fid = getattr(row, 'Offset')
                self.file_mapper[fid] = (fid // 10000 % 1000000) & 0b11111 % cache_number

    def load_balance(self, fid, size):
        '''

        :param fid: unique file id
        :param size: file size
        :return: none
        '''
        server = self.file_mapper[fid]
        # reduce heat by time, no matter this time hit or not
        self.small_caches_heat = [i * self.alpha for i in self.small_caches_heat]
        # little caches handle
        if fid in self.small_caches[server].cache.keys():
            self.small_caches[server].handle(fid, size)
            self.small_caches_heat[self.file_mapper[fid]] += size
        else:
            server = self.small_caches_heat.index(min(self.small_caches_heat))
            self.small_caches[server].handle(fid, size)
            self.file_mapper[fid] = server
        # big cache handle
        self.big_cache.handle(fid, size)

    def simple_hash(self, fid, size):
        self.small_caches[(fid // 10000 % 1000000) & 0b11111 % self.cache_number].handle(fid, size)


class DispatcherHeatNoCountMissMovingWindowDecayRate:
    def __init__(self, trace_df, cache_size, cache_number, window_size=10000, alpha=0.9999, simple=True):
        """

        :param trace_df: trace in the form of dataframe
        :param cache_size: the size of each little cache
        :param cache_number: the number of caches in the dispatcher system
        :param window_size: only reserve the heat in the last window_size requests
        :param simple: True: simple hash strategy, False: load balance strategy
        """
        self.cache_number = cache_number
        self.big_cache = Server(cache_size * cache_number)
        self.small_caches = []
        self.small_caches_window = []
        self.small_caches_heat = [0] * cache_number

        for i in range(cache_number):
            server = Server(cache_size)
            self.small_caches.append(server)

        if simple:
            self.handle_requests = self.simple_hash
        else:
            self.handle_requests = self.load_balance
            self.file_mapper = {}
            # Initialize file mapping dictionary with hash
            for row in trace_df.drop_duplicates(['Offset']).itertuples():
                fid = getattr(row, 'Offset')
                self.file_mapper[fid] = (fid // 10000 % 1000000) & 0b11111 % cache_number
            for i in range(cache_number):
                window = Window(window_size, alpha)
                self.small_caches_window.append(window)

    def load_balance(self, fid, size):
        # heat decay
        for i in range(self.cache_number):
            self.small_caches_window[i].decay()
            self.small_caches_heat[i] = self.small_caches_window[i].sum

        server = self.file_mapper[fid]
        if fid in self.small_caches[server].cache.keys():
            self.small_caches[server].handle(fid, size)
            self.small_caches_window[server].put(size)
            self.small_caches_heat[server] = self.small_caches_window[server].sum
        else:
            server = self.small_caches_heat.index(min(self.small_caches_heat))
            self.small_caches[server].handle(fid, size)
            self.file_mapper[fid] = server

        self.big_cache.handle(fid, size)

    def simple_hash(self, fid,  size):
        self.small_caches[(fid // 10000 % 1000000) & 0b11111 % self.cache_number].handle(fid, size)
