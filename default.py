#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcvfs,xbmcaddon,os
from xbmcswift2 import Plugin

pluginhandle	= int(sys.argv[1])
plugin			= Plugin()
addon			= xbmcaddon.Addon(id='plugin.video.gameone-fork')
icon_path		= xbmc.translatePath(addon.getAddonInfo('path')+"/icon.png")
addon_path		= xbmc.translatePath(addon.getAddonInfo('path'))

user_agent		= 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
base_url		= 'http://www.gameone.de'
swfurl			= 'https://playermtvnn-a.akamaihd.net/g2/g2player_2.1.7.swf'


# MAIN MENU:
def create_main_menu():
	addDir(plugin.get_string(10001),base_url+'/tv',1,icon_path)
	addDir(plugin.get_string(10002),base_url+'/blog',4,icon_path)
	addDir(plugin.get_string(10003),base_url+'/playtube',8,icon_path)
	addDir(plugin.get_string(10004),'http://gameone.de/feed/podcast.xml',11,'http://gameone.de/images/podcast.jpg')


# TV CATEGORY:
def index_tv_years(url):			#1
	log('Indexing TV years: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match = re.compile('<h4 class=\'.+?>\n(.+?)\n</h4>', re.DOTALL).findall(content)
	for year in match:
		addDir(year,'http://www.gameone.de/tv/year/'+year,2,icon_path)

def index_tv_episodes(url):			#2
	log('Indexing TV episodes: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match = re.compile('<a href="/tv/(.+?)" class="image_link"><img alt=".+?" src="(.+?)" /></a>\n<h5>\n<a href=\'.+?\' title=\'(.+?)\'', re.DOTALL).findall(content)
	for episode,thumbnail,title in match:
		addLink('Folge '+episode+' - '+title,episode,3,thumbnail)

def play_tv_episode(episode):		#3
	log('Playing TV episode: ' + episode)
	
	req = urllib2.Request('http://www.gameone.de/api/mrss/mgid%3Agameone%3Avideo%3Amtvnn.com%3Atv_show-'+episode)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	match = re.compile("<media:content.+?url='(.+?)'></media:content>").findall(content)
	
	for video_xml in match:
		req = urllib2.Request(video_xml)
		req.add_header('User-Agent', user_agent)
		response = urllib2.urlopen(req)
		link_video=response.read()
		response.close()

		match_video = re.compile('<src>(.+?)</src>').findall(link_video)
		
		video_url = match_video[-1]+' swfurl='+swfurl+' swfvfy=true' + " pageUrl=www.gameone.de app=ondemand?ovpfv=2.1.4"

		item = xbmcgui.ListItem(name, thumbnailImage='', path=video_url)
		item.setProperty('mimetype', 'video/x-flv')
		xbmcplugin.setResolvedUrl(pluginhandle, True, item)


# BLOG CATEGORY
def index_blog_categories(url):		#4
	log('Indexing blog categories: ' + url)
	
	addDir(plugin.get_string(20001),url,5,icon_path)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match_teasers = re.compile('<ul class="teasers">(.+?)</ul>', re.DOTALL).findall(content)
	for teaser in match_teasers:
		match_categories = re.compile('<a title="(.+?)" href="(.+?)">.+?<img.+?src="(.+?)"', re.DOTALL).findall(teaser)
		for category,url,thumbnail in match_categories:
			addDir(category,base_url+url,5,base_url+thumbnail)

def index_blog_entries(url):		#5
	log('Indexing blog entries: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match_posts = re.compile('<li class="post teaser_box teaser".+?<div class=\'overlay\'.+?<a href="(.+?)">(.+?)</a>.+?<a class=\'image_link\' href=\'.+?\'>\n<img .+?src="(.+?)"', re.DOTALL).findall(content)
	match_next	= re.compile('<a class="next_page" rel="next" href="(.+?)">', re.DOTALL).findall(content)
	
	for url,title,thumbnail in match_posts:
		req = urllib2.Request(base_url+url)
		req.add_header('User-Agent', user_agent)
		response = urllib2.urlopen(req)
		content = response.read()
		response.close()
		
		match_videoposts = re.compile('<div class="player_swf".+?', re.DOTALL).findall(content)
		match_blogpages = re.compile('<a class="forwards" href="(.+?)">', re.DOTALL).findall(content)
		video_amount = len(match_videoposts)
		pages_amount = len(match_blogpages)
		
		if video_amount==1:
			if pages_amount==0:
				match_video_id = re.compile('video_meta-(.+?)"').findall(content)
				addLink(title,match_video_id[0],7,thumbnail)
			else:
				addDir(title,base_url+url,6,thumbnail)
		elif video_amount>1:
			addDir(title,base_url+url,6,thumbnail)
		 
	for url in match_next:
		addDir(plugin.get_string(00001),base_url+url,5,icon_path)

