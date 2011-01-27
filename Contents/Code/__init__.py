# -*- coding: utf-8 -*-
import re, urllib, urllib2, cookielib

YOUTUBE_STANDARD_FEEDS = 'http://gdata.youtube.com/feeds/api/standardfeeds'

YOUTUBE_STANDARD_TOP_RATED_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'top_rated')
YOUTUBE_STANDARD_MOST_VIEWED_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_viewed')
YOUTUBE_STANDARD_RECENTLY_FEATURED_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'recently_featured')
YOUTUBE_STANDARD_WATCH_ON_MOBILE_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'watch_on_mobile')
YOUTUBE_STANDARD_TOP_FAVORITES_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'top_favorites')
YOUTUBE_STANDARD_MOST_RECENT_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_recent')
YOUTUBE_STANDARD_MOST_DISCUSSED_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_discussed')
YOUTUBE_STANDARD_MOST_LINKED_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_linked')
YOUTUBE_STANDARD_MOST_RESPONDED_URI = '%s/REGIONID/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_responded')

YOUTUBE_USER_FEED = 'http://gdata.youtube.com/feeds/api/users/%s'
YOUTUBE_OTHER_USER_FEED = 'http://gdata.youtube.com/feeds/api/users/%s/uploads'
YOUTUBE_USER_PROFILE = 'http://gdata.youtube.com/feeds/api/users/%s?alt=json'
YOUTUBE_USER_VIDEOS = YOUTUBE_USER_FEED+'/uploads'
YOUTUBE_USER_FAVORITES = YOUTUBE_USER_FEED+'/favorites?v=2'
YOUTUBE_USER_PLAYLISTS = YOUTUBE_USER_FEED+'/playlists?v=2'
YOUTUBE_USER_SUBSCRIPTIONS = YOUTUBE_USER_FEED+'/subscriptions?v=2'
YOUTUBE_USER_CONTACTS = YOUTUBE_USER_FEED+'/contacts?v=2'

YOUTUBE_CHANNELS_FEEDS  = 'http://gdata.youtube.com/feeds/api/channelstandardfeeds/%s?v=2'

YOUTUBE_CHANNELS_MOSTVIEWED_URI = YOUTUBE_CHANNELS_FEEDS % ('most_viewed')
YOUTUBE_CHANNELS_MOSTSUBSCRIBED_URI = YOUTUBE_CHANNELS_FEEDS % ('most_subscribed')

YOUTUBE_QUERY = 'http://gdata.youtube.com/feeds/api/%s?q=%s&v=2'

YOUTUBE = 'http://www.youtube.com'
YOUTUBE_MOVIES = YOUTUBE + '/movies?hl=en'
YOUTUBE_SHOWS = YOUTUBE + '/shows?hl=en'
YOUTUBE_TRAILERS = YOUTUBE + '/trailers?hl=en'

DEVELOPER_KEY = 'AI39si7PodNU93CVDU6kxh3-m2R9hkwqoVrfijDMr0L85J94ZrJFlimNxzFA9cSky9jCSHz9epJdps8yqHu1wb743d_SfSCRWA'

YOUTUBE_VIDEO_DETAILS = 'http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc'

YOUTUBE_VIDEO_PAGE = 'http://www.youtube.com/watch?v=%s'

YOUTUBE_VIDEO_FORMATS = ['Standard', 'Medium', 'High', '720p', '1080p']
YOUTUBE_FMT = [34, 18, 35, 22, 37]
USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

YT_NAMESPACE = 'http://gdata.youtube.com/schemas/2007'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

AuthHeader = {}

####################################################################################################

def Start():
  Plugin.AddPrefixHandler('/video/youtube', MainMenu, 'YouTube', ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  MediaContainer.title1 = 'YouTube'
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R(ART)
  MediaContainer.userAgent = ''

  DirectoryItem.thumb = R(ICON)
  VideoItem.thumb = R(ICON)

  HTTP.CacheTime = 3600
  HTTP.Headers['User-Agent'] = USER_AGENT

  Authenticate()


####################################################################################################

def ValidatePrefs():
  Authenticate()

def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON))

####################################################################################################

