#!/usr/bin/env python

# encoding: utf-8

# @author: Durand Wang

# @file: window.py

# @time: 2019/11/10 15:11


class Window:
    def __init__(self, total_size, alpha=None):
        """

        :param total_size: total size of a window
        """
        self.total_size = total_size
        self.window = [0] * total_size
        self.pointer = 0
        self.sum = 0
        if alpha:
            self.alpha = alpha

    def put(self, size):
        """

        :param size: put a file with size in the window
        :return:
        """
        self.sum -= self.window[self.pointer]
        self.window[self.pointer] = size
        self.sum += size
        self.pointer = (self.pointer + 1) % self.total_size

    def decay(self):
        self.window = [i * self.alpha for i in self.window]
        self.sum *= self.alpha


