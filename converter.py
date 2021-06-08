#!/usr/bin/python3

# Modules & Functions
from core.all_modules import *
from core.all_functions import * 

# Empty lists
names_list = []
format_list = []

# Colors
G, B, R, W, M, C, end = '\033[92m', '\033[94m', '\033[91m', '\x1b[37m', '\x1b[35m', '\x1b[36m', '\033[0m'
bad = end + R + "[" + W + "!" + R + "]"

banner()

if __name__ == '__main__':

	# Parameters
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--Input", type=str, help="Old usernames file name")
	parser.add_argument("-f", "--format",help=r'Desired format | Ex: Full Name to DOMAIN/{first}{m}{l}')
	parser.add_argument("-n", "--name", type=str, default="formatted_names", help="Output name")
	parser.add_argument("-o", "--output", type=str, default="txt", help="Output type")
	args = parser.parse_args()

	if not args.Input:
		parser.print_help()
		print(bad + " Missing parameters!" + end)
		exit(-1)

	# Variables
	if args.Input:
		Input = args.Input

	if args.format:
		format_ = args.format
	else:
		parser.print_help()
		print(bad + " Missing parameters!" + end)
		exit(-1)

	# Input List > Python list
	with open(Input) as r:
		names = r.readlines()
		for name in names:
			if '@' in name:
				names_list.append(name.replace('\n','').split('@')[0])
			else:
				names_list.append(name.replace('\n',''))

	for a in names_list:

		if '.' in a: splitted = a.split('.')
		elif " " in a: splitted = a.split(' ')

		for x in splitted:
			if x == "": splitted.remove(x)

		if len(splitted) == 2:
			FORMAT = format_
			if '{f}' in format_: FORMAT = FORMAT.replace('{f}', splitted[0][0])
			if '{first}' in format_: FORMAT = FORMAT.replace('{first}', splitted[0])
			FORMAT = FORMAT.replace('{m}', '')
			FORMAT = FORMAT.replace('{middle}', '')
			if '{l}' in format_: FORMAT = FORMAT.replace('{l}', splitted[1][0])
			if '{last}' in format_: FORMAT = FORMAT.replace('{last}', splitted[1])
			
		elif len(splitted) == 3:
			FORMAT = format_
			if '{f}' in format_: FORMAT = FORMAT.replace('{f}', splitted[0][0])
			if '{first}' in format_: FORMAT = FORMAT.replace('{first}', splitted[0])
			if '{m}' in format_: FORMAT = FORMAT.replace('{m}', splitted[1][0])
			if '{middle}' in format_: FORMAT = FORMAT.replace('{middle}', splitted[1])
			if '{l}' in format_: FORMAT = FORMAT.replace('{l}', splitted[2][0])
			if '{last}' in format_: FORMAT = FORMAT.replace('{last}', splitted[2])
			#
		elif len(splitted) == 4:
			FORMAT = format_
			if '{f}' in format_: FORMAT = FORMAT.replace('{f}', splitted[0][0])
			if '{first}' in format_: FORMAT = FORMAT.replace('{first}', splitted[0])
			if '{m}' in format_: FORMAT = FORMAT.replace('{m}', f'{splitted[1][0]}{splitted[2][0]}')
			if '{middle}' in format_: FORMAT = FORMAT.replace('{middle}', f'{splitted[1]}{splitted[2]}')
			if '{l}' in format_: FORMAT = FORMAT.replace('{l}', splitted[3][0])
			if '{last}' in format_: FORMAT = FORMAT.replace('{last}', splitted[3])

		if '..' in FORMAT:
			FORMAT = FORMAT.replace('..', '.')
		format_list.append(FORMAT)

	if args.name and args.output:
		output = args.name + '.' + args.output

	# Output
	# TXT
	if args.output == 'txt':
		open(output, 'w').close()
		for a in format_list:
			with open(output, 'a') as f:
				f.write(a)
				f.write('\n')

	# CSV
	elif args.output == 'csv':
		a = {'Names' : format_list}
		df = pd.DataFrame(a, columns=['Names'])
		df.to_csv(output, mode='a', header=False, index=None)

	# JSON
	elif args.output == 'json':
		with open(output, 'a') as f:
			f.write(json.dumps(format_list, indent=4, sort_keys=True))

	print(f'\n[*] File created: {output}')