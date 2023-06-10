import requests
from urllib.parse import urlencode, quote_plus, quote, unquote
import os
import re
import time
import sys
import unicodedata
import json
import sqlite3
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import threading

try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser

ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
KEYTMDB = ADDON.getSetting("apikey")
HANDLE = int(sys.argv[1])
BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmarkUptobox.db')
NBMEDIA = 30


class MediaSp:
    def __init__(self, **kwargs):
        for attr_name, attr_value in kwargs.items():
            setattr(self, attr_name, attr_value)

def notice(content):
    log(content, xbmc.LOGINFO)

def log(msg, level=xbmc.LOGINFO):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level)

def createListItemFromVideo(video):
    notice("create listItem")
    url = video['url']
    title = video['title']
    list_item = xbmcgui.ListItem(title, path=url)
    if "episode" in video.keys():
        list_item.setInfo(type='Video', infoLabels={'Title': title, "episode": video['episode'], "season": video['season']})
    else:
        list_item.setInfo(type='Video', infoLabels={'Title': title})
    return list_item

def normalizeNum(num):
    s, e = num.split("E")
    e = "%s%s" %("0" * (4 - len(e)), e)
    return s + "E" + e

def showInfoNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message, xbmcgui.NOTIFICATION_INFO, 5000)

def showErrorNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message,
                                  xbmcgui.NOTIFICATION_ERROR, 5000)
def list2String(liste):
  return ' '.join(str(e) for e in liste)

def getBdAnotepad(repo):
    try:
        html_parser = HTMLParser()
        adrPbi = "https://anotepad.com/note/read/"
        motifAnotepad = r'.*<\s*div\s*class\s*=\s*"\s*plaintext\s*"\s*>(?P<txAnote>.+?)</div>.*'
        rec = requests.get(adrPbi + repo, timeout=5)
        r = re.match(motifAnotepad, rec.text, re.MULTILINE|re.DOTALL)
        tx = r.group("txAnote")
        tx = html_parser.unescape(tx)
    except Exception as e:
        notice(str(e))
        showInfoNotification("pb anotepad pour changer !!!")
        tx = ""
    return tx

def getBdPastebin(repo):
    try:
        adrPbi = "http://pastebin.com/raw/"
        rec = requests.get(adrPbi + repo, timeout=2)
        tx = rec.text
        #notice(tx)
    except:
        showInfoNotification("pb pastebin !!!")
        tx = ""
    return tx

def getBdRentry(repo):
    try:
        x = requests.get('https://rentry.org/{}/raw'.format(repo), timeout=5).content
        tx = x.decode()
    except:
        showInfoNotification("pb Rentry!!!")
        tx = ""
    return tx

def getBdTextup(repo):
    try:
        url = "https://textup.fr/{}".format(repo)
        rec = requests.get(url, timeout=5)

        #motif2 = r"\d+[-_ 0-9a-zA-Z]*\s?=\s?\d+\s?=\s?\w{32}"
        #cpatron = re.compile (motif2)
        #tabDb = cpatron.findall(rec.text, re.MULTILINE)
        #notice(tabDb)

        motif = r'.*<p>(?P<textup>.+)</p></div>.*'
        r = re.match(motif, rec.text, re.MULTILINE|re.DOTALL)
        tx = r.group("textup")
        lignes = tx.split("<br/>")
        lignes = "\n".join(lignes)
    except:
        showInfoNotification("pb textup!!!")
        lignes = ""
    return lignes


def extractKodiVersion():
    #notice(xbmc.getInfoLabel('System.BuildVersion'))
    versionFloat = re.findall(r'(\d{2}[.]\d{1,2})', xbmc.getInfoLabel('System.BuildVersion'))
    return float(versionFloat[0])

def updateMinimalInfoTagVideo(li, title, plot=None, episode=None, season=None):
    if extractKodiVersion() >= 20.0:
        vinfo = li.getVideoInfoTag()
        vinfo.setMediaType("video")

        try:
            vinfo.setTitle(title)
        except Exception as e:
            notice("Util.py - updateMinimalInfoTagVideo::title " + str(e))

        if plot!= None:
            try:
                vinfo.setPlot(plot)
            except Exception as e:
                notice("Util.py - updateMinimalInfoTagVideo::plot " + str(e))

        if episode!= None:
            try:
                vinfo.setEpisode(int(episode))
            except Exception as e:
                notice("Util.py - updateMinimalInfoTagVideo::episode " + str(e))

        if season!= None:
            try:
                vinfo.setSeason(int(season))
            except Exception as e:
                notice("Util.py - updateMinimalInfoTagVideo::season " + str(e))

        return vinfo
    else:
        if plot!= None:
            li.setInfo('video', {"title": title, 'plot': plot, 'mediatype': 'video'})
        else:
            li.setInfo('video', {"title": title, 'mediatype': 'video'})
        if season!= None:
            li.setInfo('video', {"episode": episode})
        if episode!= None:
            li.setInfo('video', {"season": season})


