#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 16:28:13 2022

@author: craig
"""
import pandas as pd
ns = {'20' : "/home/craig/workspace/taa_processor/TAA24-28_Modeling_Results.xlsx",
      '25' : "/home/craig/workspace/taa_processor/TAA24-28_Modeling_Results.xlsx"}

def load_frames(run_dict):
    new_dict= {}
    for run in run_dict.keys():
        df= pd.read_excel(run_dict[run], "combined")
        df[run]=df['STR'].cumsum()
        df=df[["SRC", run]]
        new_dict[run]= df.drop_duplicates('SRC', ignore_index=True)
    return new_dict

f = load_frames(ns)

import functools as ft
df_final = ft.reduce(lambda left, right: pd.merge(left, right, on='SRC'), f.values())
df_final.to_excel('/home/craig/workspace/compare_one-to-n/output.xlsx')