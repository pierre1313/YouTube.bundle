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
YOUTUBE_QUERY = "http://gdata.youtube.com/feeds/api/videos?q=%s"

DEVELOPER_KEY = "AI39si7PodNU93CVDU6kxh3-m2R9hkwqoVrfijDMr0L85J94ZrJFlimNxzFA9cSky9jCSHz9epJdps8yqHu1wb743d_SfSCRWA"

PLUGIN_PREFIX       = "/video/youtube"
YT_FMT              = [34, 18, 35, 22, 37]

yt_videoURL         = "http://www.youtube.com/get_video?asv=3&video_id="

ART = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "YouTube", ICON, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")  
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items") 
  MediaContainer.title1 = 'YouTube'
  MediaContainer.content = 'Items'
  MediaContainer.art = R(ART)
  DirectoryItem.thumb = R(ICON)
  HTTP.CacheTime = 3600
  HTTP.Headers["User-agent"] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"  
  
####################################################################################################
def getThumb(path):
  return DataObject(HTTP.Request(path).content,'image/jpeg')
  
def parseFeed(sender = None,url=''):
  dir = MediaContainer(viewGroup="InfoList")  
  
  if url.find('?')>0:
    url = url + "&alt=json"
  else:
    url = url + "?alt=json"

  try:
    rawfeed = JSON.ObjectFromURL(url,encoding = 'utf-8')
    for video in rawfeed['feed']['entry']:
      id = video['media$group']['media$player'][0]['url']
      Log(id)
      title = video['title']['$t']
      summary = video['content']['$t']
      duration = str(int(video['media$group']['yt$duration']['seconds'])*1000)
      thumb = video['media$group']['media$thumbnail'][0]['url']
      dir.Append(Function(VideoItem(PlayVideo, title, subtitle='', summary=summary, duration=duration, thumb=Function(getThumb, path = thumb)), address = id))
  
    return dir
  except:
    return MessageContainer("Error","This query did not return any result") 
    
def MainMenu():
  dir = MediaContainer(viewGroup="List")  
  dir.Append(Function(DirectoryItem(SubMenu, L("Today")),category = 'today'))
  dir.Append(Function(DirectoryItem(SubMenu, L("This Week"), L("This Week")),category = 'this_week'))
  dir.Append(Function(DirectoryItem(SubMenu, L("This Month"), L("This Month")),category = 'this_month'))
  dir.Append(Function(DirectoryItem(SubMenu, L("All Time"), L("All Time")),category = 'all_time'))
  dir.Append(Function(DirectoryItem(parseFeed, L("Most Recent"), ""),url= YOUTUBE_STANDARD_MOST_RECENT_URI))
  dir.Append(Function(InputDirectoryItem(Search,L("Search YouTube"), L("Search YouTube"), L("Search YouTube"), thumb=R("search.png"))))
  return dir

def SubMenu(sender, category):
  dir = MediaContainer(viewGroup="InfoList")  
  dir.Append(Function(DirectoryItem(parseFeed, L("Most Viewed"), ""),url = (YOUTUBE_STANDARD_MOST_VIEWED_URI+"?time=%s" %category)))
  dir.Append(Function(DirectoryItem(parseFeed, L("Top Rated"), ""),url = (YOUTUBE_STANDARD_TOP_RATED_URI+"?time=%s" % category)))
  dir.Append(Function(DirectoryItem(parseFeed, L("Most Discussed"), ""),url = (YOUTUBE_STANDARD_MOST_DISCUSSED_URI+"?time=%s" % category)))
  return dir
      
def Search(sender, query = None):
  return parseFeed(url=YOUTUBE_QUERY % query.replace(' ','+'))
   
def PlayVideo(sender,address):
    ytPage = HTTP.Request(address).content
    
    Log(address)
    Log(ytPage)

    try:
      t = re.findall('&t=(.[^&"]{10,})', ytPage, re.IGNORECASE)[0]
    except:
      try:
        t = re.findall('"t": "([^"]+)"', ytPage)[0]
      except:
        t = ''

    v = address[address.find('v=')+2:address.find('&feature')] #
    Log(v)
    
    fmt_list = re.findall('&fmt_list=([^&]+)', ytPage)[0]
    fmts = re.findall('([0-9]+)[^,]*', fmt_list)

    index = 4
    if YT_FMT[index] in fmts:
      fmt = YT_FMT[index]
    else:
      for i in reversed( range(0, index+1) ):
        if str(YT_FMT[i]) in fmts:
          fmt = YT_FMT[i]
          break
        else:
          fmt = 5

    u = yt_videoURL + v + "&t=" + t + "&fmt=" + str(fmt)
    return Redirect(u)

####################################################################################################