def MainMenu():
  dir = MediaContainer(noCache=True)
  
  regionName = Prefs['youtube_region'].split('/')[0]
  if regionName == 'All':
    localizedVideosName = L('Videos')
  else:
    localizedVideosName = L('Videos for ')+ regionName
    
  dir.Append(Function(DirectoryItem(VideosMenu, localizedVideosName, localizedVideosName)))
  dir.Append(Function(DirectoryItem(ChannelsMenu, L('Channels'), L('Channels'))))
  dir.Append(Function(DirectoryItem(MoviesMenu, L('Movies'), L('Movies'))))
  dir.Append(Function(DirectoryItem(ShowsMenu, L('Shows'), L('Shows'))))    
#  dir.Append(Function(DirectoryItem(VideosMenu, L('* Music'), L('Music'))))
  dir.Append(Function(DirectoryItem(TrailersMenu, L('Trailers'), L('Trailers'))))    
  if Dict['loggedIn'] == True:
    dir.Append(Function(DirectoryItem(MyAccount, L('My Account'), L('My Account'))))  
  dir.Append(PrefsItem(L('Preferences'), thumb=R('icon-prefs.png')))
  return dir
  
####################################################################################################
## VIDEOS
####################################################################################################
  
def VideosMenu(sender):
  dir = MediaContainer(title2 = L("Videos"))
  dir.Append(Function(DirectoryItem(SubMenu, L('Today')), category = 'today'))
  dir.Append(Function(DirectoryItem(SubMenu, L('This Week'), L('This Week')), category = 'this_week'))
  dir.Append(Function(DirectoryItem(SubMenu, L('This Month'), L('This Month')), category = 'this_month'))
  dir.Append(Function(DirectoryItem(SubMenu, L('All Time'), L('All Time')), category = 'all_time'))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Recent')), url=YOUTUBE_STANDARD_MOST_RECENT_URI))
  dir.Append(Function(InputDirectoryItem(Search, L('Search Videos'), L('Search Videos'), L('Search Videos'), thumb=R('icon-search.png')),SearchType = 'videos'))
  return dir

####################################################################################################
## CHANNELS
####################################################################################################
  
def ChannelsMenu(sender):
  dir = MediaContainer(title2 = L("Channels"))
  dir.Append(Function(DirectoryItem(ParseChannelFeed, L('Most Viewed')), url=YOUTUBE_CHANNELS_MOSTVIEWED_URI))
  dir.Append(Function(DirectoryItem(ParseChannelFeed, L('Most Subscribed')), url=YOUTUBE_CHANNELS_MOSTSUBSCRIBED_URI))
  dir.Append(Function(InputDirectoryItem(Search, L('Search Channels'), L('Search Channels'), L('Search Channels'), thumb=R('icon-search.png')),SearchType = 'channels'))
  return dir
  
####################################################################################################
## MOVIES
####################################################################################################

def MoviesMenu(sender):
  dir = MediaContainer(title2 = L("Movies")) 
  for category in HTML.ElementFromURL(YOUTUBE_MOVIES).xpath("//div[@id='shmoovies-category-menu-container']/ul/li/a"):
    dir.Append(Function(DirectoryItem(MoviesCategoryMenu, category.text.strip()), url=YOUTUBE + category.get('href')))
  return dir

def MoviesCategoryMenu(sender,url,page=1):
  dir = MediaContainer(viewGroup='InfoList',title2 = sender.title2, httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))
 
  if page > 1:
    dir.Append(Function(DirectoryItem(MoviesCategoryMenu, L("Previous Page ...")), url=url, page = page - 1))
  
  pageContent = HTTP.Request(url+'?p='+str(page)).content
  for movie in HTML.ElementFromString(pageContent).xpath("//div[contains(@class,'movie-cell')]"):
    title = movie.xpath('.//div[@class="movie-title"]/div[@class="movie-short-title"]/a')[0].text.strip()
    id = movie.xpath('.//div[@class="movie-title"]/div[@class="movie-short-title"]/a')[0].get('href').split('v=')[1]
    thumb = movie.xpath('.//span[@class="clip"]/img')[0].get('src')
    info = (HTML.StringFromElement(movie.xpath('.//p[@class="info"]')[0]).replace('mpaa">',"|Rated ").replace('</span>','|').replace('\n','').replace('</p>','')).split('|')

    if len(info) == 2:
      duration = GetDurationFromString(info[0].split('info">')[1].strip())
      subtitle = info[1].strip()
    else:
      duration = GetDurationFromString(info[2].strip())
      subtitle = info[1].strip() + ' - ' + info[3].strip()
    summary = movie.xpath('.//p[@class="description"]')[0].text.strip()
    dir.Append(Function(VideoItem(PlayVideo, title, thumb = Function(Thumb, url=thumb), subtitle = subtitle, summary = summary, duration = duration), video_id=id))
  
  if '>Next<' in pageContent:
    dir.Append(Function(DirectoryItem(MoviesCategoryMenu, L("Next Page ...")), url=url, page = page + 1))
 
  return dir

