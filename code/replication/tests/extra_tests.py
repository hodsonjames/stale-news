# extra_tests.py
# -------
# Tests for some functions in utils_direct.py
import utils_direct as ud

"""
Test: firm_size_quintile functionality
"""
mc_dict = {'AEHR': 32623937.5, 'CRZO': 28022000.0, 'CLDN': 46662000.0, 'HME': 528310125.0, 'BLSC': 30480000.0,
           'NEB': 327324375.0, 'USAM': 1031062.5, 'IGLD': 460800000.0, 'NIO': 1002424500.0, 'PSBI': 20704625.0}
mc_list = [1031062.5, 20704625.0, 28022000.0, 30480000.0, 32623937.5, 46662000.0, 327324375.0, 460800000.0, 528310125.0,
           1002424500.0]
print("Expected: 1 Actual: " + str(ud.firm_size_quintile(mc_dict['USAM'], mc_list)))
print("Expected: 1 Actual: " + str(ud.firm_size_quintile(mc_dict['PSBI'], mc_list)))
print("Expected: 2 Actual: " + str(ud.firm_size_quintile(mc_dict['CRZO'], mc_list)))
print("Expected: 2 Actual: " + str(ud.firm_size_quintile(mc_dict['BLSC'], mc_list)))
print("Expected: 3 Actual: " + str(ud.firm_size_quintile(mc_dict['AEHR'], mc_list)))
print("Expected: 3 Actual: " + str(ud.firm_size_quintile(mc_dict['CLDN'], mc_list)))
print("Expected: 4 Actual: " + str(ud.firm_size_quintile(mc_dict['NEB'], mc_list)))
print("Expected: 4 Actual: " + str(ud.firm_size_quintile(mc_dict['IGLD'], mc_list)))
print("Expected: 5 Actual: " + str(ud.firm_size_quintile(mc_dict['HME'], mc_list)))
print("Expected: 5 Actual: " + str(ud.firm_size_quintile(mc_dict['NIO'], mc_list)))

"""
Test: day_of_week functionality
"""
print("Expected: 4 Actual: " + str(ud.day_of_week("20190927")))
print("Expected: 0 Actual: " + str(ud.day_of_week("20000103")))
print("Expected: 4 Actual: " + str(ud.day_of_week("20080229")))
