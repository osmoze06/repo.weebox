# -*- coding: utf-8 -*-
import requests
from urllib.parse import quote, urlparse, parse_qs, unquote, urlencode
from html.parser import HTMLParser
import sys
import time
import sqlite3
import os
import unicodedata
import shutil
import io
import argparse
import random
import datetime
import sqlite3
import threading
from xml.etree import ElementTree

from medias import Media, TMDB
try:
    import feniptv
    from util import *
    import xbmc
    import xbmcvfs
    import xbmcaddon
    import xbmcgui
    import xbmcplugin

    ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    HANDLE = int(sys.argv[1])
    BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/iptv.db')
    import pyxbmct
except: pass

class BookmarkIPTVXtream:
    def __init__(self, database):
        self.database = database
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        #('ffmpeg http://myf-tv.com:8080/zzww6q9eU5krRyM/09gX7NRc93Dup7N/363150', 'FR| PRIME VIDEO Multiplex FHD', '363150', 'http://covers.dragons-ott.com/JAQUETTE/prime-league1.png')

        cur.execute("""CREATE TABLE IF NOT EXISTS chainesX(
          `id`    INTEGER PRIMARY KEY,
          link TEXT,
          nom TEXT,
          num TEXT,
          poster TEXT,
          numId integer,
          fournisseur TEXT,
          UNIQUE (numId, num, fournisseur))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS fav(
          `id`    INTEGER PRIMARY KEY,
          pos INTEGER,
          link TEXT,
          nom TEXT,
          num TEXT,
          poster TEXT,
          numId integer,
          fournisseur TEXT,
          UNIQUE (numId, num, fournisseur))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS bankX(
          user TEXT,
          url TEXT,
          passwd TEXT,
          UNIQUE (url, user, passwd))
            """)


        cur.execute("""CREATE TABLE IF NOT EXISTS nomAdresseX(
          nom TEXT,
          url TEXT,
          UNIQUE (url))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS groupesX(
          `id`    INTEGER PRIMARY KEY,
          url TEXT,
          groupe TEXT,
          numId TEXT,
          valid INTEGER DEFAULT 1,
          UNIQUE (url, groupe))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS groupesvodX(
          `id`    INTEGER PRIMARY KEY,
          url TEXT,
          groupe TEXT,
          numId TEXT,
          typM TEXT,
          valid INTEGER DEFAULT 1,
          UNIQUE (url, groupe, typM))
            """)


        cur.execute("""CREATE TABLE IF NOT EXISTS lockX(
          url TEXT,
          numId TEXT,
          UNIQUE (url, numId))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS epgX(
          chaine TEXT,
          title TEXT,
          plot TEXT,
          startInt INTEGER,
          stopInt INTEGER,
          start TEXT,
          stop TEXT)
          """)


        cur.execute("""CREATE TABLE IF NOT EXISTS mapEpgX(
          url TEXT,
          numId TEXT,
          epg TEXT,
          UNIQUE (url, numId))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS correctEpgX(
          url TEXT,
          correct INTEGER,
          UNIQUE (url))
            """)

        cnx.commit()
        cur.close()
        cnx.close()

    def insertEpgX(self, tabEpg):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("DELETE FROM epgX")
        cnx.commit()
        notice(tabEpg[0])
        cur.executemany("REPLACE INTO epgX (chaine, title, plot, startInt, stopInt, start, stop) VALUES (?, ?, ?, ?, ?, ?, ?)", tabEpg)
        cnx.commit()
        cur.close()
        cnx.close()

    def extractEpgX(self):
        a = int(time.time())
        #a = time.strftime("%Y%m%d%H%M%S +0200", time.gmtime())
        #notice(a)
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT chaine, title, plot, startInt, stopInt, start, stop FROM epgX WHERE stopInt >= ?", (a,))
        liste = cur.fetchall()
        cur.close()
        cnx.close()
        return liste

    def retrait(self, fournisseur, mac=""):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        if mac:
            cur.execute("DELETE FROM adresse WHERE url=? AND mac=?", (fournisseur, mac, ))
            cur.execute("DELETE FROM tokens WHERE url=? AND mac=?", (fournisseur, mac, ))
        else:
            cur.execute("DELETE FROM adresse WHERE url=?", (fournisseur, ))
            cur.execute("DELETE FROM nomAdresse WHERE url=?", (fournisseur, ))
            cur.execute("DELETE FROM chaines WHERE fournisseur=?", (fournisseur, ))
            cur.execute("DELETE FROM tokens WHERE url=?", (fournisseur, ))
        cnx.commit()
        cur.close()
        cnx.close()

    def insertFav(self, *tab):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO fav (pos, link, nom, num, poster, numId, fournisseur) VALUES (?, ?, ?, ?, ?, ?, ?)", tab)
        cnx.commit()
        cur.close()
        cnx.close()

    def getFav(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        sql = "SELECT pos, link, nom, num, poster, numId, fournisseur FROM fav ORDER BY pos ASC"
        cur.execute(sql)
        liste = cur.fetchall()
        cur.close()
        cnx.close()
        return liste

    def delFav(self, num="", fournisseur=""):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        if num:
            cur.execute("DELETE FROM fav WHERE num=? and fournisseur=?", (num, fournisseur,))
        else:
            cur.execute("DELETE FROM fav")
        cnx.commit()
        cur.close()
        cnx.close()

    def insertChaines(self, tab):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.executemany("REPLACE INTO chaines (link, nom, num, poster, numId, fournisseur) VALUES (?, ?, ?, ?, ?, ?)", tab)
        cnx.commit()
        cur.close()
        cnx.close()

    def insertToken(self, *argv):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO tokens (url, mac, token) VALUES (?, ?, ?)", argv)
        cnx.commit()
        cur.close()
        cnx.close()

    def recupToken(self, url):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT url, mac, token FROM tokens WHERE url=? ORDER BY id DESC", (url,))
        liste = cur.fetchall()
        cnx.commit()
        cur.close()
        cnx.close()
        return liste

    def insertMapEpg(self, *argv):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO mapEpg (url, numId, epg) VALUES (?, ?, ?)", argv)
        cnx.commit()
        cur.close()
        cnx.close()

    def insertBank(self, kwargv):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        for url, macs in kwargv.items():
            for nom, mac in macs:
                cur.execute("REPLACE INTO bank (nom, url, mac) VALUES (?, ?, ?)", (nom, url, mac,))
        cnx.commit()
        cur.close()
        cnx.close()

    def getBank(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT nom, url, mac FROM bank")
        liste = cur.fetchall()
        cnx.commit()
        cur.close()
        cnx.close()
        return liste

    def delBank(self, *argv):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        if argv[0] == "del":
            cur.execute("DELETE FROM bank")
        else:
            cur.execute("DELETE FROM bank WHERE url=? AND mac=?", argv)
        cnx.commit()
        cur.close()
        cnx.close()


    def getMapEpg(self, url):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT numId, epg FROM mapEpg WHERE url=?", (url,))
        liste = cur.fetchall()
        cnx.commit()
        cur.close()
        cnx.close()
        return liste

    def getCorrectEpg(self, url):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT correct FROM correctEpg WHERE url=?", (url,))
        liste = [x[0] for x in cur.fetchall()]
        cnx.commit()
        cur.close()
        cnx.close()
        if liste:
            correct = liste[0]
        else:
            correct = 0
        return correct

    def insertCorrectEpg(self, *argv):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO correctEpg (url, correct) VALUES (?, ?)", argv)
        cnx.commit()
        cur.close()
        cnx.close()


    def deleteChaines(self, fournisseur=""):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        if fournisseur:
            cur.execute("DELETE FROM chaines WHERE fournisseur=?", (fournisseur, ))
        else:
            cur.execute("DELETE FROM chaines")
        cnx.commit()
        cur.close()
        cnx.close()

    def lockGroupe(self, url, numId, lock=1):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        if lock:
            cur.execute("REPLACE INTO lock (url, numId) VALUES (?, ?)", (url, numId, ))
        else:
            cur.execute("DELETE FROM lock WHERE url=? AND numId=?", (url, numId, ))
        cnx.commit()
        cur.close()
        cnx.close()

    def getLockGroupe(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT url, numId FROM lock")
        liste = ["%s*%s" %x for x in cur.fetchall()]
        cnx.commit()
        cur.close()
        cnx.close()
        return liste

    def getChaines(self, fournisseur,  num):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        sql = "SELECT link, nom, num, poster FROM chaines WHERE numId=? and fournisseur=?"
        cur.execute(sql, (num, fournisseur, ))
        liste = cur.fetchall()
        cur.close()
        cnx.close()
        return liste

    def getNom(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        sql = "SELECT url, nom FROM nomAdresse"
        cur.execute(sql)
        dictAdr = {x[0]: x[1] for x in cur.fetchall()}
        cur.close()
        cnx.close()
        return dictAdr

    def insertNom(self, *argv):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO nomAdresse (nom, url) VALUES (?, ?)", argv)
        cnx.commit()
        cur.close()
        cnx.close()

    def insertAdr(self, *argv):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO adresse (url, mac, user, passwd, ddate) VALUES (?, ?, ?, ?, ?)", argv)
        cnx.commit()
        cur.close()
        cnx.close()

    def insertGroupe(self, url, groupes):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        for groupe in groupes:
            cur.execute("REPLACE INTO groupes (url, groupe, numId) VALUES (?, ?, ?)", (url.strip(), groupe[0], groupe[1],))
        cnx.commit()
        cur.close()
        cnx.close()

    def updateGroupe(self, listeGroupes):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.executemany("UPDATE groupes SET valid=? WHERE groupe=?", listeGroupes)
        cnx.commit()
        cur.close()
        cnx.close()

    def updateGroupeVod(self, listeGroupes):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.executemany("UPDATE groupesvod SET valid=? WHERE groupe=? AND typM=?", listeGroupes)
        cnx.commit()
        cur.close()
        cnx.close()


    def getGroupe(self, fournisseur):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT groupe, numId, valid FROM groupes WHERE url LIKE ?", ("%" + fournisseur.strip() + "%",))
        liste = cur.fetchall()
        cnx.commit()
        cur.close()
        cnx.close()
        return liste

    def getGroupeVod(self, fournisseur, typM):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT groupe, numId, valid FROM groupesvod WHERE url=? AND typM=?", (fournisseur, typM,))
        liste = cur.fetchall()
        cnx.commit()
        cur.close()
        cnx.close()
        return liste

    def insertGroupeVod(self, url, groupes, typM):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        for groupe in groupes:
            cur.execute("REPLACE INTO groupesvod (url, groupe, numId, typM) VALUES (?, ?, ?, ?)", (url, groupe[0], groupe[1], typM, ))
        cnx.commit()
        cur.close()
        cnx.close()

    def getAdr(self, url=""):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        if url:
            sql = "SELECT mac FROM adresse WHERE url=?"
            cur.execute(sql, (url, ))
            liste = [x[0] for x in cur.fetchall()]
        else:
            sql = "SELECT url, mac, user, passwd, ddate FROM adresse"
            cur.execute(sql)
            liste = cur.fetchall()

        cur.close()
        cnx.close()
        return liste


class XCCache:
    authData = {}

class IPTVXtream:

    def __init__(self, num="1"):
        self.username = ADDON.getSetting("userx1")
        self.password = ADDON.getSetting("passx1")
        self.server = ADDON.getSetting("serverx1")
        self.liveType = "Live"
        self.vodType = "VOD"
        self.seriesType = "Series"
        self.link = self.server + "/{}/" + self.username + "/" + self.password + "/{}"

    def authenticate(self):
        r = requests.get(self.get_authenticate_URL())
        return r.json()

    # GET Stream Categories
    def categories(self, streamType):
        theURL = ""
        if streamType == self.liveType:
            theURL = self.get_live_categories_URL()
        elif streamType == self.vodType:
            theURL = self.get_vod_cat_URL()
        elif streamType == self.seriesType:
            theURL = self.get_series_cat_URL()
        else:
            theURL = ""

        r = requests.get(theURL)
        return r.json()

    # GET Streams by Category
    def streamsByCategory(self, streamType, category_id):
        theURL = ""
        if streamType == self.liveType:
            theURL = self.get_live_streams_URL_by_category(category_id)
        elif streamType == self.vodType:
            theURL = self.get_vod_streams_URL_by_category(category_id)
        elif streamType == self.seriesType:
            theURL = self.get_series_URL_by_category(category_id)
        else:
            theURL = ""
        r = requests.get(theURL)
        return r.json()

    #get epg
    def getEpg(self, stream_id="", limit=0):
        if stream_id and limit:
            url1 = self.get_live_epg_URL_by_stream_and_limit(stream_id, limit)
        elif stream_id:
            url1 = self.get_live_epg_URL_by_stream(stream_id)
        else:
            url1 = self.get_all_epg_URL()
        r = requests.get(url1)
        #with open(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/epg.xml'), "w", encoding="utf-8") as f:
        #    f.write(r.text)
        tree = ElementTree.fromstring(r.content)
        return tree

    def epgArchive(self, maj=1):
        dial = xbmcgui.DialogProgress()
        dial.create('U2P - Epg', 'Import EPG ...')
        tabEpg = []
        a = time.time()
        if maj:
            root = self.getEpg()
        else:
            tree = ElementTree.parse('epg.xml')
            root = tree.getroot()
        nbEpg = len([x for x in root.iter()])
        for i, epg in enumerate(root.iter()):
            percentage = int((i / float(nbEpg)) * 100.0)
            dial.update(percentage, 'Epg %d/%d' %(i, nbEpg))
            if "start" in epg.attrib:
                try:
                    startInt = epg.attrib["start"]
                    stopInt = epg.attrib["stop"]
                    chaine = epg.attrib["channel"]
                    start = time.strptime(epg.attrib["start"], "%Y%m%d%H%M%S %z")
                    stop = time.strptime(epg.attrib["stop"], "%Y%m%d%H%M%S %z")
                    #{'start': '20230530175000 +0200', 'stop': '20230530184000 +0200', 'channel': '13thStreet.de'}
                    #title, desc = epg.getchildren()
                    #notice(list(epg))
                    title, desc = list(epg)
                    tabEpg.append((chaine, title.text, desc.text, time.mktime(start), time.mktime(stop), startInt, stopInt))
                except: pass
        dial.close()
        return tabEpg


    def get_authenticate_URL(self):
        URL = '%s/player_api.php?username=%s&password=%s' % (self.server, self.username, self.password)
        #notice(URL)
        return URL

    def get_live_categories_URL(self, action="get_live_categories"):
        URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (self.server, self.username, self.password, action)
        return URL

    def get_live_streams_URL(self):
        URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (self.server, self.username, self.password, 'get_live_streams')
        return URL

    def get_live_streams_URL_by_category(self, category_id):
        URL = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (self.server, self.username, self.password, 'get_live_streams', category_id)
        return URL

    def get_live_epg_URL_by_stream(self, stream_id):
        URL = '%s/player_api.php?username=%s&password=%s&action=%s&stream_id=%s' % (self.server, self.username, self.password, 'get_short_epg', stream_id)
        return URL

    def get_live_epg_URL_by_stream_and_limit(self, stream_id, limit):
        URL = '%s/player_api.php?username=%s&password=%s&action=%s&stream_id=%s&limit=%s' % (self.server, self.username, self.password, 'get_short_epg', stream_id, limit)
        return URL

    def get_all_live_epg_URL_by_stream(self, stream_id):
        URL = '%s/player_api.php?username=%s&password=%s&action=%s&stream_id=%s' % (self.server, self.username, self.password, 'get_simple_data_table', stream_id)
        return URL

    def get_all_epg_URL(self):
        URL = '%s/xmltv.php?username=%s&password=%s' % (self.server, self.username, self.password)
        return URL


if __name__ == '__main__':

    cc = XCCache()
    iptv = IPTVXtream(1)
    iptv.authenticate()
    print(cc.authData)
    if cc.authData["user_info"]["status"] == "Active":
        print('server ok')
        print(cc.authData["user_info"]["exp_date"])

        #print(iptv.categories(iptv.liveType))
        #tabChaines = iptv.streamsByCategory(iptv.liveType, str(1))
        #print(tabChaines[1])
        #
        iptv.epgArchive()

        #film = iptv.link.format("live", "482")
        #print(film)
        #os.system('"C:/Program Files (x86)/VideoLAN/VLC/vlc.exe" %s.ts' %film)
        #os.system('"C:/Program Files (x86)/MPC-HC/mpc-hc.exe" %s' %film)
        #os.system('ffplay.exe -fs "%s.ts"' %film)

"""
server ok
1748347498
[{'category_id': '1', 'category_name': 'GENERALISTE', 'parent_id': 0}, {'category_id': '2', 'category_name': 'CINEMA', 'parent_id': 0}, {'category_id': '3', 'category_name': 'SERIES', 'parent_id': 0}, {'category_id': '4', 'category_name': 'DIVERTISSEMENT', 'parent_id': 0}, {'category_id': '5', 'category_name': 'DECOUVERTE', 'parent_id': 0}, {'category_id': '6', 'category_name': 'JEUNESSE', 'parent_id': 0}, {'category_id': '7', 'category_name': 'INFOS', 'parent_id': 0}, {'category_id': '8', 'category_name': 'REGIONALES', 'parent_id': 0}, {'category_id': '9', 'category_name': 'MUSIQUE', 'parent_id': 0}, {'category_id': '10', 'category_name': 'SPORT', 'parent_id': 0}, {'category_id': '11', 'category_name': 'BEIN SPORTS', 'parent_id': 0}, {'category_id': '12', 'category_name': 'PRIME VIDEO', 'parent_id': 0}, {'category_id': '13', 'category_name': 'RMC SPORT', 'parent_id': 0}, {'category_id': '14', 'category_name': 'MULTISPORTS', 'parent_id': 0}, {'category_id': '15', 'category_name': 'EUROSPORT 360', 'parent_id': 0}, {'category_id': '16', 'category_name': 'CANAL+ SPORT DIVERS', 'parent_id': 0}, {'category_id': '17', 'category_name': 'BELGE/SUISSE', 'parent_id': 0}, {'category_id': '81', 'category_name': 'RAKUTEN TV', 'parent_id': 0}, {'category_id': '82', 'category_name': 'PLUTO TV', 'parent_id': 0}, {'category_id': '23', 'category_name': 'ADULTE', 'parent_id': 0}]
{'num': 2, 'name': 'TF1', 'stream_type': 'live', 'stream_id': 482, 'stream_icon': 'https://never-dies.cc:443/images/DJagQBurpUQ4xR3aG2lwzvhXm58CUJMcpz05mRzzbfi7NSghNmeIr2ZWVq4chRTq.png', 'epg_channel_id': 'TF1.fr', 'added': '1683902974', 'custom_sid': '', 'tv_archive': 0, 'direct_source': '', 'tv_archive_duration': 0, 'category_id': '1', 'category_ids': [1], 'thumbnail': ''}
"""
"""
class XCCache:
    authData = {}

cc = XCCache()
# Note: The API Does not provide Full links to the requested stream. You have to build the url to the stream in order to play it.
#
# For Live Streams the main format is
#            http(s)://domain:port/live/username/password/streamID.ext ( In  allowed_output_formats element you have the available ext )
#
# For VOD Streams the format is:
#
# http(s)://domain:port/movie/username/password/streamID.ext ( In  target_container element you have the available ext )
#
# For Series Streams the format is
#
# http(s)://domain:port/series/username/password/streamID.ext ( In  target_container element you have the available ext )


# If you want to limit the displayed output data, you can use params[offset]=X & params[items_per_page]=X on your call.

# Authentication returns information about the account and server:
def authenticate():
    r = requests.get(get_authenticate_URL())
    cc.authData = r.json()
    return r

# GET Stream Categories
def categories(streamType):
    theURL = ""
    if streamType == liveType:
        theURL = get_live_categories_URL()
    elif streamType == vodType:
        theURL = get_vod_cat_URL()
    elif streamType == seriesType:
        theURL = get_series_cat_URL()
    else:
        theURL = ""

    r = requests.get(theURL)
    return r

# GET Streams
def streams(streamType):
    theURL = ""
    if streamType == liveType:
        theURL = get_live_streams_URL()
    elif streamType == vodType:
        theURL = get_vod_streams_URL()
    elif streamType == seriesType:
        theURL = get_series_URL()
    else:
        theURL = ""

    r = requests.get(theURL)
    return r

# GET Streams by Category
def streamsByCategory(streamType, category_id):
    theURL = ""
    if streamType == liveType:
        theURL = get_live_streams_URL_by_category(category_id)
    elif streamType == vodType:
        theURL = get_vod_streams_URL_by_category(category_id)
    elif streamType == seriesType:
        theURL = get_series_URL_by_category(category_id)
    else:
        theURL = ""

    r = requests.get(theURL)
    return r

# GET SERIES Info
def seriesInfoByID(series_id):
    r = requests.get(get_series_info_URL_by_ID(series_id))
    return r
# The seasons array, might be filled or might be completely empty.
# If it is not empty, it will contain the cover, overview and the air date of the selected season.
# In your APP if you want to display the series, you have to take that from the episodes array.

# GET VOD Info
def vodInfoByID(vod_id):
    r = requests.get(get_VOD_info_URL_by_ID(vod_id))
    return r

# GET short_epg for LIVE Streams (same as stalker portal, prints the next X EPG that will play soon)
def liveEpgByStream(stream_id):
    r = requests.get(get_live_epg_URL_by_stream(stream_id))
    return r

def liveEpgByStreamAndLimit(stream_id, limit):
    r = requests.get(get_live_epg_URL_by_stream_and_limit(stream_id, limit))
    return r

#  GET ALL EPG for LIVE Streams (same as stalker portal, but it will print all epg listings regardless of the day)
def allLiveEpgByStream(stream_id):
    r = requests.get(get_all_live_epg_URL_by_stream(stream_id))
    return r

# Full EPG List for all Streams
def allEpg():
    r = requests.get(get_all_epg_URL())
    return r


## URL-builder methods

def get_authenticate_URL():
    URL = '%s/player_api.php?username=%s&password=%s' % (server, username, password)
    return URL

def get_live_categories_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (server, username, password, 'get_live_categories')
    return URL

def get_live_streams_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (server, username, password, 'get_live_streams')
    return URL

def get_live_streams_URL_by_category(category_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (server, username, password, 'get_live_streams', category_id)
    return URL

def get_vod_cat_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (server, username, password, 'get_vod_categories')
    return URL

def get_vod_streams_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (server, username, password, 'get_vod_streams')
    return URL

def get_vod_streams_URL_by_category(category_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (server, username, password, 'get_vod_streams', category_id)
    return URL

def get_series_cat_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (server, username, password, 'get_series_categories')
    return URL

def get_series_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (server, username, password, 'get_series')
    return URL

def get_series_URL_by_category(category_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (server, username, password, 'get_series', category_id)
    return URL

def get_series_info_URL_by_ID(series_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&series_id=%s' % (server, username, password, 'get_series_info', series_id)
    return URL

def get_VOD_info_URL_by_ID(vod_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&vod_id=%s' % (server, username, password, 'get_vod_info', vod_id)
    return URL

def get_live_epg_URL_by_stream(stream_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&stream_id=%s' % (server, username, password, 'get_short_epg', stream_id)
    return URL

def get_live_epg_URL_by_stream_and_limit(stream_id, limit):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&stream_id=%s&limit=%s' % (server, username, password, 'get_short_epg', stream_id, limit)
    return URL

def get_all_live_epg_URL_by_stream(stream_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&stream_id=%s' % (server, username, password, 'get_simple_data_table', stream_id)
    return URL

def get_all_epg_URL():
    URL = '%s/xmltv.php?username=%s&password=%s' % (server, username, password)
    return URL

"""
