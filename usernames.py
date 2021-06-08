#!/usr/bin/python3

# Modules & Functions
from core.all_modules import *
from core.all_functions import * 

chrome_path = f'{os.getcwd()}/core/chromedriver'

# Colors
G, B, R, W, M, C, end = '\033[92m', '\033[94m', '\033[91m', '\x1b[37m', '\x1b[35m', '\x1b[36m', '\033[0m'
bad = end + R + "[" + W + "!" + R + "]"

banner()

# Parameters
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--company", type=str, required=False, help="Company name")
parser.add_argument("-f", "--format", type=str, help=r"Format the names (ex: {f}.{middle}{last}@domain.com)")
parser.add_argument("-p", "--max_p", type=int, default=20, help="Maximium number of pages to scrape names from | Default: 20")
parser.add_argument("-country", type=str, default="nl", help="Linkedin Country | Default: nl")
parser.add_argument("-anonsurf", action='store_true', help="Activate Anonsurf (Tor) | system-wide (ip-tables)")
parser.add_argument("-tor", action='store_true', help="Activate Tor | within script (rotation per 5 pages)")
parser.add_argument("-l", "--list", type=str, help="Proxy List")
parser.add_argument("-r", "--rotate", type=int, default=5, help="(Only Anonsurf) Number of attempts before IP rotation | Default: 5")
parser.add_argument('-rd', nargs=2, type=int, metavar=('minimum_sleep', 'maximum_sleep'), help="(Google / o365) Randomize the delay between each page in seconds | Ex: -rd 3 10")
parser.add_argument("-x", action='store_true', help="Scrape only Bing (Quick results without Proxy usage)")
parser.add_argument("-n", "--name", type=str, default="names", help="Output name")  
parser.add_argument("-o", "--output", type=str, default="txt", help="Output type")
parser.add_argument("-v", "--verbose", action='store_true', help="Show results + titles on Terminal")
parser.add_argument("-d", "--debug", action='store_true', help="Show errors")
parser.add_argument("-o365", action='store_true', help="Get valid Usernames/Emails from Office 365 login page")
parser.add_argument('-u', '--userlist', required=False, type=str, help='Usernames/Emails list')
args = parser.parse_args()

#os.system('clear')

if not args.company and not args.o365:
	parser.print_help()
	print(bad + " Missing parameters!" + end)
	exit(-1)

UserAgent = UserAgent().random
headers = {'User-Agent': f'{UserAgent}'}

if args.debug:            headless = False
elif args.debug == False: headless = True

# Variables
company = args.company
country = args.country
target = f'https://www.google.com/search?q=site:linkedin.com/in+"{company}"&start=0'
output = f'{args.name}.{args.output}' 

# Open new files with this output name and type selected in the parameters
#os.system(f'sudo touch {output}')
#os.system(f'sudo chmod 777 {output}')

# Overwrite if not empty
f = open(output, 'w').close()

# Max pages
max_p = args.max_p

count = 0 ; rotate_count = 0

# Empty lists
format_names_list = [] ; FINAL_NAMES_LIST = [] ; all_names = []
total_names = 0

if args.list:
	proxy_path = args.list
	with open(proxy_path) as f:
		proxies_list = f.read().splitlines()
		f.close()

