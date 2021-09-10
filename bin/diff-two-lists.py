#!/usr/bin/env python3


import sys


file1_name = sys.argv[1]
file2_name = sys.argv[2]

def get_lines(file_name):
	print('\n' + file_name)
	with open(file_name, 'r') as fh:
		file_lines = [l.strip() for l in fh]
	print(f'len: {len(file_lines)}')
	print(f'uniq: {len(set(file_lines))}')
	return file_lines



file1_lines = get_lines(file1_name)
file2_lines = get_lines(file2_name)


diff = list(set(file2_lines) - set(file1_lines))

print(diff)
