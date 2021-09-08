#!/usr/bin/env python

'''
sends each line of a text file to ingest queue
run:
    bin/enqueue-committees.py    <FILE_NAME>
eg:
    bin/enqueue-committees.py ./Missing-committee_details-8.31.21.csv

where ./Missing-committee_details-8.31.21.csv is a files containing committee IDs seperated by newlines
'''

import json
import sys

# hack to import local module
from os import path
sys.path.append(path.join(path.dirname(__file__), '..'))
from src.OpenFec import OpenFec


args = sys.argv
args.pop(0)
txt_files = args

openFec = OpenFec('cRmnh74ydBtUWOUpgnPztjroHhRbR9GlVpNsm4jJ')


def process_file(txt_file):
    with open(txt_file, 'r') as fh:
        for line in fh:
            committee_id = line.strip()
            route = f'/committee/{committee_id}/'
            print(route)
            committee_data = openFec.get_route_paginator(route)
            i=0
            for datum in committee_data:
                with open(f'committees/{committee_id}-{i}.json', 'w') as of:
                    of.write(datum)
                i += 1

            route = f'/committee/{committee_id}/filings/?form_category=STATEMENT'
            print(route)
            committee_filings = openFec.get_route_paginator(route)
            j=0
            for filing in committee_filings:
                with open(f'committees/{committee_id}-filing-{j}.json', 'w') as of:
                    of.write(filing)
                j += 1


for tfile in txt_files:
    print(f'processing {tfile}')
    process_file(tfile)