def updateEmptyInfoTag(li):
    if extractKodiVersion() >=20.0:
        vinfo = li.getVideoInfoTag()
        try:
            vinfo.setTitle("     ")
            vinfo.setPlot("")
            vinfo.setGenres([""])
            vinfo.setDbId(500000)
            vinfo.setYear(0)
            vinfo.setMediaType("movies")
            vinfo.setRating(0.0)
        except Exception as e:
            notice("Util.py - updateEmptyInfoTag " + str(e))
    else:
        li.setInfo('video', {"title": "     ", 'plot': "", 'genre': "", "dbid": 500000,"year": "", 'mediatype': "movies", "rating": 0.0})



def testThread(name):
    a = 0
    tActif = True
    while tActif:
        tActif = False
        for t in threading.enumerate():
            if name == t.getName():
                tActif = True
        time.sleep(0.1)
        a += 1
        if a > 150:
            break
    return True

def updateInfoTagVideo2(li, media):

    #correction
    try:
        media.year = int(str(media.year)[:4])
    except:
        media.year = 0
    try:
        if media.duration:
            media.duration = int(media.duration) * 60
        else:
            media.duration = 1
    except:
        media.duration = 1
    media.title = media.title.replace("00_", "")
    tabMedia = [x for x in dir(media) if x in ["title", "overview", "year", "genre", "popu", "duration", "numId", "episode", "saison", "vu", "typeMedia", "plot"]]
    #notice(tabMedia)

    if extractKodiVersion() >= 20.0:
        #kodi 20
        vinfo = li.getVideoInfoTag()
        dictSetInfos = {"title": (vinfo.setTitle, str), "overview": (vinfo.setPlot, str), "year": (vinfo.setYear, int),\
            "genre": (vinfo.setGenres, list), "popu": (vinfo.setRating, float), "duration": (vinfo.setDuration, int),\
            "numId": (vinfo.setUniqueIDs, dict), "episode": (vinfo.setEpisode, int), "saison": (vinfo.setSeason, int),\
            "vu": (vinfo.setPlaycount, int), "typeMedia": (vinfo.setMediaType, str), "plot": (vinfo.setPlot, str)}
        for a in tabMedia:
            info = getattr(media, a)
            if info:
                if a == "numId":
                    dictSetInfos[a][0]({"tmdb": str(info)}, "tmdb")
                    vinfo.setDbId(int(info) + 500000)
                elif a == "genre":
                    vinfo.setGenres(info.split(","))
                else:
                    try:
                        dictSetInfos[a][0](dictSetInfos[a][1](info))
                    except: pass

    else:
        #kodi 19
        if "numId" in tabMedia:
            li.setUniqueIDs({ 'tmdb' : media.numId }, "tmdb")
            li.setInfo('video', {"dbid": int(media.numId) + 500000})
        if "title" in tabMedia:
            li.setInfo('video', {"title": media.title})
        if "overview" in tabMedia:
            li.setInfo('video', {"plot": media.overview})
        if "plot" in tabMedia:
            li.setInfo('video', {"plot": media.plot})
        if "genre" in tabMedia:
            li.setInfo('video', {"genre": media.genre})
        if "duration" in tabMedia:
            li.setInfo('video', {"duration": media.duration * 60})
        if "year" in tabMedia:
            li.setInfo('video', {"year": media.year})
        if "popu" in tabMedia:
            li.setInfo('video', {"rating": media.popu})
        if "typeMedia" in tabMedia:
            li.setInfo('video', {"mediatype": media.typeMedia})
        if "vu" in tabMedia:
            li.setInfo('video', {'playcount': media.vu})
        if "episode" in tabMedia and media.episode:
            li.setInfo('video', {"episode": media.episode})
            try:
                li.setInfo('video', {"season": media.saison})
            except: pass


