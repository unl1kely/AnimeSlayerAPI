from bs4 import BeautifulSoup as bs
from JskPy import encodeUrl, best_match
from requests import get


##############
domainSlayer = "https://video.anime-slayer.com/"
animeServers = (
	"uqload.com",
	"dailymotion.com"
	"dood.",
	"uptostream.com",
	"uptostream.to",
	"vidbem.",
	"mp4upload.",
	"vidshar."
)
#
class Anime:
	def __init__(self, title):
		self.kind = list
		self.title = title
		self.search_url = "{0}/?search_param=animes&s={1}".format(domainSlayer, encodeUrl(self.title))
		self.search_response = get(self.search_url)
		if not "200" in str(self.search_response):
			self.message = "Unexpected network error."
			self.found = 0
		else:
			self.search_soup = bs(self.search_response.text, "html.parser")
			self.result_div = self.search_soup.find(class_="anime-list-content")
			self.result_list = self.result_div.find_all("h3")
			if len(self.result_list)==0:
				self.found = 0
				self.message = "{0} - Anime not found.".format(self.title)
			else:
				self.titles = [a_tag.string for a_tag in self.result_list]
				self.result_index = best_match(self.title, self.titles)
				if self.result_index!=None:
					self.found = 1
					self.name = self.titles[self.result_index]
					self.title_link = self.result_list[self.result_index].find("a").get("href")
					self.message = "Found anime : "+self.name
				else:
					self.found = 0
					self.message = "{0} - Anime not found.".format(self.title)
	def watch(self, season, episode, quality="Auto", launch=True):
		self.found = 0
		season = int(season)
		print(f"S {season}")
		Ss = ""
		if season>1: 
			self.result_index = best_match("{0} {1}".format(self.title, season), self.titles)
			if self.result_index!=None:
				self.name = self.titles[self.result_index]
				self.title_link = self.result_list[self.result_index].find("a").get("href")
				Ss = " Season {0} of".format(season)
				# found season
			else:
				self.found = 0
				self.message = "No season {0} found for {1}".format(season, self.name)
		ep = int(episode)
		title_html = get(self.title_link).text
		self.title_soup = bs(title_html, "html.parser")
		eps_list = self.title_soup.find_all("h3")[1:]
		print("0")
		print(eps_list)
		# passage
		if "1" in eps_list[0].find("a").string:
			eps_list.insert(0,"wassup")
			print("ifed")
			print(eps_list)
		if ep not in range(1,len(eps_list)):
			self.found = 0
			self.message = "No episode {0} found in{1} {2}".format(ep, Ss, self.name)
		else:
			# ep found
			ep_link = eps_list[ep].find("a").get("href")
			print("link")
			print(ep_link)
			ep_response = get(ep_link)
			ep_soup = bs(ep_response.text, "html.parser")
			watch_servers = ep_soup.find(id="episode-servers").find_all("a")
			watch_links = [a.get("data-ep-url") for a in watch_servers]
			for server in animeServers:
				for link in watch_links:
					if "drive.google.com" in link:
						drive_html = get(link)
						if str(drive_html.status_code)[-3]=='2':#goToAccountsUrl
							if '.mp4"' in drive_html:
								self.found = 1
								self.watch_link = link
								break
						del drive_html
					elif server in link:
						if str(get(link).status_code)[-3]=='2':
							self.found = 1
							self.watch_link = link
							break
				if self.found==1:
					break
			if self.found == 0:
				import random
				self.watch_link = random.choice(watch_links)
				self.found = 1
			if __name__ != '__main__':
				self.message = "{0} S{1}E{2} video link copied to clipboard".format(self.name, season, ep)
			else:
				self.message = self.watch_link
			if launch==True:
				try:
					import webbrowser
					webbrowser.open(self.watch_link)
				except Exception as e:
					print("{0}\nCould not go to watch link.".format(e))
			return self.message
