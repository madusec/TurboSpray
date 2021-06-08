#!/usr/bin/python3

# Modules & Functions
from core.all_modules import *
from core.all_functions import * 

# Colors
G, B, R, W, M, C, end = '\033[92m', '\033[94m', '\033[91m', '\x1b[37m', '\x1b[35m', '\x1b[36m', '\033[0m'
info = end + W + "[-]" + W
good = end + G + "[+]" + C
bad = end + R + "[" + W + "!" + R + "]"

banner()

if __name__ == '__main__':

	# Arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-x", "--option", type=int, help="option 1 - generate new password list | option 2 - filter known password list | option 3 - hashcat")
	parser.add_argument("-c", "--company", type=str, help="[1|2|3] Target company to include in passwords")
	parser.add_argument("-m", "--month", type=str, help="[1|2|3] Month to include in top 10 passwords")
	parser.add_argument("-y", "--year", type=int, help="[1|2|3] Year to include in top 10 passwords")
	parser.add_argument("-s", "--special", type=str, help="[1] Special Characters to include in passwords")
	parser.add_argument("-l", "--lines", type=int, help="[1] Lines number")
	parser.add_argument("-f", "--file", type=str, help="[2] Filter known password list")
	parser.add_argument("-L", "--MIN_LETTERS", type=int, help="[2] MIN_LETTERS")
	parser.add_argument("-N", "--MIN_NUMBERS", type=int, help="[2] MIN_NUMBERS")
	parser.add_argument("-C", "--MIN_CARACTERS", type=int, help="[2] MIN_CARACTERS")
	parser.add_argument("-n", "--name", type=str, default="passwords", help="Output file name")
	parser.add_argument("-o", "--output", type=str, default="txt", help="Output type: TXT-CSV-JSON")
	args = parser.parse_args()

	if not args.option and args.company:
		parser.print_help()
		print(bad + " Missing parameters!" + end)
		exit(-1)

	# New variables
	if args.name and args.output:
		output = args.name + '.' + args.output

	company = args.company
	special = args.special		

	# Empty lists
	option1_list = [] ; option2_list = []

	month = args.month
	year = args.year

	if not args.month or args.year:
		now = datetime.now()
		year = now.strftime("%Y")
		month = now.strftime("%B")

	list_of_lines = ['P@ssw0rd','Welkom123!','Welkom01!',f'{company.capitalize()}01',f'{company.capitalize()}01!',f'{month.capitalize()}{year}',f'{month.capitalize()}{year}!','Welkom02!','Welkom03!','Welkom04!']

	# Option 1
	if args.option == 1:

		if args.lines:
			lines = args.lines
			range_ = lines 
			a = 1

			for b in list_of_lines:
				option1_list.append(b)

			# Generate passwords with limited lines/range
			while a < lines:
				for i in ["%.2d" % i for i in range(range_)]:
					option1_list.append(company+i+special)
					a += 1

			# Write to TXT
			if args.output == 'txt':
				with open(output , 'w') as f:
					for i in option1_list:
						f.write(i)
						f.write('\n')

			# Write to CSV
			elif args.output == 'csv':
				a = {'Passwords' : option1_list}
				df = pd.DataFrame(a, columns=['Passwords'])
				df.to_csv(output, mode='a', header=False, index=None)

			# Write to JSON
			elif args.output == 'json':
				with open(output, 'a') as f:
					f.write(json.dumps(option1_list, indent=4, sort_keys=True))

			# Message
			print("[*] Wordlist created")

	# Option 2: Filtering known Password List		
	elif args.option == 2:

		# Variables
		special_caracters = ['~','`','!','@','#','$','%','^','&','*','(',')','-','_','+','=','{','}','[',']','|','/',':',';','"',"'",'<','>','.',',','?']
		if args.file:
			file = args.file
		
		if args.MIN_LETTERS:
			MIN_LETTERS = args.MIN_LETTERS
		else:
			MIN_LETTERS = 1
		
		if args.MIN_NUMBERS:
			MIN_NUMBERS = args.MIN_NUMBERS
		else:
			MIN_NUMBERS = 1
		
		if args.MIN_CARACTERS:
			MIN_CARACTERS = args.MIN_CARACTERS
		else:
			MIN_CARACTERS = 1

		# Overwrite if the file already existed
		open(output, 'w')

		encoding1 = 'latin-1'
		encoding2 = 'utf-16'

		# Filtering
		with open(file, encoding=encoding1) as f:
			print('[*] Working on a filtered list based on the password policy...\n')
			# Work with each line from the file that needs filtering
			all_passwords = f.read().splitlines()

			for a in list_of_lines:
				option2_list.append(a)

			num = 0 ; total = len(all_passwords)
			list__ = [10,20,30,40,50,60,70,80,90,100]
			previous = 0
			for line in all_passwords:
				num += 1
				progress = (num/total)*100
				progress = int(progress)
				if progress in list__ and progress != previous :
					previous = progress
					print(f'Progress : {progress} %')

				# Counts/Empty string
				letter_count = 0
				number_count = 0
				caracter_count = 0
				filtered_word = ''

				for c in line:

					# Filer only letters 
					if c.isalpha() :
						filtered_word += c
						letter_count += 1

					# Filter only numbers 
					elif c.isdigit() :
						filtered_word += c
						number_count += 1

					# Filter only special caracters (@/*)
					elif c in special_caracters :
						filtered_word += c
						caracter_count += 1

				# Apply the rule of minimium number of letters/numbers/caracters and then add them into a list to save them later on a file
				if letter_count >= MIN_LETTERS and number_count >=  MIN_NUMBERS and caracter_count >= MIN_CARACTERS :
					option2_list.append(filtered_word)

			# Write to TXT
			if args.output == 'txt':
				with open(output , 'a') as new:
					for i in option2_list:
						new.write(i)
						new.write('\n')

			# Write to CSV
			elif args.output == 'csv':
				a = {'Passwords' : option2_list}
				df = pd.DataFrame(a, columns=['Passwords'])
				df.to_csv(output, mode='a', header=False, index=None)

			# Write to JSON
			elif args.output == 'json':
				with open(output, 'a') as f:
					f.write(json.dumps(option2_list, indent=4, sort_keys=True))

		# Message
		print(f"[*] {output} ---> Created\n")

	# Option 3: Hashcat Generation
	elif args.option == 3 :

		# New variables
		if args.company:
			print(f'[+] Company: {args.company}')
			print(f'[+] Output: {args.output}')

			with open(output , 'a') as new:
				for a in list_of_lines:
					new.write(a)
					new.write('\n')

			os.system(f'echo "{args.company}" | hashcat -r core/OneRuleToRuleThemAll.rule --stdout >> {output}')
			print('[*] Done')
			print(f'[+] New passwords added to {output}')