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

YOUTUBE_USER_FEED = 'http://gdata.youtube.com/feeds/api/users/default'
YOUTUBE_OTHER_USER_FEED = 'http://gdata.youtube.com/feeds/api/users/%s/uploads'
YOUTUBE_USER_VIDEOS = YOUTUBE_USER_FEED+'/uploads'
YOUTUBE_USER_FAVORITES = YOUTUBE_USER_FEED+'/favorites?v=2'
YOUTUBE_USER_SUBSCRIPTIONS = YOUTUBE_USER_FEED+'/subscriptions?v=2'
YOUTUBE_USER_CONTACTS = YOUTUBE_USER_FEED+'/contacts?v=2'

YOUTUBE_CHANNELS_FEEDS  = 'http://gdata.youtube.com/feeds/api/channelstandardfeeds/%s?v=2'

YOUTUBE_CHANNELS_MOSTVIEWED_URI = YOUTUBE_CHANNELS_FEEDS % ('mostviewed')
YOUTUBE_CHANNELS_MOSTSUBSCRIBED_URI = YOUTUBE_CHANNELS_FEEDS % ('most_subscribed')

YOUTUBE_QUERY = 'http://gdata.youtube.com/feeds/api/videos?q=%s'

DEVELOPER_KEY = 'AI39si7PodNU93CVDU6kxh3-m2R9hkwqoVrfijDMr0L85J94ZrJFlimNxzFA9cSky9jCSHz9epJdps8yqHu1wb743d_SfSCRWA'

YOUTUBE_VIDEO_PAGE = 'http://www.youtube.com/watch?v=%s'
YOUTUBE_VIDEO_FORMATS = ['Standard', 'Medium', 'High', '720p', '1080p']
YOUTUBE_FMT = [34, 18, 35, 22, 37]
USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

AuthHeader = None

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

def ParseFeed(sender=None, url=''):
  cookies = HTTP.GetCookiesForURL('http://www.youtube.com')

  dir = MediaContainer(viewGroup='InfoList', httpCookies=cookies)

  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  regionid = Prefs['youtube_region'].split('/')[1]
  if regionid == 'ALL':
    url = url.replace('/REGIONID','')
  else:
    url = url.replace('/REGIONID','/'+regionid)
 
 # Log(AuthHeader)

  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8')#,headers = AuthHeader)
  if rawfeed['feed'].has_key('entry'):
    for video in rawfeed['feed']['entry']:
      video_page = video['media$group']['media$player'][0]['url']
      video_id = re.search('v=([^&]+)', video_page).group(1)
      title = video['title']['$t']
      published = Datetime.ParseDate(video['published']['$t']).strftime('%a %b %d, %Y')
      summary = video['content']['$t']
      duration = int(video['media$group']['yt$duration']['seconds']) * 1000
      try:
        rating = float(video['gd$rating']['average']) * 2
      except:
        rating = None
      thumb = video['media$group']['media$thumbnail'][0]['url']
      dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=published, summary=summary, duration=duration, rating=rating, thumb=Function(Thumb, url=thumb)), video_id=video_id))

  if len(dir) == 0:
    return MessageContainer('Error', 'This query did not return any result')
  else:
    return dir

####################################################################################################

def MainMenu():
  dir = MediaContainer(noCache=True)
  
  regionName = Prefs['youtube_region'].split('/')[0]
  if regionName == 'All':
    localizedVideosName = L('Videos')
  else:
    localizedVideosName = L('Videos') +' for '+ regionName
    
  dir.Append(Function(DirectoryItem(VideosMenu, localizedVideosName, localizedVideosName)))
  dir.Append(Function(DirectoryItem(VideosMenu, L('Channels'), L('Channels'))))
  dir.Append(Function(DirectoryItem(VideosMenu, L('Movies'), L('Movies'))))
  dir.Append(Function(DirectoryItem(VideosMenu, L('Music'), L('Music'))))    
  dir.Append(Function(DirectoryItem(MyAccount, L('My account'), L('My account'))))  
  dir.Append(PrefsItem(L('Preferences'), thumb=R('icon-prefs.png')))
  return dir
  
def MyAccount(sender):
   #Authenticate()
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(ParseFeed, L('My Videos')), url=YOUTUBE_USER_VIDEOS))
  dir.Append(Function(DirectoryItem(ParseFeed, L('My Favorites')), url=YOUTUBE_USER_FAVORITES))
  dir.Append(Function(DirectoryItem(ParseFeed, L('My Subscriptions')), url=YOUTUBE_USER_SUBSCRIPTIONS))
  dir.Append(Function(DirectoryItem(MyContacts, L('My Contacts')), url=YOUTUBE_USER_CONTACTS))
  return dir 
   
def MyContacts(sender,url):
  dir = MediaContainer()
  for username in XML.ElementFromURL(url):   
    dir.Append(Function(DirectoryItem(ParseFeed, username), url=YOUTUBE_OTHER_USER_FEED%username))
  return dir 
   
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
    Log(data)
    for keys in data.split('\n'):
      if 'Auth=' in keys:
        AuthToken = keys.replace("Auth=",'')
        Log(AuthToken)
        HTTP.Headers['Authorization'] = "GoogleLogin auth="+AuthToken
        HTTP.Headers['X-GData-Key'] = "key="+DEVELOPER_KEY
        AuthHeader = dict([('Authorization', "GoogleLogin auth="+AuthToken) , ('X-GData-Key',"key="+DEVELOPER_KEY)])
        Log(AuthHeader)
        Log("Login Sucessful")
        dir = MessageContainer("Login sucessful", "You are now logged in")
  except:
    dir = MessageContainer("Login failed", "Please goback to the preference menu and re-enter your credentials")
  return dir
  
def VideosMenu(sender):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(SubMenu, L('Today')), category = 'today'))
  dir.Append(Function(DirectoryItem(SubMenu, L('This Week'), L('This Week')), category = 'this_week'))
  dir.Append(Function(DirectoryItem(SubMenu, L('This Month'), L('This Month')), category = 'this_month'))
  dir.Append(Function(DirectoryItem(SubMenu, L('All Time'), L('All Time')), category = 'all_time'))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Recent')), url=YOUTUBE_STANDARD_MOST_RECENT_URI))
  dir.Append(Function(InputDirectoryItem(Search, L('Search Videos'), L('Search Videos'), L('Search Videos'), thumb=R('icon-search.png'))))
  return dir
  
def ChannelsMenu(sender):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Viewed')), url=YOUTUBE_CHANNELS_MOSTVIEWED_URI))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Subscribed')), url=YOUTUBE_CHANNELS_MOSTSUBSCRIBED_URI))
  dir.Append(Function(InputDirectoryItem(Search, L('Search Channels'), L('Search Channels'), L('Search Channels'), thumb=R('icon-search.png'))))
  return dir

####################################################################################################

def SubMenu(sender, category):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Viewed')), url=YOUTUBE_STANDARD_MOST_VIEWED_URI+'?time=%s' % (category)))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Top Rated')), url=YOUTUBE_STANDARD_TOP_RATED_URI+'?time=%s' % (category)))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Discussed')), url=YOUTUBE_STANDARD_MOST_DISCUSSED_URI+'?time=%s' % (category)))
  return dir

####################################################################################################

def Search(sender, query=''):
  dir = MediaContainer()
  dir = ParseFeed(url=YOUTUBE_QUERY % (String.Quote(query, usePlus=False)))
  return dir

####################################################################################################

def PlayVideo(sender, video_id):
  yt_page = HTTP.Request(YOUTUBE_VIDEO_PAGE % (video_id), cacheTime=1).content

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
  return Redirect(url)
