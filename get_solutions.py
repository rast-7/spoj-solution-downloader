import os
import requests
import lxml
from getpass import getpass
from bs4 import BeautifulSoup
from contextlib import contextmanager

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
	for tr in soup.find_all('tr'):
		for td in soup.find_all('td'):
			if td.a.text != '':
				solved_problems.add(td.a.text)
	return solved_problems

def get_ac_id(soup):
	ac_id = soup.find('td').a['data-sid']
	return ac_id

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
			ac_id = get_ac_id(soup2)
		
			print("Downloading {}...". format(problem))
			with change_dir("spoj_solutions"):
				filename = problem + ".cpp"
				with open(filename, "w") as solution:
					solution.write(session.get('https://www.spoj.com/files/src/save/{sol_id}'.format(sol_id=ac_id)).text)
