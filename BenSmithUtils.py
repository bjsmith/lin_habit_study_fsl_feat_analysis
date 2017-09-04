import csv
from datetime import datetime

# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 11:51:08 2015

@author: ben
"""


def get_csv_dict(file_location, fields_to_keep, delimiter='\t'):
    ret_list = []
    with open(file_location, 'rb') as csvfile:
        dict_reader = csv.DictReader(csvfile, delimiter=delimiter, quotechar='"')
        for row in dict_reader:
            row_d = {}
            for field in fields_to_keep: row_d[field] = row[field]
            ret_list.append(row_d)
            # ret_list.append(row)
    return (ret_list)

def vprint(str):
    if 'verbose' in vars():
        if(verbose):
            print(str)



def get_timestamp():
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