def index_blog_videos(url):			#6
	log('Indexing videos: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match_video = re.compile('video_meta-(.+?)"').findall(content)
	match_thumb = re.compile('"image", "(.+?)"', re.DOTALL).findall(content)
	match_title = re.compile('<p><strong>(.+?):</strong>', re.DOTALL).findall(content)
	match_next	= re.compile('<a class="forwards" href="(.+?)">').findall(content)
	
	i = 0
	for video_id in match_video:
		addLink(match_title[i],video_id,7,match_thumb[i])
		i = i + 1
	
	for url in match_next:
		addDir(plugin.get_string(00001),url,6,icon_path)
	
def play_blog_video(video_id):		#7
	log('Playing blog video: ' + video_id)
	
	video_url = get_video(video_id)
	
	item = xbmcgui.ListItem(name, thumbnailImage='', path=video_url)
	item.setProperty('mimetype', 'video/x-flv')
	xbmcplugin.setResolvedUrl(pluginhandle, True, item)


# PLAYTUBE CATEGORY
def index_playtube_categories(url):	#8
	log('Indexing Playtube categories: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match = re.compile("<ul class='channels'>(.+?)</ul>", re.DOTALL).findall(content)
	match = re.compile("<a class='name' href='(.+?)' title='(.+?)'>", re.DOTALL).findall(match[0])
	
	for url,title in match:
		if not title == 'GameTrailers':
			addDir(title,url,9,icon_path)

def index_playtube_videos(url):		#9
	log('Indexing Playtube videos: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match = re.compile('<h3><a href="(.+?)">(.+?)</a></h3>\n<p><a href=".+?">.+?</a></p>\n</div>\n<a href=".+?" class="img_link"><img alt=".+?" src="(.+?)" /></a>', re.DOTALL).findall(content)
	match_next = re.compile('<a class="next_page" rel="next" href="(.+?)"').findall(content)
	
	for url,title,thumbnail in match:
		addLink(title,url,10,thumbnail)
		
	for url in match_next:
		addDir(plugin.get_string(00001),base_url+url,9,icon_path)

def play_playtube_video(url):		#10
	log('Playing Playtube video: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match_video = re.compile('video_meta-(.+?)"').findall(content)
	video_url = get_video(match_video[0])
	play_video(video_url)


# PODCAST CATEGORY	
def index_podcasts(url):			#11
	log('Indexing podcasts: ' + url)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match = re.compile('</image>.+?</rss>', re.DOTALL).findall(content)
	match_podcasts = re.compile('<title>(.+?)</title>.+?<feedburner:origLink>(.+?)</feedburner:origLink>', re.DOTALL).findall(match[0])
	
	for title,url in match_podcasts:		
		addLink(title,url,12,'http://gameone.de/images/podcast.jpg')


def play_video(url):				#12
	log('Playing media: ' + url)
	
	item = xbmcgui.ListItem(path=url)
	return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def get_video(video_id):
	log('Scraping video ID: ' + url)
	
	req = urllib2.Request("http://riptide.mtvnn.com/mediagen/"+video_id)
	req.add_header('User-Agent', user_agent)
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	
	match = re.compile('<src>(.+?)</src>').findall(content)
	video = match[-1]+' swfurl='+swfurl+' swfvfy=true' + " pageUrl=www.gameone.de app=ondemand?ovpfv=2.1.4"
	return video
                
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def string_escape(string):
	string = string.replace('&amp;','&')
	string = string.replace('&quot;','"')
	string = string.replace('&#x27;',"'")
	
	return string

def addLink(name,url,mode,iconimage=icon_path,fanart=''):
	name = string_escape(name)
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	liz.setProperty('IsPlayable', 'true')
	liz.setProperty('fanart_image',fanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
	return ok

def addDir(name,url,mode,iconimage=icon_path,fanart=''):
	name = string_escape(name)
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	liz.setProperty('fanart_image',fanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok
	
def log(msg):
	print('GameOne.de scraper - %s' % msg)


params=get_params()
url=None
name=None
mode=None
thumb=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        thumb=urllib.unquote_plus(params["thumb"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass



if mode==None or url==None or len(url)<1:
        create_main_menu()
       
elif mode==1:
        index_tv_years(url)

elif mode==2:
        index_tv_episodes(url)
        
elif mode==3:
        play_tv_episode(url)

elif mode==4:
        index_blog_categories(url)

elif mode==5:
        index_blog_entries(url)

elif mode==6:
	index_blog_videos(url)

elif mode==7:
	play_blog_video(url)

elif mode==8:
	index_playtube_categories(url)

elif mode==9:
	index_playtube_videos(url)
	
elif mode==10:
	play_playtube_video(url)

elif mode==11:
	index_podcasts(url)

elif mode==12:
	play_video(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