try:
	if args.company:
		# Scrape Bing
		print('[*] Scraping Bing...')
		s = requests.Session()
		previous_names = []
		for num in range(0, max_p):
			titles_list = [] ; names_list = [] ; FINAL_NAMES_LIST = [] ; format_names_list = []
			current_names = []
			# bing_url = f'https://www.bing.com/search?q=site%3alinkedin.com%2fin%2f%22{company}%22&qs=n&sp=-1&pq=site%3alinkedin.com%2fin%2f%22{company}%22&sc=0-31&sk=&cvid=A1477CB87C1946A9A7DF537E9F381703&first={num}1&FORM=PERE1'
			# bing_url = f'https://www.bing.com/search?q=site:linkedin.com/in+"{company}"&first={num}'
			bing_url = f'https://www.bing.com/search?q=site:{country}.linkedin.com/in+"{company}"+intitle:{company}&first={num}1'
			r = s.get(bing_url, headers=headers)
			
			soup = bs(r.text, 'lxml') # Parse the source code
			titles = soup.find_all('h2') 
			
			for title in titles:
				try: 
					TITLE = title.find('a').text
					titles_list.append(TITLE)
				except: 
					pass

			for i in titles_list: 
				current_names.append(i)
			if current_names == previous_names:
				if args.verbose: 
					print('[!] Reached Last Page.')
					print('[*] Progress: 100%')
				elif not args.verbose:
					os.system('clear')
					print('[*] Scraping Bing')
					print('[*] Progress: 100%')
				break
			else:
				previous_names = []
				for i in titles_list: 
					previous_names.append(i)

			if args.verbose:
				for TITLE in titles_list: 
					print(TITLE)

			formatting(args, titles_list, names_list, format_names_list, FINAL_NAMES_LIST, output)

			# Progress
			count += 1
			percentage = (count/max_p)*100 
			percentage = str("%.1f" % percentage) + '%' 
			
			if args.verbose: 
				print(f'\n[*] Progress: {percentage}\n')

			elif not args.verbose:
				os.system('clear')
				print('[*] Scraping Bing')
				print(f'[*] Progress: {percentage}')

		if not args.x:
			# Google Scraping

			# Proxies file
			if args.list:
				print(f'[*] Setting up a Proxy...')
				driver, options = proxy_browser(target, headless, proxies_list, args)

			# Tor
			elif args.tor:
				driver, options = tor_browser(headless)

			# Anonsurf
			elif args.anonsurf:
				driver, options = anonsurf_browser(headless)

			# No proxy, No Tor
			else:
				driver, options = no_proxy_browser(headless)

			count = 0

			print('[*] Scraping Google...')
			previous_names = []
			for num in range(0, max_p):
				titles_list = [] ; names_list = []
				current_names = []
				URL = f'https://www.google.com/search?q=site:{country}.linkedin.com/in+"{company}"+intitle:{company}&start={num}'
				
				message = ""
				titles_list = scrape_google(URL, driver, args, company, titles_list, names_list)

				if message == 'captcha': 
					break
				else: 
					pass
				
				formatting(args, titles_list, names_list, format_names_list, FINAL_NAMES_LIST, output)
				
				for i in titles_list: 
					current_names.append(i)
				if current_names == previous_names:
					if args.verbose: 
						print('[!] Reached Last Page.')
						print('[*] Progress: 100%')
					elif not args.verbose:
						os.system('clear')
						print('[*] Scraping Google')
						print('[*] Progress: 100%')
					break
				else:
					previous_names = []
					for i in titles_list: 
						previous_names.append(i)
				
				count += 1
				percentage = (count/max_p)*100
				percentage = str("%.1f" % percentage) + '%'

				# Verbose
				if args.verbose: 
					print(f'[*] Progress: {percentage}')
				
				elif not args.verbose:
					os.system('clear')
					print('[*] Scraping Google')
					print(f'[*] Progress: {percentage}')

				if args.rd:
					delay = round(random.uniform(args.rd[0], args.rd[1]), 3)
					if args.verbose: print(f'[..] Delay for: {delay} s') 
					sleep(delay)

				# Tor | Rotation
				rotate_count += 1

				if args.tor:
					if rotate_count == 5 and percentage != '100.0%':
						rotate_tor()
						rotate_count = 0

				# Anonsurf | Rotation
				if args.rotate:
					if rotate_count == args.rotate and percentage != '100.0%': 

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
								try:    print(f'[*] Your IP after rotating Anonsurf: {requests.get("https://api.ipify.org").text}')
								except:
									print("[!] Sorry, I'am facing difficulties getting the new Tor IP\n") 
									anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
									continue
								break
							driver = start_chrome(target, options=options)
							rotate_count = 0

		# Show how many names have been found
		if args.output == "txt":
			with open(output) as f:
				old = f.read().splitlines()
				total_names = len(old)
				f.close()
		elif args.output == 'csv':
			old = []
			with open(output) as f:
				for line in f:
					old.append(line.split()[0])
				total_names = len(old)
				f.close()
		elif args.output == 'json':
			with open(output) as f:
				old = json.load(f)
				total_names = len(old)
				f.close()

		print(f'\n[+] {total_names} names found')

		try:    kill_browser()
		except: pass

	# Enumeration
	elif args.o365:
		if not args.userlist:
			parser.print_help()
			print(bad + " Missing parameters!" + end)
			exit(-1)		

		valid_emails = []
		print('[*] Accessing Office365...')
		driver = start_chrome('https://www.office.com/', headless=headless)
		print('[*] Getting the login page...')
		click('Sign in')
		print('[*] Enumeration...')
		url = driver.current_url
		with open(args.userlist) as f:
			for a in f.readlines():
				a = a.replace('\n', '')
				go_to(url)
				write(a, into='Email')
				#sleep(0.3)
				click('next')
				sleep(5)
				if Text('Enter Password').exists():
					valid_emails.append(a) 
					print(f'[+++] {a} is valid') 
					#go_to(url)
				elif Text("We couldn't find an account with that username").exists():
					print(f'[-] {a} is not valid')
				
				if args.rd:
					delay = round(random.uniform(args.rd[0], args.rd[1]), 3)
					if args.verbose: print(f'[..] Delay for: {delay} s') 
					sleep(delay)

		kill_browser()
		print('\nFinished.')

		output = f'valid_o365_emails.{args.output}'

		# TXT Output
		if args.output == 'txt':
			f = open(output, 'a')
			for email in valid_emails:
				f.write(email) 
				f.write('\n')

		# CSV Output
		if args.output == 'csv':
				a = {'Emails' : valid_emails}
				df = pd.DataFrame(a, columns=['Emails'])
				df.to_csv(output, mode='a', header=False, index=None)

		# JSON Output
		elif args.output == 'json':
			with open(output, 'a') as f:
				f.write(json.dumps(valid_emails, indent=4, sort_keys=True))

	if args.anonsurf:
		print('[-] Stopping Anonsurf...')
		anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True)

except KeyboardInterrupt:
	print('\n[!] Keyboard interrupted')
	
	if args.anonsurf:
		print('[-] Stopping Anonsurf...')
		anonsurf_subprocess = subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True)

	try:    kill_browser()
	except: pass
	if args.company:
		# Show how many names been found
		if args.output == "txt":
			with open(output) as f:
				old = f.read().splitlines()
				total_names = len(old)
				f.close()
		elif args.output == 'csv':
			old = []
			with open(output) as f:
				for line in f:
					old.append(line.split()[0])
				total_names = len(old)
				f.close()
		elif args.output == 'json':
			with open(output) as f:
				old = json.load(f)
				total_names = len(old)
				f.close()
		print(f'\n[+] {total_names} names found')
		
	sys.exit()