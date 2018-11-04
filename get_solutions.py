import os
import requests
import lxml
from getpass import getpass
from bs4 import BeautifulSoup
from contextlib import contextmanager

lang = {'C': '.c', 'C++': '.cpp', 'CPP14': '.cpp', 'JAVA': '.java',
		'PYTHON3': '.py', 'PYPY': '.py', 'C++ 4.3.2': '.cpp', 'CPP': '.cpp'
		}

@contextmanager
def login(username, password):
	ses = requests.session()
	ses.post('https://www.spoj.com/login', data={
		'login_user': username,
		'password': password
		})
	yield ses

@contextmanager
def change_dir(destination):
	try:
		cwd = os.getcwd()
		if os.path.exists(cwd + "/" + destination):	
			os.chdir(destination)
		else:
			os.mkdir(destination)
			os.chdir(destination)
		yield
	finally:
		os.chdir(cwd)


def get_solved_problems(soup):
	solved_problems = set()
	tab = soup.find('table', class_='table')
	for tr in soup.find('table', class_='table'):
		for tr in tab.find_all('tr'):
			for td in tab.find_all('td'):
				if td.a.text != '':
					solved_problems.add(td.a.text)
	return solved_problems

def get_ac_id(soup):
	for tr in soup.find_all('tr'):
		# print(tr)
		sol_status = tr.find('td', class_='statusres text-center')
		if sol_status != None and sol_status['status'] == '15':
			ac_lang = tr.find('td', class_='slang').find('span').text
			ac_id = tr.find('td', class_='statustext').text
			print(ac_lang.strip(), ac_id.strip())
			return (ac_lang.strip(), ac_id.strip())



if __name__ == '__main__':
	username = input("username: ")
	password = getpass("password: ")
	with login(username, password) as session:
		
		content = session.get('https://www.spoj.com/myaccount')
		soup = BeautifulSoup(content.text, "lxml")
		solved_problems = get_solved_problems(soup)
		
		for problem in solved_problems:
			url = 'https://www.spoj.com/status/' + problem + ',' + username
			cont = session.get(url)
			soup2 = BeautifulSoup(cont.text, 'lxml')
			print(problem + ":\n")
			ac_lang, ac_id = get_ac_id(soup2)
		
			with change_dir("spoj_solutions"):
				filename = problem + lang[ac_lang]
				print("Downloading {}...". format(filename))
				with open(filename, "w") as solution:
					solution.write(session.get('https://www.spoj.com/files/src/save/{sol_id}'.format(sol_id=ac_id)).text)
