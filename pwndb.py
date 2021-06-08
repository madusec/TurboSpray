#!/usr/bin/python3

# https://github.com/davidtavarez/pwndb
# added tor, csv output and split option

# Modules & Functions
from core.all_modules import *
from core.all_functions import * 

# Colors
G, B, R, W, M, C, end = '\033[92m', '\033[94m', '\033[91m', '\x1b[37m', '\x1b[35m', '\x1b[36m', '\033[0m'
info = end + W + "[-]" + W
good = end + G + "[+]" + C
bad = end + R + "[" + W + "!" + R + "]"

def main(emails, proxies, output=None):
	if not output:
		print(info + " Searching for leaks...")

	results = []
	emails_list = [] ; passwords_list = []


	for email in emails:
		leaks = find_leaks(email.strip(), proxies)
		if leaks:
			for leak in leaks:
				results.append(leak)

	if not results:
		if not output:
			print(bad + " No leaks found." + end)

	# Different file types | Split emails from passwords (each one in different file)
	if not args.split and output == 'txt':
		open('leaked.txt', 'w') 
	if args.split == 'e' and output == 'txt':
		open('leaked_emails.txt', 'w')
	if args.split == 'p' and output == 'txt':
		open('leaked_passwords.txt', 'w')

	if not args.split and output == 'csv':
		open('leaked.csv', 'w') 
	if args.split == 'e' and output == 'csv':
		open('leaked_emails.csv', 'w')
	if args.split == 'p' and output == 'csv':
		open('leaked_passwords.csv', 'w')

	if not args.split and output == 'json':
		open('leaked.json', 'w')

	# TXT / no output
	if not output or output == 'txt':
		for result in results:
			username = result.get('username', '') 
			domain = result.get('domain', '') 
			password = result.get('password', '') 

			emails_list.append(username + "@" + domain)
			passwords_list.append(password)
			
			# No output selected, returns results in terminal
			if not output:
				print(good + "\t" + username + "@" + domain + ":" + password)
			
			# TXT output
			if output == 'txt':
				print(username + "@" + domain + ":" + password)

				# Emails + Passwords
				if not args.split:
					with open('leaked.txt', 'a') as f:
						f.write(username + "@" + domain + ":" + password)
						f.write('\n')
				
				# Emails
				if args.split == 'e':
					with open('leaked_emails.txt', 'a') as f:
						f.write(username + "@" + domain)
						f.write('\n')

				# Passwords
				if args.split == 'p':
					with open('leaked_passwords.txt', 'a') as f:
						f.write(password)
						f.write('\n')

	# CSV Output
	if output == 'csv':
		for result in results:
			username = result.get('username', '') 
			domain = result.get('domain', '') 
			password = result.get('password', '') 

			emails_list.append(username + "@" + domain) 
			passwords_list.append(password) 

			print(username + "@" + domain + ":" + password)

		# Emails + Passwords 
		if not args.split:
			a = {'Usernames' : emails_list ,'Passwords' : passwords_list}
			df = pd.DataFrame(a, columns=['Usernames', 'Passwords'])
			df.to_csv('leaked.csv', mode='a', header=False, index=None)
		
		# Emails
		if args.split == 'e':
			a = {'Usernames' : emails_list}
			df = pd.DataFrame(a, columns=['Usernames'])
			df.to_csv('leaked_emails.csv', mode='a', header=False, index=None)
		
		# Passwords
		if args.split == 'p':
			a = {'Passwords' : passwords_list}
			df = pd.DataFrame(a, columns=['Passwords'])
			df.to_csv('leaked_passwords.csv', mode='a', header=False, index=None)
	
	# JSON Output 
	if output == 'json':
		print(json.dumps(results, indent=4, sort_keys=True))
		with open('leaked.json', 'a') as f:
			f.write(json.dumps(results, indent=4, sort_keys=True))
			f.write('\n')
			f.close()

def find_leaks(email, proxies):
	s = requests.Session()
	url = "http://pwndb2am4tzkvold.onion/"
	username = email
	domain = "%"

	if "@" in email:
		username = email.split("@")[0]
		domain = email.split("@")[1]
		if not username:
			username = '%'

	request_data = {'luser': username, 'domain': domain, 'luseropr': 1, 'domainopr': 1, 'submitform': 'em'}

	r = s.post(url, data=request_data, proxies=proxies)

	return parse_pwndb_response(r.text)


def parse_pwndb_response(text):
	if "Array" not in text:
		return None

	leaks = text.split("Array")[2:]
	emails = []

	for leak in leaks:
		leaked_email = ''
		domain = ''
		password = ''
		try :
			leaked_email = leak.split("[luser] =>")[1].split("[")[0].strip()
			domain = leak.split("[domain] =>")[1].split("[")[0].strip()
			password = leak.split("[password] =>")[1].split(")")[0].strip()
		except:
			pass
		if leaked_email:
			emails.append({'username': leaked_email, 'domain': domain, 'password': password})
	return emails


if __name__ == '__main__':

	# Parameters
	parser = argparse.ArgumentParser(prog='pwndb.py')
	parser.add_argument("-t", "--target", help="Target email/domain to search for leaks.")
	parser.add_argument("-s", "--split", type=str, help="Output only Email or Password with 'e' or 'p'")
	parser.add_argument("-l", "--list", help="A list of emails in a file to search for leaks.")
	parser.add_argument("-o","--output", help="Return results in JSON, CSV or TXT")
	parser.add_argument("-anonsurf", action='store_true', help="Tor is activated automatically, if you want anonsurf (system-wide) then use this parameter.")
	args = parser.parse_args()

	banner()
	print('Additions to https://github.com/davidtavarez/pwndb\n')

	# Tor option
	if not args.anonsurf:
		print('[+] Setting up Tor...')
		os.system('sudo service tor restart')
		sleep(5)
		proxies = {'http': 'socks5h://localhost:9050'}
		get_current_ip()
		print('')

	# Anonsurf Autostart
	elif args.anonsurf:
		print('[+] Setting up Anonsurf...')
		proxies = False
		tor = subprocess.run(['sudo', 'anonsurf', 'start'], capture_output=True)
		while True:
			try:
				print(f'[*] Your current IP: {requests.get("https://api.ipify.org").text}')
			except:
				print("[!] Failed - Trying again...")
				tor = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
				continue
			break
		print('[*] Anonsurf activated')

	if not args.list and not args.target:
		parser.print_help()
		print(bad + " Missing parameters!" + end)
		exit(-1)

	emails = []

	# Choose Output: JSON, CSV, TXT
	output = None
	if args.output:
		if args.output not in ['json', 'csv', 'txt']:
			print(bad + " Output should be JSON, CSV or TXT" + end)
			exit(-1)
		output = args.output

	if args.target:
		emails.append(args.target)

	if args.list:
		try:
			lines = open(args.list).readlines()
			for line in lines:
				for input in line.split(','):
					addresses = getaddresses([input])
					for address in addresses:
						emails.append(str(addresses[0][1]).strip())
		except Exception as e:
			print(bad + " Can't read the file: " + str(args.list))
			exit(-1)
	try:
		main(emails, proxies, output)
	except ConnectionError:
		print(bad + " Can't connect to service! restart tor service and try again.")
	except Exception as e:
		print(bad + " " + str(e))
	except KeyboardInterrupt:
		if args.anonsurf:
			print('\n[-] Stopping Anonsurf')
			subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True)
		print('[*] Finished')
		sys.exit()

	if args.anonsurf:
		# Tor autostop
		print('[-] Stopping Anonsurf')
		subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True)
		print('[*] Finished')