from PMS import Plugin, Log, XML, HTTP, JSON, Prefs
from PMS.MediaXML import *
from PMS.FileTypes import PLS
from PMS.Shorthand import _L, _R, _E, _D
import gdata.youtube, gdata.youtube.service
import re

PLUGIN_PREFIX       = "/video/youtube"

yt_service          = None
yt_videoURL         = "http://www.youtube.com/get_video?video_id="

####################################################################################################

def Start():
  Plugin.AddRequestHandler(PLUGIN_PREFIX, HandleRequest, "YouTube", "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", contentType="items")  
  Plugin.AddViewGroup("List", viewMode="List", contentType="items") 
  
  global yt_service
  yt_service = gdata.youtube.service.YouTubeService()
  yt_service.developer_key = "AI39si7PodNU93CVDU6kxh3-m2R9hkwqoVrfijDMr0L85J94ZrJFlimNxzFA9cSky9jCSHz9epJdps8yqHu1wb743d_SfSCRWA"
  yt_service.client_id = "ytapi-Plex-YouTubePlugin-ei1mp311-0"
  
####################################################################################################
def parseFeed(feed,dir):
  for video in feed.entry:
    id = PLUGIN_PREFIX + "/play^" + _E(video.media.player.url)
    title = video.media.title.text
    summary = video.media.description.text
    duration = str(int(video.media.duration.seconds)*1000)
    thumb = video.media.thumbnail[0].url
    dir.AppendItem(VideoItem(id, title, summary, duration, thumb))
  return dir

def HandleRequest(pathNouns, count):
  global yt_service
  #Log.Add(pathNouns[-1])
  try:
    title2 = pathNouns[count-1].split("||")[1]
    pathNouns[count-1] = pathNouns[count-1].split("||")[0]
  except:
    title2 = ""
  
  if count == 0: vg="List"
  else: vg="InfoList"
    
  dir = MediaContainer("art-default.png", viewGroup=vg, title1="YouTube", title2=title2)  
  if count == 0:
    dir.AppendItem(DirectoryItem("today||" + _L("Today"), _L("Today")))
    dir.AppendItem(DirectoryItem("this_week||" + _L("This Week"), _L("This Week")))
    dir.AppendItem(DirectoryItem("this_month||" + _L("This Month"), _L("This Month")))
    dir.AppendItem(DirectoryItem("all_time||" + _L("All Time"), _L("All Time")))
    dir.AppendItem(DirectoryItem("feed^YOUTUBE_STANDARD_MOST_RECENT_URI||" + _L("Most Recent"), _L("Most Recent"), ""))
    dir.AppendItem(SearchDirectoryItem("search||" + _L("Search YouTube"), _L("Search YouTube"), _L("Search YouTube"), _R("search.png")))
    
  elif count == 1 and pathNouns[0] in ['today', 'this_week', 'this_month', 'all_time']:
    dir.AppendItem(DirectoryItem(("feed^YOUTUBE_STANDARD_MOST_VIEWED_URI^%s||" % pathNouns[0]) + _L("Most Viewed"), _L("Most Viewed"), ""))
    dir.AppendItem(DirectoryItem(("feed^YOUTUBE_STANDARD_TOP_RATED_URI^%s||" % pathNouns[0]) + _L("Top Rated"), _L("Top Rated"), ""))
    dir.AppendItem(DirectoryItem(("feed^YOUTUBE_STANDARD_MOST_DISCUSSED_URI^%s||" % pathNouns[0]) + _L("Most Discussed"), _L("Most Discussed"), ""))
    
  elif pathNouns[0].startswith("feed") and count < 2:
    dir = parseFeed(yt_service.GetYouTubeVideoFeed(pathNouns[0].split("^")[1]), dir)
    
  elif count > 1 and pathNouns[1].startswith("feed"):
    params = pathNouns[1].split("^")
    dir = parseFeed(yt_service.GetYouTubeVideoFeed(params[1], params[2]), dir)
    
  elif pathNouns[0].startswith("search") and count < 3:
    if count > 1:
      query = pathNouns[1]
    if count > 2:
      for i in range(2, len(pathNouns)): query += "/%s" % pathNouns[i]
    yt_query = gdata.youtube.service.YouTubeVideoQuery()
    yt_query.vq = query # the term(s) that you are searching for
    yt_query.orderby = 'relevance'    # how to display the results
    yt_query.max_results = '40'        # number of results to retrieve
    dir = parseFeed(yt_service.YouTubeQuery(yt_query),dir)
    if dir.ChildCount() == 0:
      dir.AppendItem(DirectoryItem("%s/search" % PLUGIN_PREFIX, "(No Results)", ""))
   
  elif pathNouns[-1].startswith("play"):
    ytPage = HTTP.Get(_D(pathNouns[-1].split("^")[1]))

    Log.Add(_D(pathNouns[-1].split("^")[1]))
    #Log.Add(ytPage)

    try:
      t = re.findall('&t=(.[^&"]{10,})', ytPage, re.IGNORECASE)[0]
    except:
      try:
        t = re.findall('"t": "([^"]+)"', ytPage)[0]
      except:
        t = ''
    Log.Add(t)

    v = re.findall("'VIDEO_ID': '([^']+)'", ytPage)[0] #
    hd = re.findall("'IS_HD_AVAILABLE': ([^,]+),", ytPage)[0] #
    fmt = "18"
    if hd == "true":
      fmt = "22"

    u = yt_videoURL + v + "&t=" + t + "&asv=2&fmt=" + fmt
    return Plugin.Redirect(u)

  return dir.ToXML()
####################################################################################################