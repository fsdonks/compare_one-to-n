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
run_dict = {core.variable_name : "/home/craig/workspace/compare_one-to-n/1-n.xlsx",
      '20' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx",
      '25' : "/home/craig/workspace/compare_one-to-n/1-n.xlsx"}
first_cuts_output='/home/craig/workspace/compare_one-to-n/first_cuts.xlsx'
total_cuts_table='/home/craig/workspace/compare_one-to-n/total_cuts.xlsx'


core.spit_cuts(run_dict, 
                  supp_demand_path, 
                  interests_path, 
                  [40000, 20000], total_cuts_table)


core.summary_table(run_dict, 
                  supp_demand_path, 
                  interests_path, 
                  first_cuts_output)