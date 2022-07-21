#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 16:28:13 2022

@author: craig
"""
import pandas as pd
import functools as ft

def load_frames(run_dict, supp_demand_path, interests_path):
    supply_demand=pd.read_excel(supp_demand_path, "SupplyDemand")
    new_dict= {}
    for run in run_dict.keys():       
        df= pd.read_excel(run_dict[run], "combined")
        df[run]=df['STR'].cumsum()
        if len(new_dict)==0:
            df_small=df[["SRC", "STR"]]
            interests = pd.read_excel(interests_path)
            df_small=df_small.merge(interests, on='SRC', how='right')
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

def summary_table(run_dict, 
                  supp_demand_path, 
                  interests_path, 
                  output_path):
    f = load_frames(run_dict, 
                  supp_demand_path, 
                  interests_path)
    df_final = ft.reduce(lambda left, right: pd.merge(left, right, on='SRC'), f.values())
    df_final.to_excel(output_path)

#scatterplot
