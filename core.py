#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 16:28:13 2022

@author: craig
"""
import pandas as pd
ns = {'variable' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx",
      '20' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx",
      '25' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx"}
supply_demand=pd.read_excel("/home/craig/workspace/compare_one-to-n/SupplyDemand.xlsx", "SupplyDemand")

def load_frames(run_dict):
    new_dict= {}
    for run in run_dict.keys():       
        df= pd.read_excel(run_dict[run], "combined")
        df[run]=df['STR'].cumsum()
        if len(new_dict)==0:
            df_small=df[["SRC", "STR"]]
            interests = pd.read_excel("/home/craig/workspace/compare_one-to-n/interesting_srcs.xlsx")
            df_small=df_small.merge(interests, on='SRC', how='left')
            df_small=df_small.merge(supply_demand[['SRC', 'RA', 'ARNG', 'USAR']], on='SRC', how='left')
            if run=='variable':
                df_small=df_small.merge(supply_demand[['SRC', 'RCAvailable']], 
                            on='SRC', how='left')
                df_small.rename(inplace=True, 
                  columns={'RCAvailable' : run + '_RC Units Available'})
        else:
            df_small=df[["SRC"]]
            df_small=df_small.merge(supply_demand[['SRC', 'ARNG', 'USAR']], on='SRC', how='left')
            df_small['RC']=df_small['ARNG']+df_small['USAR']
            df_small[run + '_RC Units Available']= int(run)*df_small['RC']//100
            df_small.astype({run + '_RC Units Available': 'Int64'}, copy=False)
            df_small=df_small[["SRC", run + '_RC Units Available']]
        df_small=df_small.merge(df[['SRC', run]].copy(), on='SRC', how='left')
        df_small.rename(inplace=True, columns={run : run + '_1-n position'})
        new_dict[run]= df_small.drop_duplicates('SRC', ignore_index=True)
    return new_dict

f = load_frames(ns)

import functools as ft
df_final = ft.reduce(lambda left, right: pd.merge(left, right, on='SRC'), f.values())
df_final.to_excel('/home/craig/workspace/compare_one-to-n/output.xlsx')

#scatterplot
