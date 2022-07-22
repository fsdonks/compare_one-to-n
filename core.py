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
        #add running total
        df[run]=df['STR'].cumsum()
        if len(new_dict)==0:
            df_small=df[["SRC", "STR", run]]
            interests = pd.read_excel(interests_path)
            #make sure interests doesn't have duplicates
            #and filter on interests
            df_small=df_small.merge(
                interests.drop_duplicates('SRC', ignore_index=True), on='SRC')
            df_small=df_small.merge(supply_demand[['SRC', 'RA', 'ARNG', 'USAR']], on='SRC')
            if run=='variable':
                df_small=df_small.merge(supply_demand[['SRC', 'RCAvailable']], 
                            on='SRC')
                df_small.rename(inplace=True, 
                  columns={'RCAvailable' : run + '_RC Units Available'})
        else:
            df_small=df.merge(supply_demand[['SRC', 'ARNG', 'USAR']], on='SRC')
            df_small['RC']=df_small['ARNG']+df_small['USAR']
            df_small[run + '_RC Units Available']= int(run)*df_small['RC']//100
            df_small.astype({run + '_RC Units Available': 'Int64'}, copy=False)
            df_small=df_small[["SRC", run + '_RC Units Available', run]]
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

#Table of cuts by run
#same dict as input
#without src info joins for now
#do cumsum
def compute_cuts(run_dict, supp_demand_path, interests_path, cut_level):
    supply_demand=pd.read_excel(supp_demand_path, "SupplyDemand")
    new_dict= {}
    for run in run_dict.keys():       
        df= pd.read_excel(run_dict[run], "combined")
        #add running total
        df[run]=df['STR'].cumsum()
        curr_cuts=0
        cut_records=pd.DataFrame()
        num_skipped=0
        for idx,row in df.iterrows():
            if num_skipped==5:
                break
            new_str=row['STR']
            if curr_cuts+new_str - cut_level > 4000:
                num_skipped+=1
                continue
            cut_records = cut_records.append(row)
            curr_cuts+=new_str
            if curr_cuts>cut_level:
                break
        #now have cut_records
        result=cut_records.groupby('SRC').count()
        result=result[[run]]
        result.reset_index(inplace=True)
        new_dict[run]=result
    df_final = ft.reduce(lambda left, right: pd.merge(left, right, on='SRC'), new_dict.values())
    return df_final
#take cuts here in python (ask dallas if there's a standard for that.)
#merge right with their data like above
#them concat each of the values

#scatterplot