####################################################################################################
## SHOWS
####################################################################################################

def ShowsMenu(sender):
  dir = MediaContainer(title2 = L("Shows")) 
  for category in HTML.ElementFromURL(YOUTUBE_SHOWS).xpath("//div[@id='shmoovies-category-menu-container']/ul/li/a"):
    dir.Append(Function(DirectoryItem(ShowsCategoryMenu, category.text.strip()), url=YOUTUBE + category.get('href')))
  return dir

def ShowsCategoryMenu(sender,url,page=1):
  dir = MediaContainer(viewGroup='List',title2 = sender.title2)
 
  if page > 1:
    dir.Append(Function(DirectoryItem(ShowsCategoryMenu, L("Previous Page ...")), url=url, page = page - 1))
  
  pageContent = HTTP.Request(url+'?p='+str(page)).content
  for show in HTML.ElementFromString(pageContent).xpath("//div[contains(@class,'show-cell')]"):
    title = show.xpath('.//h3')[0].text.strip()
    link = YOUTUBE + show.xpath('.//a')[0].get('href')
    thumb = show.xpath('.//span[@class="clip"]/img')[0].get('src')
    dir.Append(Function(DirectoryItem(ShowsVideos, title, thumb = Function(Thumb, url=thumb)), url=link,thumb = thumb))
  
  if '>Next<' in pageContent:
    dir.Append(Function(DirectoryItem(ShowsCategoryMenu, L("Next Page ...")), url=url, page = page + 1))
 
  return dir
  
def ShowsVideos(sender,url,thumb):
  dir = MediaContainer(viewGroup='InfoList',title2 = sender.title2, httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  for episode in HTML.ElementFromURL(url).xpath("//tbody/tr"):
    title = episode.xpath('./td[3]//h3')[0].text.strip()
    id = episode.xpath('./td[3]//a')[0].get('href').split('v=')[1]
    duration = GetDurationFromString(episode.xpath('./td[3]//p[@class="info"]')[0].text.strip())
    summary = episode.xpath('./td[3]//p[@class="description"]')[0].text.strip()
    try: 
      subtitle =  L('Air date : ') + episode.xpath('./td[5]')[0].text.strip()
    except:
      subtitle = ''
    dir.Append(Function(VideoItem(PlayVideo, title, thumb = thumb, subtitle = subtitle, summary = summary, duration = duration), video_id=id))

  return dir
  
####################################################################################################
## TRAILERS
####################################################################################################

def TrailersMenu(sender):
  dir = MediaContainer(title2 = L("Trailers")) 
  for category in HTML.ElementFromURL(YOUTUBE_TRAILERS).xpath("//div[@class='trailer-list']/preceding-sibling::h3/a"):
    dir.Append(Function(DirectoryItem(TrailersVideos, category.text.strip()), url=YOUTUBE + category.get('href')))
  return dir
  
def GetSummary(videoid):
  try:
    details = JSON.ObjectFromURL(YOUTUBE_VIDEO_DETAILS%videoid)
    return str(details['entry']['media$group']['media$description']['$t'])
  except:
    return ''
    
def TrailersVideos(sender,url,page=1):
  dir = MediaContainer(viewGroup='List',title2 = sender.title2, httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))
 
  if page > 1:
    dir.Append(Function(DirectoryItem(TrailersVideos, L("Previous Page ...")), url=url, page = page - 1))
  
  pageContent = HTTP.Request(url+'&p='+str(page)).content
  for trailer in HTML.ElementFromString(pageContent).xpath("//div[contains(@class,'trailer-cell')]"):
    id = trailer.xpath('.//div[@class="trailer-title"]/div[@class="trailer-short-title"]/a')[0].get('href').split('v=')[1]
   
    title = trailer.xpath('.//div[@class="trailer-title"]/div[@class="trailer-short-title"]/a')[0].text.strip()
    thumb = trailer.xpath('.//span[@class="clip"]/img')[0].get('src')
    
    try:
      summary = trailer.xpath('.//p[@class="description"]')[0].text.strip()
    except:
      summary = ''
    try:
      subtitle = trailer.xpath('.//span[contains(@class,"video-release-date")]')[0].text.strip()
    except:
      subtitle = ''
    
    #duration = str(details['entry']['media$group']['yt$duration'])*1000
    duration = 0 # possible future addition
    dir.Append(Function(VideoItem(PlayVideo, title, thumb = thumb, subtitle = subtitle, summary = summary, duration = duration), video_id=id))
  
  if '>Next<' in pageContent:
    dir.Append(Function(DirectoryItem(TrailersVideos, L("Next Page ...")), url=url, page = page + 1))
 
  return dir
  

