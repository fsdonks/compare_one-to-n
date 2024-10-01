#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 16:28:13 2022

@author: craig
"""

import pandas as pd
import functools as ft
import math
import numpy as np

variable_name = 'Variable RC'
default_rc_availability=50

def load_frames(run_dict, supp_demand_path, rc_avail, interests_path=None):
    supply_demand=pd.read_excel(supp_demand_path, "SupplyDemand")
    new_dict= {}
    for run in run_dict.keys():       
        df= pd.read_excel(run_dict[run], "combined")
        #add running total
        df[run]=df['STR'].cumsum()
        if len(new_dict)==0:
            df_small=df[["SRC", "STR", run]]
            if interests_path is not None:
                interests = pd.read_excel(interests_path)
                #make sure interests doesn't have duplicates
                #and filter on interests
                #eventually, change merge so that order is interest, supply demand,
                #and then df_small instead of starting with df_small now.
                df_small=df_small.merge(
                    interests.drop_duplicates('SRC', ignore_index=True), on='SRC')
            df_small=df_small.merge(supply_demand[['SRC', 'RA', 'ARNG', 'USAR']], on='SRC')
            if run==variable_name:
                df_small=df_small.merge(supply_demand[['SRC', 'RCAvailable']], 
                            on='SRC')
                df_small['RC']=df_small['ARNG']+df_small['USAR']
                conditions = [df_small['RC']==0, df_small['RCAvailable']==0]
                choices=[0, df_small['RC'].apply(lambda 
                                                 x: math.floor(x*default_rc_availability/100))]
                df_small['RCAvailable'] = np.select(conditions, choices, 
                                                    default=df_small['RCAvailable'])    
                df_small.rename(inplace=True, 
                  columns={'RCAvailable' : run + '_RC Units Available'})
        else:
            df_small=df.merge(supply_demand[['SRC', 'ARNG', 'USAR']], on='SRC')
            df_small['RC']=df_small['ARNG']+df_small['USAR']
            if(rc_avail):
                run_int=int(run)
            else:
                run_int=default_rc_availability
            df_small[run + '_RC Units Available'] = np.where(df_small['RC']==0, 
                                                             0, df_small['RC'].apply(lambda x: max(1, math.floor(run_int*x//100))))
            df_small.astype({run + '_RC Units Available': 'Int64'}, copy=False)
            df_small=df_small[["SRC", run + '_RC Units Available', run]]
        df_small.rename(inplace=True, columns={run : run + '_1-n position'})
        new_dict[run]= df_small.drop_duplicates('SRC', ignore_index=True)
    return new_dict

def summary_table(run_dict, 
                  supp_demand_path, 
                  output_path,
                  #If none, use the run number
                  rc_avail=None,
                  interests_path=None):
    f = load_frames(run_dict, 
                  supp_demand_path, 
                  rc_avail,
                  interests_path)
    df_final = ft.reduce(lambda left, right: pd.merge(left, right, on='SRC'), f.values())
    df_final.to_excel(output_path)

#Table of cuts by run
#same dict as input
#without src info joins for now
#do cumsum
def compute_cuts(run_dict, supp_demand_path, interests_path, cut_level):
    new_dict= {}
    for run in run_dict.keys():       
        df= pd.read_excel(run_dict[run], "combined")
        #add running total
        df["cumsum"]=df['STR'].cumsum()
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
        #result=cut_records.groupby('SRC').count()
        result=cut_records
        result['run']=run
        result['cut_level']=cut_level
        new_dict[run]=result
    df_final = ft.reduce(lambda left, right: pd.concat([left, right]), new_dict.values())
    return df_final

sort_order_upper = list(reversed([' ',
              variable_name,
              ]))

sort_order_lower = sort_order_upper+['SRC2',
                    'SRC',
                    'Unit',
                    'RA',
                    'ARNG',
                    'USAR',
                    'Variable RC Availability'
              ]


def sorter(sort_order, x):
    enum=enumerate(sort_order)
    positions=dict((j,i) for i,j in enum)
    res=[positions[y]+100 if y in positions else y for y in x ]
    return res

def compute_availability(rc_percentage):
    #if there was any division by 0
    if(math.isnan(rc_percentage) or rc_percentage==0 or
       math.isinf(rc_percentage)):
        rc_percentage=default_rc_availability
    rc_percentage=round(rc_percentage)
    rc_percentage=str(rc_percentage)+'%'
    return rc_percentage

def add_availability_percentage(table):
    table[' ', 'avails']=table[' ', 'RCAvailable']/table[' ', 'RC']*100
    table[' ', 'avails']=table[' ', 'avails'].apply(compute_availability)
    return table

def spit_cuts(run_dict, supp_demand_path, cut_levels, 
              output_path, interests_path=None):
    all_cuts = []
    for c in cut_levels:
        all_cuts.append(compute_cuts(run_dict, 
                                     supp_demand_path, 
                                     interests_path, c))
    df_final = ft.reduce(lambda left, right: pd.concat([left, right]), 
                         all_cuts)
    supply_demand=pd.read_excel(supp_demand_path, "SupplyDemand")
    table=pd.pivot_table(df_final, values='TITLE', index=['SRC'],
                    columns=['run', 'cut_level'], aggfunc='count')
    if interests_path is not None:
        interests = pd.read_excel(interests_path)
                #make sure interests doesn't have duplicates
                #and filter on interests
        supply_demand=supply_demand.merge(
        interests.drop_duplicates('SRC', ignore_index=True), on='SRC')
    supply_demand['SRC2']=supply_demand['SRC'].str[:2]
    #if want to add a branch filter
    #branches=['02', '99']
    #supply_demand=supply_demand[supply_demand['SRC2'].isin(branches)]
    supply_demand=supply_demand[['SRC2', 'SRC', 
                                 'RA', 
                                 'ARNG', 
                                 'USAR', 
                                 'RCAvailable', 'UNTDS']]
    #In order to merge with the pivot table, we need to set index and change 
    #to a MultiIndex
    supply_demand.set_index('SRC', inplace=True)
    supply_demand.columns = pd.MultiIndex.from_product([[' '], supply_demand.columns])
    table=table.merge(supply_demand, left_index=True, right_index=True)
    
    # runs=set([x for x in table.columns.get_level_values(0) if x!=' ' and x!=variable_name])
    table[' ', 'RC']=table[' ', 'ARNG']+table[' ', 'USAR']
    # for run in runs:
    #     rint=int(run)
    #     table[run, 'RC Units Available']= rint*table[' ', 'RC']//100
    #     table.astype({(run, 'RC Units Available'): 'Int64'}, copy=False)
    
    table=add_availability_percentage(table)
    #In order to rename multiindex columns with tupes, we set the column
    #values first.
    table.columns = table.columns.values
    table.columns = pd.MultiIndex.from_tuples(table.rename(columns={(' ', 'avails'): (variable_name, 'Variable RC Availability'),
                                                                    (' ', 'UNTDS') : (' ', 'Unit')}))
    table.drop(columns=[(' ', 'RCAvailable'), (' ', 'RC')], inplace=True)
    table.reset_index(inplace=True, col_level=1)
    table.rename(axis=1, level=0, mapper={'':' '},inplace=True)
    table = table.sort_index(axis=1, key=ft.partial(sorter, sort_order_lower), ascending=[False, True])
    table = table.sort_values((' ', 'SRC'))
    table.to_excel(output_path)
    return table

#scatterplot
