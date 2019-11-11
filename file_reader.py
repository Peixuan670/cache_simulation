#!/usr/bin/env python

# encoding: utf-8

# @author: Durand Wang

# @file: file_reader.py

# @time: 2019/11/10 16:27

import numpy as np
import pandas as pd


def df_reader_msr(file_path):
    """
    the part of last dash line indicate the trace origin, now we only have msr(microsoft)
    :param file_path:
    :return: dataframe of trace
    """
    df = pd.read_csv(file_path, header=None)
    df.columns = ['Timestamp', 'Hostname', 'DiskNumber', 'Type', 'Offset', 'Size', 'ResponseTime']
    df['Timestamp'] = df['Timestamp'].astype(np.int64)
    return df.sort_values(by='Timestamp')