####################################################################################################
## MY ACCOUNT
####################################################################################################
  
def MyAccount(sender):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(ParseFeed, L('My Videos')), url=YOUTUBE_USER_VIDEOS % 'default'))
  dir.Append(Function(DirectoryItem(ParseFeed, L('My Favorites')), url=YOUTUBE_USER_FAVORITES % Prefs['youtube_user']))
  dir.Append(Function(DirectoryItem(ParsePlaylist, L('My Playlists')), url=YOUTUBE_USER_PLAYLISTS % Prefs['youtube_user']))
  dir.Append(Function(DirectoryItem(ParseSubscriptions, L('My Subscriptions')), url=YOUTUBE_USER_SUBSCRIPTIONS % 'default'))
  dir.Append(Function(DirectoryItem(MyContacts, L('My Contacts')), url=YOUTUBE_USER_CONTACTS % 'default'))
  return dir 
   
def MyContacts(sender,url):
  dir = MediaContainer()
  xmlcontent = HTTP.Request(url).content.strip()
  Page = HTML.ElementFromString(xmlcontent.replace('yt:','yt-'))
  if Page.xpath('//entry') == None:
    dir = MessageContainer(L("Error"), L("You have no contacts"))
  else:
    for contact in Page.xpath('//entry'): 
      if contact.xpath('yt-status')[0].text == 'accepted':
        username = contact.xpath('yt-username')[0].text
        dir.Append(Function(DirectoryItem(ParseFeed, username), url=YOUTUBE_OTHER_USER_FEED%username))
  return dir 
  
####################################################################################################
## AUTHENTICATION
####################################################################################################
 
def Authenticate():
  global AuthHeader
  try:
    handler = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(handler)
    u=Prefs['youtube_user']
    p=Prefs['youtube_passwd']
    params = urllib.urlencode({"Email": u, "Passwd": p,"service":"youtube","source":DEVELOPER_KEY})
    f = handler.open("https://www.google.com/accounts/ClientLogin", params)
    data = f.read()
    f.close()
    for keys in data.split('\n'):
      if 'Auth=' in keys:
        AuthToken = keys.replace("Auth=",'')
        HTTP.Headers['Authorization'] = "GoogleLogin auth="+AuthToken
        HTTP.Headers['X-GData-Key'] = "key="+DEVELOPER_KEY
        AuthHeader = dict([('Authorization', "GoogleLogin auth="+AuthToken) , ('X-GData-Key',"key="+DEVELOPER_KEY)])
        Log(AuthHeader)
        Dict['loggedIn']=True
        Log("Login Sucessful")
  except:
    Dict['loggedIn']=False
    Log("Login Failed")  
  return True
  
####################################################################################################

def SubMenu(sender, category):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Viewed')), url=YOUTUBE_STANDARD_MOST_VIEWED_URI+'?time=%s' % (category)))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Top Rated')), url=YOUTUBE_STANDARD_TOP_RATED_URI+'?time=%s' % (category)))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Discussed')), url=YOUTUBE_STANDARD_MOST_DISCUSSED_URI+'?time=%s' % (category)))
  return dir

####################################################################################################

def Search(sender, SearchType = 'videos', query=''):
  dir = MediaContainer()
  if SearchType == 'videos':
    dir = ParseFeed(url=YOUTUBE_QUERY % (SearchType,String.Quote(query, usePlus=False)))
  else:
    dir = ParseChannelSearch(url=YOUTUBE_QUERY % (SearchType,String.Quote(query, usePlus=False)))
  return dir
  
####################################################################################################
  
