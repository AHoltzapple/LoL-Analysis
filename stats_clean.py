# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 19:07:53 2020

@author: arshl
"""

import pandas as pd
import time
import re
import numpy as np


merged_df = pd.read_csv('C:\\Users\\arshl\\Dropbox\\github\\UGG LoL\\merged_df.csv', index_col='matchnum')

merged_df['killpct'] = merged_df['killpct'].str.replace('%','', regex=True)
merged_df[['kills','deaths','assists','level','csscore','killpct']] = merged_df[['kills','deaths','assists','level','csscore','killpct']].apply(pd.to_numeric)
merged_df['duration'] = pd.to_datetime(merged_df['duration'],format='%M:%S').dt.time