def updateInfoTagVideo(li, media, setUniqueId= False, isSerie=False, hasDuration=False, replaceTitle=False, hasPlaycount=False):

    if extractKodiVersion() >= 20.0:
        vinfo = li.getVideoInfoTag()

        try:
            if setUniqueId:
                vinfo.setUniqueIDs({ "tmdb" : str(media.numId) }, "tmdb")
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setUniqueIDs " + str(e))

        try:
            if replaceTitle:
                vinfo.setTitle(media.title.replace("00_", ""))
            else:
                vinfo.setTitle(media.title)
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setTitle " + str(e))

        try:
            vinfo.setPlot(media.overview)
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setPlot " + str(e))

        try:
            if type(media.genre) == list:
                vinfo.setGenres(media.genre)
            else:
                vinfo.setGenres([media.genre])
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setGenres " + str(e))

        try:
            if hasPlaycount:
                vinfo.setPlaycount(int(media.vu))
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setPlaycount " + str(e))

        try:
            vinfo.setDbId(int(media.numId) + 500000)
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setDbId " + str(e))

        try:
            if media.year != "":
                vinfo.setYear(int(media.year[: 4]))
        except Exception as e:
            vinfo.setYear(0)
            notice("Util.py - updateInfoTagVideo::setYear " + str(e))

        try:
            vinfo.setMediaType(media.typeMedia)
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setMediaType " + str(e))

        try:
            if media.popu != "":
                vinfo.setRating(float(media.popu))
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setRating " + str(e))

        try:
            if isSerie:
                vinfo.setEpisode(int(media.episode))
                vinfo.setSeason(int(media.saison))
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setEpisode/setSeason " + str(e))


        try:
            if hasDuration :
                if type(media.duration) == int:
                    vinfo.setDuration(media.duration * 60)
                else:
                    if media.duration != "":
                        vinfo.setDuration(int(media.duration) * 60)
        except Exception as e:
            notice("Util.py - updateInfoTagVideo::setDuration " + str(e))

        return vinfo
    else:

        if setUniqueId:
            li.setUniqueIDs({ 'tmdb' : media.numId }, "tmdb")

        if replaceTitle:
            li.setInfo('video', {"title": media.title.replace("00_", "")})
        else:
            li.setInfo('video', {"title": media.title})

        li.setInfo('video', {"plot": media.overview})

        if hasPlaycount:
            try:
                if media.vu:
                    li.setInfo('video', {'playcount': media.vu})
            except:
                pass

        li.setInfo('video', {"genre": media.genre})
        li.setInfo('video', {"dbid": int(media.numId) + 500000})
        li.setInfo('video', {"year": media.year})
        li.setInfo('video', {"mediatype": media.typeMedia})
        li.setInfo('video', {"rating": media.popu})

        if isSerie:
            li.setInfo('video', {"episode": media.episode})
            li.setInfo('video', {"season": media.saison})

        if hasDuration :
            li.setInfo('video', {"duration": media.duration * 60})
        return li

def makeNameRep(title):
    title = unquote(title)#, encoding='latin-1', errors='replace')
    title = unicodedata.normalize('NFD', title).encode('ascii','ignore').decode("latin-1")
    tab_remp = [r'''\\|/|:|\*|\?|"|<|>|\|| {2,}''', ' ']
    title = re.sub(tab_remp[0], tab_remp[1], title)
    title = title[:64].strip()
    return title

def saveFile(fileIn, textOut):
    if os.path.isfile(fileIn):
        try:
            with io.open(fileIn, "r", encoding="utf-8") as f:
                textIn = f.read()
        except:
            with io.open(fileIn, "r", encoding="latin-1") as f:
                textIn = f.read()
    else:
        textIn = ""
    if textIn != textOut:
        with open(fileIn, "w") as f:
            f.write(textOut)

def uExtractMedias(bd=None,limit=0, offset=1, sql="", unique=0):
    cnx = sqlite3.connect(bd)
    cur = cnx.cursor()
    requete = None
    try:
        def normalizeTitle(tx):
            #tx = re.sub(r''' {2,}''', ' ', re.sub(r''':|;|'|"|,''', ' ', tx))
            tx = re.sub(r''':|;|'|"|,|\-''', ' ', tx)
            tx = re.sub(r''' {2,}''', ' ', tx)
            tx = str(tx).lower()
            return unicodedata.normalize('NFD', tx).encode('ascii','ignore').decode("latin-1")
        cnx.create_function("normalizeTitle", 1, normalizeTitle)
        if sql:
            cur.execute(sql)
            if unique:
                requete = [x[0] for x in cur.fetchall()]
            else:
                requete = cur.fetchall()
        else:
            if limit > 0:
                cur.execute("SELECT title, overview, year, poster, link, numId FROM movie LIMIT %d OFFSET %d" %(limit, offset))
            else:
                cur.execute("SELECT title, overview, year, poster, link, numId FROM movie ORDER BY title COLLATE NOCASE ASC")
            requete = cur.fetchall()
    except Exception as e:
        notice("util.py - uExtractMedias :" +str(sql) + " - " + str(e))

    cur.close()
    cnx.close()
    return requete