def GetDurationFromString(duration):

  try:
    durationArray = duration.split(":")

    if len(durationArray) == 3:
      hours = int(durationArray[0])
      minutes = int(durationArray[1])
      seconds = int(durationArray[2])
    elif len(durationArray) == 2:
      hours = 0
      minutes = int(durationArray[0])
      seconds = int(durationArray[1])
    elif len(durationArray)  ==  1:
      hours = 0
      minutes = 0
      seconds = int(durationArray[0])
      
    return int(((hours)*3600 + (minutes*60) + seconds)*1000)
    
  except:
    return 0  

####################################################################################################

def ParseFeed(sender=None, url=''):
  dir = MediaContainer(viewGroup='InfoList', httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  regionid = Prefs['youtube_region'].split('/')[1]
  if regionid == 'ALL':
    url = url.replace('/REGIONID','')
  else:
    url = url.replace('/REGIONID','/'+regionid)
 
  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8',headers = AuthHeader)
  if rawfeed['feed'].has_key('entry'):
    for video in rawfeed['feed']['entry']:
      if video.has_key('yt$videoid'):
        video_id = video['yt$videoid']['$t']
      else:
        if video['media$group'].has_key('media$player'):
          try:
            video_page = video['media$group']['media$player'][0]['url']
          except:
            video_page = video['media$group']['media$player']['url']
          video_id = re.search('v=([^&]+)', video_page).group(1)
        else:
		  video_id = None      
        title = video['title']['$t']
      
      if (video_id != None) and not(video.has_key('app$control')):
        try:
          published = Datetime.ParseDate(video['published']['$t']).strftime('%a %b %d, %Y')
        except: 
          published = Datetime.ParseDate(video['updated']['$t']).strftime('%a %b %d, %Y')
       
        try: 
          summary = video['content']['$t']
        except:
          summary = video['media$group']['media$description']['$t']
     
        duration = int(video['media$group']['yt$duration']['seconds']) * 1000
      
        try:
          rating = float(video['gd$rating']['average']) * 2
        except:
          rating = None
      
        thumb = video['media$group']['media$thumbnail'][0]['url']
      
        dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=published, summary=summary, duration=duration, rating=rating, thumb=Function(Thumb, url=thumb)), video_id=video_id))

  if len(dir) == 0:
    return MessageContainer(L('Error'), L('This query did not return any result'))
  else:
    return dir
    
def ParseSubscriptionFeed(sender=None, url=''):
  dir = MediaContainer(viewGroup='InfoList', httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  regionid = Prefs['youtube_region'].split('/')[1]
  if regionid == 'ALL':
    url = url.replace('/REGIONID','')
  else:
    url = url.replace('/REGIONID','/'+regionid)
 
  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8',headers = AuthHeader)
  for video in rawfeed['feed']['entry']:
    if ('events?' in url) and ('video' in video['category'][1]['term']):
		for details in video['link'][1]['entry']:
		  if details.has_key('yt$videoid'):
			video_id = details['yt$videoid']['$t']
		  else:
		    if details['media$group'].has_key('media$player'):
			  try:
			    video_page = details['media$group']['media$player'][0]['url']
  			  except:
			    video_page = details['media$group']['media$player']['url']
  			  video_id = re.search('v=([^&]+)', video_page).group(1)
		    else:
		      video_id = None
		    title = details['title']['$t']

		      
		  if (video_id != None) and not(video.has_key('app$control')):
  		    try:
			  published = Datetime.ParseDate(details['published']['$t']).strftime('%a %b %d, %Y')
		    except: 
		      published = Datetime.ParseDate(details['updated']['$t']).strftime('%a %b %d, %Y')
		   
		    try: 
		  	  summary = details['content']['$t']
		    except:
			  summary = details['media$group']['media$description']['$t']
		 
		    duration = int(details['media$group']['yt$duration']['seconds']) * 1000
		  
		    try:
			  rating = float(details['gd$rating']['average']) * 2
		    except:
			  rating = None
		  
		    thumb = details['media$group']['media$thumbnail'][0]['url']
		  
		    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=published, summary=summary, duration=duration, rating=rating, thumb=Function(Thumb, url=thumb)), video_id=video_id))

  if len(dir) == 0:
    return MessageContainer(L('Error'), L('This query did not return any result'))
  else:
    return dir    
    
