# -*- coding: utf-8 -*-
import re

YOUTUBE_STANDARD_FEEDS = 'http://gdata.youtube.com/feeds/api/standardfeeds'
YOUTUBE_STANDARD_TOP_RATED_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'top_rated')
YOUTUBE_STANDARD_MOST_VIEWED_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_viewed')
YOUTUBE_STANDARD_RECENTLY_FEATURED_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'recently_featured')
YOUTUBE_STANDARD_WATCH_ON_MOBILE_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'watch_on_mobile')
YOUTUBE_STANDARD_TOP_FAVORITES_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'top_favorites')
YOUTUBE_STANDARD_MOST_RECENT_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_recent')
YOUTUBE_STANDARD_MOST_DISCUSSED_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_discussed')
YOUTUBE_STANDARD_MOST_LINKED_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_linked')
YOUTUBE_STANDARD_MOST_RESPONDED_URI = '%s/%s' % (YOUTUBE_STANDARD_FEEDS, 'most_responded')
YOUTUBE_QUERY = 'http://gdata.youtube.com/feeds/api/videos?q=%s'

DEVELOPER_KEY = 'AI39si7PodNU93CVDU6kxh3-m2R9hkwqoVrfijDMr0L85J94ZrJFlimNxzFA9cSky9jCSHz9epJdps8yqHu1wb743d_SfSCRWA'

YOUTUBE_VIDEO_PAGE = 'http://www.youtube.com/watch?v=%s'
YOUTUBE_GET_VIDEO_URL = 'http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%d&asv=3'
YOUTUBE_VIDEO_FORMATS = ['Standard', 'Medium', 'High', '720p', '1080p']
YOUTUBE_FMT = [34, 18, 35, 22, 37]
USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler('/video/youtube', MainMenu, 'YouTube', ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  MediaContainer.title1 = 'YouTube'
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R(ART)
  MediaContainer.userAgent = USER_AGENT

  DirectoryItem.thumb = R(ICON)
  VideoItem.thumb = R(ICON)

  HTTP.CacheTime = 3600
  HTTP.Headers['User-Agent'] = USER_AGENT

####################################################################################################

def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON))

####################################################################################################

def ParseFeed(sender=None, url=''):
  dir = MediaContainer(viewGroup='InfoList')

  if url.find('?') > 0:
    url = url + '&alt=json'
  else:
    url = url + '?alt=json'

  rawfeed = JSON.ObjectFromURL(url, encoding='utf-8')
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
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(SubMenu, L('Today')), category = 'today'))
  dir.Append(Function(DirectoryItem(SubMenu, L('This Week'), L('This Week')), category = 'this_week'))
  dir.Append(Function(DirectoryItem(SubMenu, L('This Month'), L('This Month')), category = 'this_month'))
  dir.Append(Function(DirectoryItem(SubMenu, L('All Time'), L('All Time')), category = 'all_time'))
  dir.Append(Function(DirectoryItem(ParseFeed, L('Most Recent')), url=YOUTUBE_STANDARD_MOST_RECENT_URI))
  dir.Append(Function(InputDirectoryItem(Search, L('Search YouTube'), L('Search YouTube'), L('Search YouTube'), thumb=R('icon-search.png'))))
  dir.Append(PrefsItem('Preferences', thumb=R('icon-prefs.png')))
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

    try:
      t = re.findall('&t=([^&"]+)', yt_page, re.IGNORECASE)[0]
    except:
      try:
        t = re.findall('"t": "([^"]+)"', yt_page)[0]
      except:
        t = ''

    fmt_list = re.findall('&fmt_list=([^&]+)', yt_page)[0]
    fmt_list = String.Unquote(fmt_list, usePlus=False)
    fmts = re.findall('([0-9]+)[^,]*', fmt_list)

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

    url = YOUTUBE_GET_VIDEO_URL % (video_id, t, fmt)
    return Redirect(url)
