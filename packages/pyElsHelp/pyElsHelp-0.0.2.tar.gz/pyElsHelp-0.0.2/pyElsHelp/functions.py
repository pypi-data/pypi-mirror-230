import requests

class ElsUser():
	def __init__(self, login=None, password=None):
		self.login = login
		self.password = password

	def auth(self):
		if self.login != None and self.password != None:
			try:
				session = requests.Session()
				url = 'https://elschool.ru/Logon/Index'
				user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
				r = session.get(url, headers = {
				    'User-Agent': user_agent_val
				}, verify = False)
				session.headers.update({'Referer':url})
				session.headers.update({'User-Agent':user_agent_val})
				_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
				post_request = session.post(url, {
				     'login': f'{self.login}',
				     'password': f'{self.password}',
				     '_xsrf':_xsrf,
				})
				#print(post_request.text)
				user_id = post_request.text.split(r'<input type="hidden" id="model_menu_user_id" value="')[1].split(r'"')[0]
				if post_request.text.split('<title>')[1].split('</title>')[0] == 'Личный кабинет':
					return {'success': True, 'user_id': user_id}
				else:
					return {'success': False, 'error': 'Incorrect login or password'}
			except:
				return {'success': False, 'error': 'Incorrect login or password'}
		else:
			return {'success': False, 'error': 'No login or password entered'}

	def get_marks(self, subject=None, period=0):
		if self.login != None and self.password != None:
			if subject != None:
				if period in [0, 1, 2, 3, 4, 5, 6]: #0 — целый год, 1-4 — 1-4 ч./трим., 5 — 1 полугодие, 6 — 2 полугодие
					try:
						session = requests.Session()
						url = 'https://elschool.ru/Logon/Index'
						user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
						r = session.get(url, headers = {
						    'User-Agent': user_agent_val
						}, verify = False)
						session.headers.update({'Referer':url})
						session.headers.update({'User-Agent':user_agent_val})
						_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
						post_request = session.post(url, {
						     'login': f'{self.login}',
						     'password': f'{self.password}',
						     '_xsrf':_xsrf,
						})
						r1 = session.get('https://elschool.ru/users/diaries', headers = {
						    'User-Agent': user_agent_val
						}, verify = False)
						session.headers.update({'Referer':url})
						session.headers.update({'User-Agent':user_agent_val})
						_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
						s = r1.text.split('class="btn">Табель</a>')[0].split(r'href="')[-1].split(r'"')[0]
						#print(f'https://elschool.ru/users/diaries/{s}')
						r2 = session.get(f'https://elschool.ru/users/diaries/{s}', headers = {
						    'User-Agent': user_agent_val
						}, verify = False)
						session.headers.update({'Referer':url})
						session.headers.update({'User-Agent':user_agent_val})
						_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
						
						spg, fl, col4 = [], True, -1
						for i in range(1, 100):
							str_marks = ''
							s1 = list(r2.text.split(f'<tbody period="{i}"'))
							if len(s1) > 1:
								pr = s1[0].split(r'<th colspan="')[-1].split('>')[1].split('<')[0]
								if pr == subject:
									spo = []
									l1 = list(s1[1].split(r'<td class="grades-period-name">1')[1].split('<span>'))
									if s1[1].split(r'<td class="grades-period-name">1')[1][1:4] == 'чет':
										col4 = s1[1].split(r'<td class="grades-period-name">4')[1].split('<td class="grades-period-name">1')[0].count('<span>')
										col3 = s1[1].split(r'<td class="grades-period-name">3')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col4
										col2 = s1[1].split(r'<td class="grades-period-name">2')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col3 - col4
										col1 = s1[1].split(r'<td class="grades-period-name">1')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col2 - col3 - col4
							        	#print(f'{pr}: 1 четверть - {col1}, 2 четверть - {col2}, 3 четверть - {col3}, 4 четверть - {col4}')
									elif s1[1].split(r'<td class="grades-period-name">1')[1][1:4] == 'три':
										col3 = s1[1].split(r'<td class="grades-period-name">3')[1].split('<td class="grades-period-name">1')[0].count('<span>')
										col2 = s1[1].split(r'<td class="grades-period-name">2')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col3
										col1 = s1[1].split(r'<td class="grades-period-name">1')[1].split('<td class="grades-period-name">1')[0].count('<span>') - col2 - col3
									for r in l1[1:]:
										yu = r.split('</span>')[0]
										spo.append(yu)
										str_marks += f'{yu} '
									if col4 != -1:
										spg.append({'Предмет': f'{pr}', 'Оценки': f'{" ".join(spo)}', 'Colvo': f'{col1} {col2} {col3} {col4}', 'str': str_marks[0:len(str_marks)-1]})
									else:
										spg.append({'Предмет': f'{pr}', 'Оценки': f'{" ".join(spo)}', 'Colvo': f'{col1} {col2} {col3}', 'str': str_marks[0:len(str_marks)-1]})
									
									if period == 0:
										try:
											return {'success': True, 'Subject': subject, 'marks': str_marks[0:len(str_marks)-1].split()}
										except:
											return {'success': False, 'error': 'Marks not found'}
									elif period == 1:
										try:
											return {'success': True, 'Subject': subject, 'marks': str_marks[0:len(str_marks)-1].split()[0:col1]}
										except:
											return {'success': False, 'error': 'Marks not found'}
									elif period == 2:
										try:
											return {'success': True, 'Subject': subject, 'marks': str_marks[0:len(str_marks)-1].split()[col1:col2]}
										except:
											return {'success': False, 'error': 'Marks not found'}
									elif period == 3:
										try:
											return {'success': True, 'Subject': subject, 'marks': str_marks[0:len(str_marks)-1].split()[col1+col2:col3]}
										except:
											return {'success': False, 'error': 'Marks not found'}
									elif period == 4:
										try:
											return {'success': True, 'Subject': subject, 'marks': str_marks[0:len(str_marks)-1].split()[col1+col2+col3:]}
										except:
											return {'success': False, 'error': 'Marks not found'}
									elif period == 5:
										try:
											return {'success': True, 'Subject': subject, 'marks': str_marks[0:len(str_marks)-1].split()[0:col1+col2]}
										except:
											return {'success': False, 'error': 'Marks not found'}
									elif period == 6:
										try:
											return {'success': True, 'Subject': subject, 'marks': str_marks[0:len(str_marks)-1].split()[col1+col2:]}
										except:
											return {'success': False, 'error': 'Marks not found'}

						return {'success': False, 'error': 'Subject not found'}

					except:
						return {'success': False, 'error': 'Incorrect login or pasword'}
				else:
					return {'success': False, 'error': 'Wrong period value'}
			else:
				return {'success': False, 'error': 'No subject entered'}
		else:
			return {'success': False, 'error': 'No login or password entered'}

	def get_class(self):
		if self.login != None and self.password != None:
			try:
				session = requests.Session()
				url = 'https://elschool.ru/Logon/Index'
				user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
				r0 = session.get(url, headers = {
				    'User-Agent': user_agent_val
				}, verify = False)
				session.headers.update({'Referer':url})
				session.headers.update({'User-Agent':user_agent_val})
				_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
				post_request = session.post(url, {
				     'login': f'{self.login}',
				     'password': f'{self.password}',
				     '_xsrf':_xsrf,
				})
				r1 = session.get('https://elschool.ru/users/privateoffice', headers = {
				    'User-Agent': user_agent_val
				}, verify = False)
				session.headers.update({'Referer':url})
				session.headers.update({'User-Agent':user_agent_val})
				_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
				s = r1.text.split(r'<a class="d-block" href=')[1].split(r'>')[0]
				#print(s)
				#print(f'https://elschool.ru/users/diaries/{s}')
				r2 = session.get(f'https://elschool.ru{s}', headers = {
				    'User-Agent': user_agent_val
				}, verify = False)
				session.headers.update({'Referer':url})
				session.headers.update({'User-Agent':user_agent_val})
				_xsrf = session.cookies.get('_xsrf', domain=".elschool.ru")
				school = r2.text.split('<span class="link-to-institute">')[1].split('">')[1].split('</a>')[0]
				school = school.translate({ord(x): '' for x in '&quot;'})
				school = school.lstrip()
				school = school.rstrip()
				#print(school)
				#print(r2.text)
				sg = r2.text.split('<tr class="mdtable-row "')
				sp_res = []
				for i in range(1, len(sg)):
					sp = sg[i]
					s2 = sp.split('<a class="" href="/users/')[1]
					s3 = s2.split('title')[1]
					s4 = s3.split('">')[1]
					s5 = s4.split('</a>')[0]
					s5 = s5.lstrip()
					s5 = s5.rstrip()
					sp_res.append(s5)
				sg = r2.text.split('mdtable-row mdtable-row_last"')
				sp = sg[1]
				s2 = sp.split('<a class="" href="/users/')[1]
				s3 = s2.split('title')[1]
				s4 = s3.split('">')[1]
				s5 = s4.split('</a>')[0]
				s5 = s5.lstrip()
				s5 = s5.rstrip()
				sp_res.append(s5)

				return {'success': True, 'school': school, 'class': sp_res}

			except Exception as e:
				return {'success': False, 'error': f'{e}'}
		else:
			return {'success': False, 'error': 'No login or password entered'}


