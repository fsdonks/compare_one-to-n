#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:07:44 2022

@author: craig
"""
import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('/home/craig/workspace/compare_one-to-n/')
import core as core

supp_demand_path = "/home/craig/workspace/compare_one-to-n/SupplyDemand.xlsx"
interests_path = "/home/craig/workspace/compare_one-to-n/interesting_srcs.xlsx"
run_dict = {'variable' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx",
      '20' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx",
      '25' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx"}
output_path='/home/craig/workspace/compare_one-to-n/output.xlsx'



core.compute_cuts(run_dict, 
                  supp_demand_path, 
                  interests_path, 
                  40000)

core.summary_table(run_dict, 
                  supp_demand_path, 
                  interests_path, 
                  output_path)