def ParseChannelFeed(sender=None, url=''):
  dir = MediaContainer(viewGroup='InfoList', httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))
  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  regionid = Prefs['youtube_region'].split('/')[1]
  if regionid == 'ALL':
    url = url.replace('/REGIONID','')
  else:
    url = url.replace('/REGIONID','/'+regionid)

  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8',headers = AuthHeader)
  if rawfeed['feed'].has_key('entry'):
    for video in rawfeed['feed']['entry']:
      feedpage = video['author'][0]['uri']['$t']+'?v=2&alt=json'
      videos = JSON.ObjectFromURL(feedpage, encoding='utf-8',headers = AuthHeader)['entry']['gd$feedLink']
      for vid in videos:
        if 'upload' in vid['rel']:
          link = vid['href']
      title = video['title']['$t']
      summary = video['summary']['$t']
      thumb = video['media$group']['media$thumbnail'][0]['url']
      dir.Append(Function(DirectoryItem(ParseFeed, title=title, summary=summary, thumb=Function(Thumb, url=thumb)), url=link))

  if len(dir) == 0:
    return MessageContainer(L('Error'), L('This query did not return any result'))
  else:
    return dir
    
def ParseChannelSearch(sender=None, url=''):
  dir = MediaContainer(viewGroup='InfoList', httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8',headers = AuthHeader)
  if rawfeed['feed'].has_key('entry'):
    for video in rawfeed['feed']['entry']:
      link = video['gd$feedLink'][0]['href']
      title = video['title']['$t']
      summary = video['summary']['$t']
      thumb = JSON.ObjectFromURL(YOUTUBE_USER_PROFILE % video['author'][0]['name']['$t'], encoding='utf-8',headers = AuthHeader)['entry']['media$thumbnail']['url']
      dir.Append(Function(DirectoryItem(ParseFeed, title=title, summary=summary, thumb=Function(Thumb, url=thumb)), url=link))

  if len(dir) == 0:
    return MessageContainer(L('Error'), L('This query did not return any result'))
  else:
    return dir
    
def ParsePlaylist(sender=None, url=''):
  dir = MediaContainer(viewGroup='InfoList', httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8',headers = AuthHeader)
  if rawfeed['feed'].has_key('entry'):
    for video in rawfeed['feed']['entry']:
      link = video['content']['src']
      title = video['title']['$t']
      summary = video['summary']['$t']
      thumb = R(ICON)
      dir.Append(Function(DirectoryItem(ParseFeed, title=title, summary=summary, thumb=Function(Thumb, url=thumb)), url=link))

  if len(dir) == 0:
    return MessageContainer(L('Error'), L('This query did not return any result'))
  else:
    return dir
    
def ParseSubscriptions(sender=None, url=''):
  dir = MediaContainer(viewGroup='InfoList', httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))
  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8',headers = AuthHeader)
  if rawfeed['feed'].has_key('entry'):
    for subscription in rawfeed['feed']['entry']:
      link = subscription['content']['src']
      title = subscription['title']['$t']
      dir.Append(Function(DirectoryItem(ParseSubscriptionFeed, title=title), url=link))

  if len(dir) == 0:
    return MessageContainer(L('Error'), L('You have no subscriptions'))
  else:
    return dir

####################################################################################################

def PlayVideo(sender, video_id):
  yt_page = HTTP.Request(YOUTUBE_VIDEO_PAGE % (video_id), cacheTime=1, headers = AuthHeader).content

  fmt_url_map = re.findall('"fmt_url_map".+?"([^"]+)', yt_page)[0]
  fmt_url_map = fmt_url_map.replace('\/', '/').split(',')

  fmts = []
  fmts_info = {}

  for f in fmt_url_map:
    (fmt, url) = f.split('|')
    fmts.append(fmt)
    fmts_info[str(fmt)] = url

  index = YOUTUBE_VIDEO_FORMATS.index(Prefs['youtube_fmt'])
  if YOUTUBE_FMT[index] in fmts:
    fmt = YOUTUBE_FMT[index]
  else:
    for i in reversed( range(0, index+1) ):
      if str(YOUTUBE_FMT[i]) in fmts:
        fmt = YOUTUBE_FMT[i]
        break
      else:
        fmt = 5

  url = fmts_info[str(fmt)]
  Log("  VIDEO URL --> " + url)
  return Redirect(url)