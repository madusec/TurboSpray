#!/usr/bin/python3

from core.all_modules import *

#############################################
# Extract

try:
	proxies_list = []
	filename = 'proxies.txt'

	url = 'https://cagriari.com/fresh_proxy.txt'

	r = requests.get(url).text
	soup = bs(r, 'lxml')
	raw_list = soup.text.split('\n')[3:]
	for raw_proxy in raw_list:
		proxy = raw_proxy.split('|')[0]
		if proxy != '':
			proxies_list.append(proxy)
	proxies_list = list(set(proxies_list))

	print(f'[+] {len(proxies_list)} proxies found on: {url}')

	with open(filename, 'w') as f:
		for proxy in proxies_list:
			f.write(proxy)
			f.write('\n')
		f.close()

	print(f'[+] All proxies have been written into [{filename}]')

except KeyboardInterrupt:
	print('\n[!] Keyboard interrupted')
	sys.exit()

print(colored('\n[!] Exit for List [E] | Continue for Validation [C]', 'blue'))
choice = input(colored('[*] Choose E or V \n>>> ', 'blue'))
if choice.lower() == 'e':
	sys.exit()
elif choice.lower() == 'c':
	pass

#############################################
# Validate

def test_them(filename):
	
	with open(filename) as f:
		proxies_list = f.read().splitlines()
		f.close()
	
	total = len(proxies_list)
	count = 1
	working = 0

	print('\n[+] Slow validation...')
	open('tested_proxies.txt', 'w')

	target = 'https://google.com'
	timeout = 5

	try:
		for PROXY in proxies_list:
			try:
				proxies = {'https' : f'https://{PROXY}'}
				r = requests.get(target, proxies=proxies, timeout=timeout)
				working += 1
				print(colored(f'[{count}/{total}] | {PROXY} -- Good -- Status code={r.status_code} -- [+{working}]', 'green'))
				with open('tested_proxies.txt', 'a') as f:
					f.write(PROXY)
					f.write('\n')
					f.close()
			except ConnectionError:
				print(colored(f'[{count}/{total}] | {PROXY} -- Bad -- [ConnectionError]', 'red'))
				pass
			except ProxyError:
				print(colored(f'[{count}/{total}] | {PROXY} -- Bad -- [ProxyError]', 'red'))
				pass
			except SSLError:
				print(colored(f'[{count}/{total}] | {PROXY} -- Bad -- [SSLError]', 'red'))
				pass
			except(ReadTimeout, ConnectTimeout,):
				print(colored(f'[{count}/{total}] | {PROXY} -- Bad -- [Timeout]', 'red'))
				pass
			count += 1

	except KeyboardInterrupt:
		print('\n[!] Keyboard interrupted')
		sys.exit()
	
test_them(filename)
print('[*] Done')