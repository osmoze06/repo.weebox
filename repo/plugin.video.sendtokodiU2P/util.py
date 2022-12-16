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


def notice(content):
    log(content, xbmc.LOGINFO)

def log(msg, level=xbmc.LOGINFO):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level)

def createListItemFromVideo(video):
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


def getBdAnotepad(repo):
    try:
        html_parser = HTMLParser()
        adrPbi = "https://anotepad.com/note/read/"
        motifAnotepad = r'.*<\s*div\s*class\s*=\s*"\s*plaintext\s*"\s*>(?P<txAnote>.+?)</div>.*'
        rec = requests.get(adrPbi + repo, timeout=5)
        r = re.match(motifAnotepad, rec.text, re.MULTILINE|re.DOTALL)
        tx = r.group("txAnote")
        tx = html_parser.unescape(tx)
    except:
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
