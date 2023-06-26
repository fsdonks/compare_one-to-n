#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:07:44 2022

@author: craig
"""

from pathlib import Path

import sys
if '__file__' in globals():
    repo_path=str(Path(__file__).parent)
else: 
    repo_path='/home/craig/workspace/make-one-to-n'
    
repo_path=repo_path+'/'
sys.path.append(repo_path)

import core as core

supp_demand_path = repo_path+"SupplyDemand.xlsx"
interests_path = repo_path+"interesting_srcs.xlsx"
run_dict = {core.variable_name : repo_path+"1-n.xlsx",
      '20' : repo_path+"1-n.xlsx",
      '25' : repo_path+"1-n.xlsx"}
first_cuts_output=repo_path+'first_cuts.xlsx'
total_cuts_table=repo_path+'total_cuts.xlsx'


core.spit_cuts(run_dict, 
                  supp_demand_path,                  
                  [40000, 20000], total_cuts_table, interests_path,)


core.summary_table(run_dict, 
                  supp_demand_path,  
                  first_cuts_output, interests_path,)