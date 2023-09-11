import requests

# APARAT VIDEO API
video = 'https://www.aparat.com/etc/api/video/videohash/{}'

class Video:
	def __init__(self, uid, res=0, filename=0):
		self.uid = uid
		self.res = res
		self.filename = filename
		
	def download(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			file_links = data['file_link_all']
			
			if self.filename == 0:
				self.filename = data['title'] + '.mp4'
				
			else:
				pass
			
			if self.res == '144p':
				for link in file_links:
					if link['profile'] == '144p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == '240p':
				for link in file_links:
					if link['profile'] == '240p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == '360p':
				for link in file_links:
					if link['profile'] == '360p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == '480p':
				for link in file_links:
					if link['profile'] == '480p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == '720p':
				for link in file_links:
					if link['profile'] == '720p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == '1080p':
				for link in file_links:
					if link['profile'] == '1080p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == '1440p':
				for link in file_links:
					if link['profile'] == '1440p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == '2160p':
				for link in file_links:
					if link['profile'] == '2160p':
						url = link['urls'][0]
						
						response = requests.get(url)
						
						with open(self.filename, 'wb') as f:
							f.write(response.content)
						
						break
						
			elif self.res == 0:
				file_link = data['file_link']
				
				url = file_link
				
				response = requests.get(url)
				
				with open(self.filename, 'wb') as f:
					f.write(response.content)
		
		else:
			print(f'error {response.status_code}')
			
	def get_title(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			title = data['title']
			
			return title
		
		else:
			print(f'error {response.status_code}')
			
	def get_description(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			description = data['description']
			
			return description
			
		else:
			print(f'error {response.status_code}')
			
	def get_username(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			username = data['username']
			
			return username
			
		else:
			print(f'error {response.status_code}')
			
	def get_sender_name(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			sender_name = data['sender_name']
			
			return sender_name
			
		else:
			print(f'error {response.status_code}')
			
	def get_visit_cnt(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			visit_cnt = data['visit_cnt']
			
			return visit_cnt
			
		else:
			print(f'error {response.status_code}')
			
	def get_big_poster(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			if self.filename == 0:
				self.filename = data['title'] + '.jpg'
				
			else:
				pass
			
			url = data['big_poster']
			
			response = requests.get(url)
			
			with open(self.filename, 'wb') as f:
				f.write(response.content)
			
		else:
			print(f'error {response.status_code}')
			
	def get_small_poster(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			if self.filename == 0:
				self.filename = data['title'] + '.jpg'
				
			else:
				pass
			
			url = data['small_poster']
			
			response = requests.get(url)
			
			with open(self.filename, 'wb') as f:
				f.write(response.content)
			
		else:
			print(f'error {response.status_code}')
			
	def get_duration(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			duration = data['duration']
			
			return duration
			
		else:
			print(f'error {response.status_code}')
			
	def get_sdate(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			sdate = data['sdate']
			
			return sdate
			
		else:
			print(f'error {response.status_code}')
			
	def get_create_date(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			create_date = data['create_date']
			
			return create_date
			
		else:
			print(f'error {response.status_code}')
			
	def official(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			official = data['official']
			
			if official == 'yes':
				return True
				
			else:
				return False
			
		else:
			print(f'error {response.status_code}')
			
	def get_like_cnt(self):
		url = video.format(self.uid)
		
		response = requests.get(url)
		
		if response.status_code == 200:
			data = response.json()['video']
			
			like_cnt = data['like_cnt']
			
			return like_cnt
			
		else:
			print(f'error {response.status_code}')