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
import feniptv
from medias import Media, TMDB
try:
    from util import *
    import xbmc
    import xbmcvfs
    import xbmcaddon
    import xbmcgui
    import xbmcplugin

    ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    HANDLE = int(sys.argv[1])
    BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/iptv.db')
except: pass

import pyxbmct


class MyDialog(pyxbmct.AddonDialogWindow):
    def __init__(self):
        #self.setGeometry(1000, 560, 50, 30)
        self._monitor = xbmc.Monitor()
        self._player = xbmc.Player()
        #self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        
    def play(self, path):
        self._player.play(path)
        xbmc.sleep(200)  # Wait for the player to start, adjust the timeout if necessary
        self.close()
        while self._player.isPlaying():
            if self._monitor.waitForAbort(1):
                raise SystemExit
        self.doModal()

class BookmarkIPTV:

    def __init__(self, database):
        self.database = database
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        #('ffmpeg http://myf-tv.com:8080/zzww6q9eU5krRyM/09gX7NRc93Dup7N/363150', 'FR| PRIME VIDEO Multiplex FHD', '363150', 'http://covers.dragons-ott.com/JAQUETTE/prime-league1.png')
        
        cur.execute("""CREATE TABLE IF NOT EXISTS chaines(
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
        
        cur.execute("""CREATE TABLE IF NOT EXISTS adresse(
          url TEXT,
          mac TEXT,
          user TEXT,
          passwd TEXT,
          ddate TEXT,
          UNIQUE (url, mac))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS bank(
          nom TEXT,
          url TEXT,
          mac TEXT,
          UNIQUE (url, mac))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS tokens(
          `id`    INTEGER PRIMARY KEY,
          url TEXT,
          mac TEXT,
          token TEXT,
          UNIQUE (url, mac))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS nomAdresse(
          nom TEXT,
          url TEXT,
          UNIQUE (url))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS groupes(
          `id`    INTEGER PRIMARY KEY,
          url TEXT,
          groupe TEXT,
          numId TEXT,
          valid INTEGER DEFAULT 1,
          UNIQUE (url, groupe))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS groupesvod(
          `id`    INTEGER PRIMARY KEY,
          url TEXT,
          groupe TEXT,
          numId TEXT,
          typM TEXT,
          valid INTEGER DEFAULT 1,
          UNIQUE (url, groupe, typM))
            """)


        cur.execute("""CREATE TABLE IF NOT EXISTS lock(
          url TEXT,
          numId TEXT,
          UNIQUE (url, numId))
            """)

        cur.execute("""CREATE TABLE IF NOT EXISTS mapEpg(
          url TEXT,
          numId TEXT,
          epg TEXT,
          UNIQUE (url, numId))
            """)
        
        cur.execute("""CREATE TABLE IF NOT EXISTS correctEpg(
          url TEXT,
          correct INTEGER,
          UNIQUE (url))
            """)
        
        cnx.commit()
        cur.close()
        cnx.close()

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


class IPTVMac:

    def __init__(self, urlBase, adrMac, token=""):
        notice(urlBase)
        self.adrMac = quote(adrMac)
        self.urlBase = urlBase
        self.urlBase = self.urlBase.replace("/c/", "")
        if self.urlBase[-1] == "/":
            self.urlBase = self.urlBase[:-1]
        #self.session = requests.Session()
        self.headers = {
        "X-User-Agent": "Model: MAG254; Link: Ethernet,WiFi",
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3",
        "Referer": self.urlBase,
        "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Host": self.urlBase.split("://")[1],
        "Cookie": "mac=" + self.adrMac + "; stb_lang=en; timezone=Europe/Paris; adid=dbe9f56771de8f9abaa3bade08465d6c",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        }
        self.token = token
        self.vod = "vod"
        self.tv = "itv"
        self.stb = "stb"
        if self.token:
            self.headers["Authorization"] = "Bearer %s" %self.token
        self.proxyDict = {}
        self.tokenUrl = "/portal.php?type=stb&action=handshake"
        self.xpcom = "/c/xpcom.common.js&JsHttpRequest=1-xml"
        self.profileUrl = "/portal.php?type=stb&action=get_profile&JsHttpRequest=1-xml"
        self.infosCompteUrl = "/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
        self.genreUrl = "/portal.php?type=itv&action=get_genres&JsHttpRequest=1-xml"
        self.genreUrlVod =  "/server/load.php?action=create_link&type=vod&cmd={}&JsHttpRequest=1-xml"
        self.listGenreUrl = "/portal.php?type={}&action=get_ordered_list&genre={}&force_ch_link_check=&fav=0&sortby=number&hd=0&p={}&from_ch_id=0&JsHttpRequest=1-xml"
        #self.listGenreUrl = "/portal.php?type={}&action=get_ordered_list&category={}&force_ch_link_check=&fav=0&sortby=number&hd=0&p={}&from_ch_id=0&JsHttpRequest=1-xml"
        self.catUrl = "/portal.php?type={}&action=get_categories&JsHttpRequest=1-xml"  #vod ou series
        self.createLink = "/portal.php?type=itv&action=create_link&cmd={}&series=0&forced_storage=false&disable_ad=false&download=false&force_ch_link_check=false&JsHttpRequest=1-xml"
        self.createLinkVod = "/server/load.php?action=create_link&type={}&cmd={}&JsHttpRequest=1-xml" 
        self.createLinkSerie = "/portal.php?type=vod&action=create_link&cmd={}&series={}&forced_storage=false&disable_ad=false&download=false&force_ch_link_check=false&JsHttpRequest=1-xml"
        #type=tv_archive&action=create_link&cmd=auto%20%2Fmedia%2F16031997_1702.mpg&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml
        self.createLinkReplay = "/portal.php?type=tv_archive&action=create_link&cmd=auto%2Fmedia%2F{}.mpg&forced_storage=false&disable_ad=false&download=false&force_ch_link_check=false&JsHttpRequest=1-xml"
        #self.createLinkReplay = "/portal.php?type=tv_archive&action=create_link&cmd=auto%20%2Fmedia%2F36830002_5942.mpg&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
        #self.createLinkReplay = "/portal.php?type=tv_archive&action=create_link&cmd=auto%20%2Fmedia%2F{}.mpg&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
        
        #type=epg&action=get_simple_data_table&ch_id=123481&date=2022-07-09&p=2&JsHttpRequest=1-xml
        self.data_table = "/portal.php?type=epg&action=get_simple_data_table&ch_id={}&date={}&p={}&JsHttpRequest=1-xml"
        self.panel ="/panel_api.php"
        self.epg = "/portal.php?type={}&action=get_epg_info&period=72&JsHttpRequest=1-xml"
        self.epgChannel = "/portal.php?type=itv&action=get_short_epg&ch_id={}&size=10&JsHttpRequest=1-xml"
        self.catVOD = "/portal.php?type=vod&action=get_categories&JsHttpRequest=1-xml"
        self.saison = "/portal.php?type=series&action=get_ordered_list&movie_id={}&category={}&season_id=0&episode_id=0&force_ch_link_check=&from_ch_id=0&fav=0&sortby=added&hd=0&not_ended=0&p={}&JsHttpRequest=1-xml"
        self.getsaison = "/portal.php?type=series&action=get_ordered_list&movie_id={}&category={}&genre=*&season_id=0&episode_id=0&force_ch_link_check=&from_ch_id=0&fav=0&sortby=added&hd=0&not_ended=0&p={}&JsHttpRequest=1-xml"
        self.listGenreUrlSeries = "/portal.php?type=series&action=get_ordered_list&movie_id=0&category={}&season_id=0&episode_id=0&force_ch_link_check=&from_ch_id=0&fav=0&sortby=added&hd=0&not_ended=0&p={}&JsHttpRequest=1-xml"
        #categorie, genre => numid du groupe
        #"get_live_categories", "get_vod_categories", "get_live_streams", "get_short_epg", "get_simple_data_table", "get_vod_streams", "get_vod_info"
        
    def getInfos(self, compUrl):
        if self.proxyDict:
            print("proxi")
            info = requests.get(self.urlBase + compUrl, proxies=self.proxyDict, headers=self.headers)
        else: 

            info = requests.get(self.urlBase + compUrl, headers=self.headers)
        return info

    @property 
    def extractUsersPass(self):
        url5 = self.urlBase + "/portal.php?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/1823_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml" 
        res = requests.get(url5, headers=self.headers, timeout=15, verify=False)
        try:
            j = json.loads(res.text)["js"]["cmd"]
            user, pwd= j.split("/")[-3], j.split("/")[-2]
        except:
            user, pwd = "", ""
        return user, pwd
    
    def getUrl(self, compUrl):
        print(compUrl)
        if self.proxyDict:
            print("proxi")
            info = requests.get(compUrl, proxies=self.proxyDict, stream=True, allow_redirects=True)
        else: 
            info = requests.get(compUrl, stream=True, allow_redirects=True)
        return info.url

    @property
    def valideCompte(self):
        try:
            notice(self.urlBase)
            self.getInfos(self.xpcom)
            self.token = self.getInfos(self.tokenUrl).json()['js']['token']
            notice("Token: " + self.token)
            self.headers["Authorization"] = "Bearer %s" %self.token
            
            profile = self.getInfos(self.profileUrl).json()["js"]["id"]
            timez = self.getInfos(self.profileUrl).json()["js"]["default_timezone"]
            
            if profile == None:
                return False

            infoCompte = self.getInfos(self.infosCompteUrl).json()["js"]["phone"]
            self.dateExpiration = infoCompte
            notice("date expiration Compte: " + infoCompte)
            try:
                reste = datetime.datetime.strptime(infoCompte, "%B %d, %Y, %I:%M %p") - datetime.datetime.now()
                notice("reste: " + str(reste.days) + " jours")
                
                if int(reste.days):
                    return True
                else:
                    return False
            except:
                return True
        except Exception as e:
            notice("erreur validité compte " + str(e))
            return False

    def getChaines(self, typ, genre, i):
        tmpChaines = self.getInfos(self.listGenreUrl.format(typ, genre, i)).json()["js"]["data"]
        if typ == "itv":
            self.chaines += [(chaine["cmd"], chaine["name"], chaine["id"], chaine["logo"]) for chaine in tmpChaines]
        else:
            self.chaines += [self.extractInfosVod(chaine) for chaine in tmpChaines]
            
    def listeChaines(self, typ, genre):
        i = 1
        #'allow_local_timeshift': '1'
        #notice(self.urlBase + self.listGenreUrl.format(typ, genre, i))
        page = self.getInfos(self.listGenreUrl.format(typ, genre, i)).json()
        #notice("recup 1ere page (%s): "%genre + str(page))
        self.chaines = [(chaine["cmd"], chaine["name"], chaine["id"], chaine["logo"]) for chaine in page["js"]["data"]]
        nbItems = page["js"]["total_items"]
        itemsPage = page["js"]["max_page_items"]
        nbItems -= itemsPage
        while nbItems > 0:
            i += 1
            threading.Thread(name="iptvC", target=self.getChaines, args=(typ, genre, i,)).start()
            nbItems -= itemsPage
            time.sleep(0.05)
        self.testThread()
        return self.chaines

    def extractInfosVod(self, media):
        idVod = media.get("id")
        name = media.get("name")
        description = media.get("description", "pas d'infos...")
        duree = media.get("time", "0")
        numId = media.get("tmdb_id", "0")
        poster = media.get("screenshot_uri", "")
        certif = media.get("age", "")
        year = media.get("year", "")
        added = media.get("added", "")
        actors = media.get("actors", "")
        director = media.get("director", "")
        rep = media.get("path", "")
        popu = media.get("rating_kinopoisk", "")
        genre = media.get("genres_str", "")
        link = media.get("cmd", "")
        episodes = media.get("series", "[]")
        return (idVod, name, description, duree, numId, poster, certif, year, added, actors, director, rep, popu, genre, link, episodes)


    def listeVod(self, typ, genre, numSerie="", offset="ko"):
        if offset != "ko":
            i = offset
            nbPage = (5 + offset) * 14
        else:
            i = 1
            nbPage = 0
        #"id", "name", "description", "time", "tmdb_id", 'screenshot_uri', "age", 'year', "added", actors", "director", path", 'rating_kinopoisk'
        #('399532', "FR| Fortress 2: Sniper's Eye", "Le film suit l'histoire d'un lieu", 97, '883502', 'http://myf-tv.com:8080/images/byi8ay0EFKsHxxItmFKAbfwSgBU_big.jpg', '12+', '2022-04-29', '2022-04-28 17:55:50', 'Chad Michael Murray', 'Josh Sternfeld', "FR|_Fortress_2:_Sniper's_Eye", 'N/A')
        if numSerie:
            try:
                if numSerie.split(":")[0] == numSerie.split(":")[1]: 
                    requete = self.saison.format(numSerie, genre, i)
                else:
                    requete = self.getsaison.format(quote(numSerie), numSerie, i)
            except:
                requete = self.getsaison.format(quote(numSerie), numSerie, i)
        else:
            requete = self.listGenreUrl.format(typ, genre, i)
            
        #notice(requete)
        page = self.getInfos(requete).json()
        #notice(page)
        self.chaines = [self.extractInfosVod(chaine) for chaine in page["js"]["data"]]
        nbItems = page["js"]["total_items"]
        if nbPage and nbItems >= nbPage:
            nbItems = nbPage
        itemsPage = page["js"]["max_page_items"]
        nbItems -= itemsPage
        while nbItems > 0:
            i += 1
            threading.Thread(name="iptvC", target=self.getChaines, args=(typ, genre, i,)).start()
            nbItems -= itemsPage
            time.sleep(0.1)
        self.testThread()
        return self.chaines

    def testThread(self):
        a = 0
        tActif = True
        while tActif:
            tActif = False
            for t in threading.enumerate():
                if "iptvC" == t.getName():
                    tActif = True
            time.sleep(0.1)
            a += 1
            if a > 150:
                break
        return True

class EpgFournisseur:
    def __init__(self):
        self.epg = {}

    def getAllEpg(self, fournisseurs):
        bd = BookmarkIPTV(BDBOOKMARK)
        for fournisseur in fournisseurs:
            infosFourniseur = bd.recupToken(fournisseur)
            site, mac, token = infosFourniseur[0]
            threading.Thread(name="getepg", target=self.getEpg, args=(fournisseur, site, mac, token)).start()
        self.testThread("getepg")
        return self.epg

    def testThread(self, nom):
        a = 0
        tActif = True
        while tActif:
            tActif = False
            for t in threading.enumerate():
                if nom == t.getName():
                    tActif = True
            time.sleep(0.1)
            a += 1
            if a > 250:
                break
        return True

    def getEpg(self, fournisseur, site, mac, token):
        iptv = IPTVMac(site, mac, token)
        self.epg[fournisseur] = iptv.getInfos(iptv.epg.format(iptv.tv)).json()["js"]["data"]

#=================================================================================== fonctions =====================================================================
def connect(t=False):
    site = ADDON.getSetting("site1")
    mac = str.upper(ADDON.getSetting("mac1"))
    token = ADDON.getSetting("token1")
    #notice(site)
    if t:
        iptv = IPTVMac(site, mac, token)
    else:
        iptv = IPTVMac(site, mac)
    return iptv

def menu():
    xbmcplugin.setPluginCategory(HANDLE, "files")
    xbmcplugin.setContent(HANDLE, "files")
    bd = BookmarkIPTV(BDBOOKMARK)
    adrs = bd.getNom()
    for fournisseur, nom in adrs.items():
        ok = addDirectoryGroupe(nom, isFolder=True, parameters={"action": "loadF", "fourn": fournisseur})                
    ok = addDirectoryGroupe("Ajouter adresse", isFolder=True, parameters={"action": "ajoutIPTV"})
    ok = addDirectoryGroupe("Bank", isFolder=True, parameters={"action": "IPTVbank"})
    ok = addDirectoryGroupe("Favoris", isFolder=True, parameters={"action": "IPTVfav"})
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def ajoutIPTV():
    bd = BookmarkIPTV(BDBOOKMARK)
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Liste', 'compte(s) iptv à inserer?', nolabel="Liste", yeslabel="Unique")
    if not ret:
        repo = dialog.input("Num Anotepad/Pastebin/Rentry/TextUp", type=xbmcgui.INPUT_ALPHANUM)
        if repo:
            heberg = ADDON.getSetting("heberg") 
            if heberg == "Pastebin": 
                tx = getBdPastebin(repo)
            elif heberg == "Rentry":
                tx = getBdRentry(repo)
            elif heberg == "Textup":
                tx = getBdTextup(repo)
            else:
                tx = getBdAnotepad(repo)
            lignes = [x for x in tx.splitlines() if x]
            dictIptv = {}
            for ligne in lignes:
                ligne = ligne.strip()
                if 'http' == ligne[:4]:
                    fournisseur, nom = ligne.split("=")
                    dictIptv[fournisseur] =  []
                else:
                    ligne = ligne.replace(" ", "")
                    masque = r"(?P<mac>\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)"
                    r = re.match(masque, ligne)
                    if r:
                        mac = r.group("mac")
                        dictIptv[fournisseur].append((nom, mac.upper()))

            bd.insertBank(dictIptv)
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Comptes', 'Nombre comptes ajouter dans la bank:\n%s' %"\n".join(["%s => %d" %(k, len(v)) for k, v in dictIptv.items()]) )
            return
    else:
        choix = ["Ajout"]
        dictAdr = bd.getNom()
        adr = list(dictAdr.keys())
        choix += adr
        dialog = xbmcgui.Dialog()
        d = dialog.select("Urls", choix)
        if d != -1:
            if d == 0:
                dialog = xbmcgui.Dialog()
                url = dialog.input("Url fournisseur ex:http://clicktel.xyz:2095", type=xbmcgui.INPUT_ALPHANUM)
                url = "/".join((url.split("/")[:3]))
            else:
                url = adr[d - 1]
            if url:
                if url in dictAdr.keys():
                    nom = dictAdr[url]
                else:
                    dialog = xbmcgui.Dialog()
                    nom = dialog.input("Nom du fournisseur", type=xbmcgui.INPUT_ALPHANUM)
                    if not nom:
                        return
                dialog = xbmcgui.Dialog()
                mac = dialog.input("Adresse Mac ex:00:1A:79:C1:E3:BE", type=xbmcgui.INPUT_ALPHANUM, defaultt="00:1A:79:")
                if not mac:
                    return
                addCompteIptv(url, mac, nom)

def addCompteIptv(url, mac, nom):
    bd = BookmarkIPTV(BDBOOKMARK)
    iptv = IPTVMac(url.strip(), mac.strip())
    ok = iptv.valideCompte
    if ok:
        user, passwd = iptv.extractUsersPass
        groupes = [(genre["title"], genre["id"]) for genre in iptv.getInfos(iptv.genreUrl).json()["js"]]
        dialogTuto = xbmcgui.Dialog()
        dialogTuto.textviewer("Details des bouquets", "\n".join([w[0] for w in groupes]))
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('Compte', 'expiration: %s\nAjouter?' %iptv.dateExpiration, nolabel="Non", yeslabel="Oui")
        if ret:
            bd.insertAdr(url.strip(), mac.strip(), user.strip(), passwd.strip(), iptv.dateExpiration)
            bd.insertGroupe(url, groupes)
            bd.insertNom(nom, url.strip())
        else:
            return

def IPTVbank():
    bd = BookmarkIPTV(BDBOOKMARK)
    liste = bd.getBank()
    dialog = xbmcgui.Dialog()
    compt = dialog.select("Selectionner le compte a importer", ["%s - %s" %(x[0], x[2]) for x in liste])
    if compt != -1:
            nom, url, mac = liste[compt]
            addCompteIptv(url, mac, nom)
            resume = dialog.yesno('Bank', 'Supprimer ce compte de la bank ?')
            if resume:
                bd.delBank(url, mac)

def importCompte(url, mac, nom):
    bd = BookmarkIPTV(BDBOOKMARK)
    iptv = IPTVMac(url.strip(), mac.strip())
    ok = iptv.valideCompte
    if ok:
        user, passwd = iptv.extractUsersPass
        groupes = [(genre["title"], genre["id"]) for genre in iptv.getInfos(iptv.genreUrl).json()["js"]]
        bd.insertAdr(url.strip(), mac.strip(), user.strip(), passwd.strip(), iptv.dateExpiration)
        bd.insertGroupe(url, groupes)
        bd.insertNom(nom, url)
        return 1
    else:
        return 0
        
def activeMac(params):
    bd = BookmarkIPTV(BDBOOKMARK)
    fournisseur = params["fourn"]
    mac = params["mac"]
    ADDON.setSetting("site1", fournisseur)
    ADDON.setSetting("mac1", mac)
    time.sleep(0.1)
    iptv = connect()
    ok = iptv.valideCompte
    if ok:
        ADDON.setSetting(id="token1", value=iptv.token)
        bd.insertToken(fournisseur, mac, iptv.token)
        if params["numId"] == "favs":
            IPTVfav()
        else:
            affChaines(params)

def load(params):
    ADDON.setSetting("passtmp", "")
    fournisseur = params["fourn"]    
    bd = BookmarkIPTV(BDBOOKMARK)
    if fournisseur == "http://activeott.xyz:80":
        bd.deleteChaines(fournisseur)
    macs = bd.getAdr(fournisseur)
    for mac in macs:
        ADDON.setSetting("site1", fournisseur)
        ADDON.setSetting("mac1", mac)
        time.sleep(0.1)
        iptv = connect()
        ok = iptv.valideCompte
        if ok:
            break
    ADDON.setSetting(id="token1", value=iptv.token)
    bd.insertToken(fournisseur, mac, iptv.token)
    liste = bd.getGroupe(fournisseur)
    if liste:
        dictCat = {x[0]: x[1] for x in liste if int(x[2]) == 1}
    else:
        dictCat = {genre["title"]: genre["id"] for genre in iptv.getInfos(iptv.genreUrl).json()["js"]}
    
    typM = iptv.tv
    
    groupes = sorted(dictCat.keys())
    xbmcplugin.setPluginCategory(HANDLE, "files")
    xbmcplugin.setContent(HANDLE, 'files')
    for i, media in enumerate(groupes):
        ok = addDirectoryGroupe(media, isFolder=True, parameters={"action": "affChaine", "numId": dictCat[media], "fourn": fournisseur, "typM": typM })                
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def gestfourn(params):
    notice(params)
    fournisseur = params["fourn"]    
    bd = BookmarkIPTV(BDBOOKMARK)
    liste = bd.getGroupe(fournisseur)
    choix = ["tout"]
    choix += [x[0] for x in liste]
    dialog = xbmcgui.Dialog()
    d = dialog.multiselect("Selectionner les Groupes à Afficher", choix, preselect=[])
    if d:
        if 0 in d:
            listeGroupes = [(1, x) for x in choix[1:]]
        else:
            listeGroupes = [(1, x) if (i + 1) in d else (0, x) for i, x in enumerate(choix[1:])]
        bd.updateGroupe(listeGroupes)
        xbmc.executebuiltin("Container.Refresh")
    return

def gestfournVod(params):
    fournisseur = params["fourn"]
    typM = params["typM"]
    bd = BookmarkIPTV(BDBOOKMARK)
    liste = bd.getGroupeVod(fournisseur, typM)
    if liste:
        choix = ["tout"]
        choix += [x[0] for x in liste]
        dialog = xbmcgui.Dialog()
        d = dialog.multiselect("Selectionner les Groupes VOD à Afficher", choix, preselect=[])
        if d:
            if 0 in d:
                listeGroupes = [(1, x, typM) for x in choix[1:]]
            else:
                listeGroupes = [(1, x, typM) if (i + 1) in d else (0, x, typM) for i, x in enumerate(choix[1:])]
            bd.updateGroupeVod(listeGroupes)
            xbmc.executebuiltin("Container.Refresh")
    return

def addDirectoryGroupe(name, isFolder=True, parameters={}):
    ''' Add a list item to the XBMC UI.'''
    #notice(parameters)
    li = xbmcgui.ListItem(label=name)
    li.setInfo('video', {"title": name, 'plot': "",'mediatype': 'video'})
    li.setArt({'thumb': 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png',
              'icon': ADDON.getAddonInfo('icon'),
              'fanart': ADDON.getAddonInfo('fanart')})
    commands = []
    if parameters["action"] == "affVod":
        commands.append(('[COLOR yellow]Gestion Groupes Vod/Series[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestfournVod&fourn=%s&typM=%s)' %(parameters["fourn"], parameters["typM"], )))
    else:
        commands.append(('[COLOR yellow]Maj EPG[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=bdepg)'))
        if "numId" in parameters.keys():
            commands.append(('[COLOR yellow]Gestion Groupes[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestfourn&fourn=%s)' %(parameters["fourn"])))
            commands.append(('[COLOR yellow]Protection[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=lock&fourn=%s&numId=%s)' %(parameters["fourn"], parameters["numId"])))
            commands.append(('[COLOR yellow]Synchro EPG[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=mapepg&fourn=%s&numId=%s)' %(parameters["fourn"], parameters["numId"])))
            li.addContextMenuItems(commands)
        elif "fourn" in parameters.keys():
            commands.append(('[COLOR yellow]VOD[/COLOR]', 'ActivateWindow(10025, plugin://plugin.video.sendtokodiU2P/?action=getVod&fourn=%s&typM=vod, return)' %(parameters["fourn"])))
            commands.append(('[COLOR yellow]SERIES[/COLOR]', 'ActivateWindow(10025, plugin://plugin.video.sendtokodiU2P/?action=getVod&fourn=%s&typM=series, return)' %(parameters["fourn"])))
            commands.append(('[COLOR yellow]Correction Heure EPG[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestFuseau&fourn=%s)' %(parameters["fourn"])))
    if commands:
        li.addContextMenuItems(commands)
    #notice(parameters)
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def getVodSeries(params):
    ADDON.setSetting("passtmp", "")
    fournisseur = params["fourn"]   
    typM =  params["typM"]
    bd = BookmarkIPTV(BDBOOKMARK)
    infosFournisseur = bd.recupToken(fournisseur)
    if infosFournisseur:
        site, mac, token = infosFournisseur[0]
        ADDON.setSetting("site1", fournisseur)
        ADDON.setSetting("mac1", mac)
        ADDON.setSetting(id="token1", value=token)
    else:
        macs = bd.getAdr(fournisseur)
        for mac in macs:
            ADDON.setSetting("site1", fournisseur)
            ADDON.setSetting("mac1", mac)
            time.sleep(0.1)
            iptv = connect()
            ok = iptv.valideCompte
            if ok:
                break
        ADDON.setSetting(id="token1", value=iptv.token)
        bd.insertToken(fournisseur, mac, iptv.token)
    iptv = IPTVMac(site, mac, token)
    liste = bd.getGroupeVod(fournisseur, typM)
    if liste:
        dictCat = {x[0]: x[1] for x in liste if int(x[2]) == 1}
    else:
        groupes = [(genre["title"], genre["id"]) for genre in iptv.getInfos(iptv.catUrl.format(typM)).json()["js"]]
        bd.insertGroupeVod(fournisseur, groupes, typM)
        dictCat = {x[0]: x[1] for x in groupes}
    groupes = sorted(dictCat.keys())
    xbmcplugin.setPluginCategory(HANDLE, "files")
    xbmcplugin.setContent(HANDLE, 'files')
    for i, media in enumerate(groupes):
        ok = addDirectoryGroupe(media, isFolder=True, parameters={"action": "affVod", "numId": dictCat[media], "fourn": fournisseur, "typM": typM, "offset": 1})                
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def affEpisodes(params):
    #notice(params)
    fournisseur = params["fourn"]
    numId = params["numId"]
    typM = params["typM"]
    bd = BookmarkIPTV(BDBOOKMARK)
    infosFourniseur = bd.recupToken(fournisseur)
    site, mac, token = infosFourniseur[0]
    #site = ADDON.getSetting("site1")
    #mac = str.upper(ADDON.getSetting("mac1"))
    #token = ADDON.getSetting("token1")
    iptv = IPTVMac(site, mac, token)
    numSerie = params["numSerie"]
    medias = iptv.listeVod(typM, numId, numSerie)
    media = [x for x in medias if x[1] == params["saison"]][0]
    media = Media("vod", *media)
    xbmcplugin.setPluginCategory(HANDLE, "Episodes")
    xbmcplugin.setContent(HANDLE, 'movies')
    for episode in media.episodes:
        ok = addDirectoryVod("#Episode %d" %episode, isFolder=False, parameters={"action": "playMediaIptv", "lien": media.link, "iptv": media.title, "typM": "episode", "numEpisode": episode, "fourn": fournisseur}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def affVod(params):
    #notice(params)
    fournisseur = params["fourn"]
    numId = params["numId"]
    typM = params["typM"]
    bd = BookmarkIPTV(BDBOOKMARK)
    infosFournisseur = bd.recupToken(fournisseur)
    site, mac, token = infosFournisseur[0]
    #site = ADDON.getSetting("site1")
    #mac = str.upper(ADDON.getSetting("mac1"))
    #token = ADDON.getSetting("token1")
    iptv = IPTVMac(site, mac, token)
    if "numSerie" in params.keys():
        numSerie = params["numSerie"]
    else:
        numSerie = ""
    if "offset" in params.keys():
        offset = int(params["offset"])
    else:
        offset =  "ko"
    medias = iptv.listeVod(typM, numId, numSerie, offset)
    #"id", "name", "description", "time", "tmdb_id", 'screenshot_uri', "age", 'year', "added", actors", "director", path", 'rating_kinopoisk'
    #('399532', "FR| Fortress 2: Sniper's Eye", "Le film suit l'histoire d'un lieu", 97, '883502', 'http://myf-tv.com:8080/images/byi8ay0EFKsHxxItmFKAbfwSgBU_big.jpg', '12+', '2022-04-29', '2022-04-28 17:55:50', 'Chad Michael Murray', 'Josh Sternfeld', "FR|_Fortress_2:_Sniper's_Eye", 'N/A')
    xbmcplugin.setPluginCategory(HANDLE, typM)
    xbmcplugin.setContent(HANDLE, 'movies')
    for i, media in enumerate(sorted(medias, key=lambda x: x[8], reverse=True)):
        media = Media("vod", *media)
        if typM == "series":
            if  media.link:
                ok = addDirectoryVod("%s" %(media.title), isFolder=True, parameters={"action": "affEpisodes", "numId": numId, "fourn": fournisseur, "typM": typM, "numSerie": media.id, "saison": media.title}, media=media)
            else:
                ok = addDirectoryVod("%s" %(media.title), isFolder=True, parameters={"action": "affVod", "numId": numId, "fourn": fournisseur, "typM": typM, "numSerie": media.id}, media=media)
        else:
            ok = addDirectoryVod("%s" %(media.title), isFolder=False, parameters={"action": "playMediaIptv", "lien": media.link, "iptv": media.title, "typM": typM, "fourn": fournisseur}, media=media)

    if len(medias) > 83 and "offset" in params.keys():
        addDirNext(params)

    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def addDirNext(params):
    isFolder = True
    li = xbmcgui.ListItem(label="[COLOR red]Page Suivante[/COLOR]")
    li.setInfo('video', {"title": "     ", 'plot': "", 'genre': "", "dbid": 500000, 
            "year": "", 'mediatype': "movies", "rating": 0.0})
    li.setArt({
              'thumb': 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/next.png',
              'icon': ADDON.getAddonInfo('icon'),
              'fanart': ADDON.getAddonInfo('fanart'),
              })
    try:
        params["offset"] = str(int(params["offset"]) + 5)
    except: pass
    url = sys.argv[0] + '?' + urlencode(params)
    return xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=isFolder)

def addDirectoryVod(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=name)
    li.setUniqueIDs({ 'tmdb' : media.numId }, "tmdb")
    try:
        int(media.duration)
    except:
        media.duration = "0"
    li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu, "duration": int(media.duration) * 60 })
    
    li.setArt({'icon': media.backdrop,
            'thumb': media.poster,
            'poster': media.poster,
            'fanart': media.backdrop})
    li.setProperty('IsPlayable', 'true')    
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def lock(params):
    fournisseur = params["fourn"]
    numId = params["numId"]
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Protection Groupe', 'Que veux tu faire?', nolabel="Oter la protection", yeslabel="Protéger")
    bd = BookmarkIPTV(BDBOOKMARK)
    if not ret:
        #oter
        d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        if d == "x2015x":
            bd.lockGroupe(fournisseur, numId, 0)
        else:
            return 
    else:
        bd.lockGroupe(fournisseur, numId)

def retireriptv():
    bd = BookmarkIPTV(BDBOOKMARK)
    dictAdr = bd.getNom()
    choix = list(dictAdr.keys())
    dialog = xbmcgui.Dialog()
    d = dialog.select("Gestion retrait", choix)
    if d != -1:
        fournisseur = choix[d]
        ret = dialog.yesno('Retrait', 'Que veux tu faire retirer?', nolabel="Mac", yeslabel="Fournisseur")
        if not ret:
            #mac
            liste = bd.getAdr()
            #url, mac, user, passwd, ddate
            choix = ["%s -> %s" %(x[1], x[4]) for x in liste if x[0] == fournisseur]
            listeMac = [x[1] for x in liste if x[0] == fournisseur]
            dialog = xbmcgui.Dialog()
            d = dialog.select("Macs", choix)
            if d != -1:
                bd.retrait(fournisseur, mac=listeMac[d])
        else:
            bd.retrait(fournisseur)

def verifLock(fournisseur, numId):
    bd = BookmarkIPTV(BDBOOKMARK)
    if "%s*%s" %(fournisseur, numId) in bd.getLockGroupe():
        if ADDON.getSetting("passtmp") == "ok":
            ok = True
        else:
            dialog = xbmcgui.Dialog()
            d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if d == "x2015x":
                ok = True
            else: 
                ok = False
            ADDON.setSetting("passtmp", "ok")
    else:
        ok = True
    return ok

def affepgChann(params):
    #notice(params)
    fournisseur = params["fourn"]
    idChannel = params["channelId"]
    nom = params["title"]
    bd = BookmarkIPTV(BDBOOKMARK)
    infosFourniseur = bd.recupToken(fournisseur)
    site, mac, token = infosFourniseur[0]
    #site = ADDON.getSetting("site1")
    #mac = str.upper(ADDON.getSetting("mac1"))
    #token = ADDON.getSetting("token1")
    iptv = IPTVMac(site, mac, token)
    epgs = iptv.getInfos(iptv.epgChannel.format(idChannel)).json()["js"]
    tx = ""
    for prog in epgs:
        #'category': '', 'director': '', 'actor': ''
        tx += "[COLOR red]%s[/COLOR]\n" %prog["name"]
        tx += "%s - %s\n" %(prog["time"][11:-3], prog["time_to"][11:-3])
        tx += "%s\n\n" %prog["descr"]
    dialogTuto = xbmcgui.Dialog()
    dialogTuto.textviewer(nom, tx)

def affChainesNew(params):
    fournisseur = params["fourn"]
    numId = params["numId"]
    typM = params["typM"]
    if fournisseur in ["http://activeott.xyz:80"]:
        correct = 1
    else:
        correct = 0
    ok = verifLock(fournisseur, numId)
    if ok:  
        bd = BookmarkIPTV(BDBOOKMARK)
        infosFourniseur = bd.recupToken(fournisseur)
        site, mac, token = infosFourniseur[0]  
        #site = ADDON.getSetting("site1")
        #mac = str.upper(ADDON.getSetting("mac1"))
        #token = ADDON.getSetting("token1")
        iptv = IPTVMac(site, mac, token)
        dictEpgNom = {x[0]: x[1] for x in bd.getMapEpg(fournisseur)} 
        macs = bd.getAdr(fournisseur)
        chaines = bd.getChaines(fournisseur, numId)
        epg = iptv.getInfos(iptv.epg.format(iptv.tv)).json()["js"]["data"]
        if not chaines:
            chaines = iptv.listeChaines(typM, numId)
            bd.insertChaines([list(x) + [int(numId), fournisseur] for x in chaines])
        window = feniptv.FenIptv("TV", chaines, epg)    
        window.doModal()
        del window   

def removeDB():
    db = xbmcvfs.translatePath("special://home/userdata/addon_data/plugin.video.sendtokodiU2P/iptv.db")
    xbmcvfs.delete(db)
    showInfoNotification("DB iptv effacée")

def iptvdepfav(params):
    channelId =  params['channelId']
    fourn = params['fourn']
    bd = BookmarkIPTV(BDBOOKMARK)
    liste = bd.getFav()
    channel = [x[1:] for x in liste if x[3] == channelId and x[6] == fourn][0]
    choix = [x[1:] for x in liste if x[1:] != channel]
    dialog = xbmcgui.Dialog()
    d = dialog.select("Deplacer %s avant?" %channel[1], [x[1] for x in choix])
    if d != -1:
        choix.insert(d, channel)
        for i, c in enumerate(choix):
            bd.insertFav(i, c[0], c[1], c[2], c[3], c[4], c[5])
    #ADDON.getSetting("mac1")
    IPTVfav() 

def supfavIptv(params):
    bd = BookmarkIPTV(BDBOOKMARK)
    bd.delFav(params["channelId"], params["fourn"])
    showInfoNotification("Favori effacé")
    #cmd = "ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=IPTVfav,return)"
    #xbmc.executebuiltin(cmd)
    
def addFavIptv(params):
    #notice(params)
    #{'action': 'addFavIptv', 'link': 'ffmpeg http://myf-tv.com:8080/4agfk8MyegAWXZy/cfB0nbR5Cwtte0G/136522', 'nom': 'RTL TVI HEVC', 'num': '136522', 'cover': 'http://covers.dragons-ott.com/JAQUETTE/PICON-LOGO/PICON-ALPHA/picon-belge/rtltvihd.png', 'numbouquet': '29', 'fourn': 'http://myf-tv.com:8080'}
    link, nom, num, poster, numId, fournisseur = params["link"], params["nom"], params["num"], params["cover"], params["numbouquet"], params["fourn"]
    bd = BookmarkIPTV(BDBOOKMARK)
    favs = bd.getFav()
    try:
        posFav = max([x[0] for x in favs])
    except:
        posFav = 0
    dialog = xbmcgui.Dialog()
    d = dialog.input("Nom et position ex: TF1-001", type=xbmcgui.INPUT_ALPHANUM, defaultt="%s-%s" %(nom, str(posFav + 1).zfill(3)))
    if d:
        nom, posFav = "-".join(d.split("-")[:-1]), int(d.split("-")[-1])
        bd.insertFav(posFav, link, nom, num, poster, int(numId), fournisseur)
        showInfoNotification("Ajout Fav's Ok!")

def replay(params):
    notice(params)
    fournisseur = params["fourn"]
    channelId = params["channelId"]
    tabReplay = []
    d = datetime.datetime.now()
    for i in range(7):
        ddate =  d - datetime.timedelta(days=i)
        tabReplay.append(ddate.strftime("%Y-%m-%d"))
    dialog = xbmcgui.Dialog()
    d = dialog.select("Replay du ?", tabReplay)
    if d != -1:
        ddate = tabReplay[d]
        bd = BookmarkIPTV(BDBOOKMARK)
        infosFourniseur = bd.recupToken(fournisseur)
        site, mac, token = infosFourniseur[0]
        iptv = IPTVMac(site, mac, token)
        data = iptv.getInfos(iptv.data_table.format(channelId, ddate, 1)).json()["js"]
        replays = [(x["id"] , x['name'], x['descr'], x['time'].split(' ')[1], x['time_to'].split(' ')[1]) for x in data["data"]]
        nbPages = int(data['total_items'] / data['max_page_items'] + 0.5)
        for i in range(2, nbPages + 1, 1):
            data = iptv.getInfos(iptv.data_table.format(channelId, ddate, i)).json()["js"]
            replays += [(x["id"] , x['name'], x['descr'], x['time'].split(' ')[1], x['time_to'].split(' ')[1]) for x in data["data"]]
        
        xbmcplugin.setPluginCategory(HANDLE, "TV")
        xbmcplugin.setContent(HANDLE, "files")
        #{'id': '4437031_43982', 'mark_archive': 1, 'stop_timestamp': 1657668360, 'mark_rec': 0, 'duration': 4200, 'open': 0, 'actor': '', 'time_to': '2022-07-13 01:26:00', 'descr': "Clara et ses amies aiment l'argent. Elles organisent des parties fines chez les millionnaires et en profitent pour d�pouiller leurs h�tes. Un jour, elles d�cident de tenter un gros coup.", 't_time_to': '01:26', 'start_timestamp': 1657664160, 'correct': '2022-07-13 00:16:00', 'ch_id': '43982', 'name': 'La cambrioleuse', 'time': '2022-07-13 00:16:00', 't_time': '00:16', 'category': '', 'real_id': '43982_1657664160', 'mark_memo': 0, 'director': ''}
        for replay in sorted(replays):
            li = xbmcgui.ListItem(label=replay[1])
            #('4437032_43982', 'Garde à vue', "Deux fillettes ont été violées", '01:26:00', '02:51:00')
            plot = "%s - %s\n%s" %(replay[3], replay[4], replay[2])
            li.setInfo('video', {"title": replay[1], 'plot': plot, 'mediatype': 'video', 'playcount': 1})
            li.setProperty('IsPlayable', 'true')
            parameters={"action": "playMediaIptv", "replay": replay[0], "lien": replay[0], "iptv": replay[1], "fourn": fournisseur}  
            url = sys.argv[0] + '?' + urlencode(parameters)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)               
        xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)
    else:
        return

def IPTVfav():
    bd = BookmarkIPTV(BDBOOKMARK)
    chaines = bd.getFav()
    
    fournisseurs = list(set([x[-1] for x in chaines]))
    dictMacs = {fournisseur: bd.getAdr(fournisseur) for fournisseur in fournisseurs}
    dictEpgNom = {}
    if os.path.isfile(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/epg.bd")):
        for fournisseur in fournisseurs:
            dictEpgNom[fournisseur] = {x[0]: x[1] for x in bd.getMapEpg(fournisseur)}
    
    epg = {}
    correct = {}

    epgFull = EpgFournisseur()
    #notice(fournisseurs)
    epg = epgFull.getAllEpg(fournisseurs)
    #notice(epg.keys())
    """
    for fournisseur in fournisseurs:
        infosFourniseur = bd.recupToken(fournisseur)
        site, mac, token = infosFourniseur[0]
        iptv = IPTVMac(site, mac, token)
        correct[fournisseur] =  bd.getCorrectEpg(site)
        epg[fournisseur] = iptv.getInfos(iptv.epg.format(iptv.tv)).json()["js"]["data"]
    """
    xbmcplugin.setPluginCategory(HANDLE, "TV")
    xbmcplugin.setContent(HANDLE, ADDON.getSetting('contentIptv'))
    for i, (pos, link, nom, numChaine, poster, IdGroupe, fournisseur) in enumerate(chaines):
        infosFourniseur = bd.recupToken(fournisseur)
        site, mac, token = infosFourniseur[0]
        a = time.time() + (3600 * correct.get(fournisseur, 0))
        plot = ""
        thumb = ""
        if  fournisseur in dictEpgNom.keys() and numChaine in dictEpgNom[fournisseur].keys() and dictEpgNom[fournisseur][numChaine] != "Aucun":
            progs = getNomEpgExt(dictEpgNom[fournisseur][numChaine])
            for i, prog in enumerate(progs):
                if (int(a) + 7200) in range(int(prog[0][:-2]), int(prog[1][:-2]), 1):
                    plot = "%s-%s\n[COLOR red]%s[/COLOR]\n%s\n%s" %(datetime.datetime.fromtimestamp(int(prog[0][:-2]) - 7200).strftime('%H:%M'), \
                        datetime.datetime.fromtimestamp(int(prog[1][:-2]) - 7200).strftime('%H:%M'), prog[2], prog[3], prog[4])
                    thumb = prog[5]
                    break
        elif fournisseur in epg.keys() and numChaine in epg[fournisseur].keys():
            for e in epg[fournisseur][numChaine]:
                if e['start_timestamp'] < int(a) and int(a) < e['stop_timestamp']:
                    plot = "%s-%s\n[COLOR red]%s[/COLOR]\n%s" %(datetime.datetime.fromtimestamp(e['start_timestamp']).strftime('%H:%M'), \
                        datetime.datetime.fromtimestamp(e['stop_timestamp']).strftime('%H:%M'), e["name"], e["descr"])
                    thumb = poster
                    break
        li = xbmcgui.ListItem(label=nom)
        li.setInfo('video', {"title": nom, 'plot': plot, 'mediatype': 'video', 'playcount': 1})
        thumb = thumb.replace(" ", "%20")
        poster = poster.replace(" ", "%20")
        li.setArt({
                  'poster': poster,
                  "banner": poster,
                  'icon': poster,
                  #'icon': ADDON.getAddonInfo('icon'),
                  #'fanart': ADDON.getAddonInfo('fanart'),
                  'fanart': thumb })
        if thumb:
            li.setArt({'thumb': thumb})
        else:
            li.setArt({'thumb': poster})
        li.setProperty('IsPlayable', 'true')
        commands = []
        commands.append(('[COLOR yellow]Programmes[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=affepgChann&channelId=%s&title=%s&fourn=%s)' %(numChaine, nom.split("|")[-1].strip(), fournisseur)))
        commands.append(('[COLOR yellow]Synchro EPG[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=mapepg&channelId=%s&fourn=%s&title=%s)' %(numChaine, fournisseur, nom.split("|")[-1].strip())))
        commands.append(('[COLOR yellow]Retirer Favoris[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=iptvsupfav&channelId=%s&fourn=%s)' %(numChaine, fournisseur)))
        commands.append(('[COLOR yellow]Deplacer[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=iptvdepfav&channelId=%s&fourn=%s, return)' %(numChaine, fournisseur)))
        commands.append(('[COLOR yellow]Replay[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=iptvreplay&channelId=%s&fourn=%s, return)' %(numChaine, fournisseur)))
        for m in dictMacs[fournisseur]:
            if m == mac:
                color = "green"
            else:
                color = "red"
            commands.append(('[COLOR %s]%s[/COLOR]' %(color, m), 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=activemac&mac=%s&fourn=%s&numId=favs&typM=itv,return)' %(m, fournisseur)))
        li.addContextMenuItems(commands)
        parameters={"action": "playMediaIptv", "lien": link, "iptv": nom.split("|")[-1].strip(), "fourn": fournisseur}  
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)               
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)
     

def affChaines(params):
    fournisseur = params["fourn"]
    numId = params["numId"]
    typM = params["typM"]
    ok = verifLock(fournisseur, numId)
    if ok:    
        bd = BookmarkIPTV(BDBOOKMARK)
        infosFourniseur = bd.recupToken(fournisseur)
        site, mac, token = infosFourniseur[0]
        #site = ADDON.getSetting("site1")
        #mac = str.upper(ADDON.getSetting("mac1"))
        #token = ADDON.getSetting("token1")
        iptv = IPTVMac(site, mac, token)
        correct =  bd.getCorrectEpg(site)
        if os.path.isfile(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/epg.bd")):
            dictEpgNom = {x[0]: x[1] for x in bd.getMapEpg(fournisseur)} 
        else:
            dictEpgNom = {}
        macs = bd.getAdr(fournisseur)
        chaines = bd.getChaines(fournisseur, numId)
        try:
            epg = iptv.getInfos(iptv.epg.format(iptv.tv)).json()["js"]["data"]
        except:
            epg = {}
        if not chaines:
            chaines = iptv.listeChaines(typM, numId)
            bd.insertChaines([list(x) + [int(numId), fournisseur] for x in chaines])
        #('ffmpeg http://myf-tv.com:8080/zzww6q9eU5krRyM/09gX7NRc93Dup7N/363150', 'FR| PRIME VIDEO Multiplex FHD', '363150', 'http://covers.dragons-ott.com/JAQUETTE/prime-league1.png')
        xbmcplugin.setPluginCategory(HANDLE, "TV")
        xbmcplugin.setContent(HANDLE, ADDON.getSetting('contentIptv'))
        a = time.time() + (3600 * correct)
        for i, chaine in enumerate(chaines):
            plot = ""
            thumb = ""
            if  chaine[2] in dictEpgNom.keys() and dictEpgNom[chaine[2]] != "Aucun":
                #'1650781740.0', '1650787200.0', 'Telematin', 'Magazine de services', "overview", 'https://focus.telerama.fr/1111x625/2022/02/13/fefdf6b798a1e61d26429f35178bc4db4f71599a.jpg')
                progs = getNomEpgExt(dictEpgNom[chaine[2]])
                for i, prog in enumerate(progs):
                    if (int(a) + 7200) in range(int(prog[0][:-2]), int(prog[1][:-2]), 1):
                        plot = "%s-%s\n[COLOR red]%s[/COLOR]\n%s\n%s" %(datetime.datetime.fromtimestamp(int(prog[0][:-2]) - 7200).strftime('%H:%M'), \
                             datetime.datetime.fromtimestamp(int(prog[1][:-2]) - 7200).strftime('%H:%M'), prog[2], prog[3], prog[4])
                        thumb = prog[5]
                        break
            elif chaine[2] in epg.keys():
                for e in epg[chaine[2]]:
                    if e['start_timestamp'] < int(a) and int(a) < e['stop_timestamp']:
                        plot = "%s-%s\n[COLOR red]%s[/COLOR]\n%s" %(datetime.datetime.fromtimestamp(e['start_timestamp']).strftime('%H:%M'), \
                            datetime.datetime.fromtimestamp(e['stop_timestamp']).strftime('%H:%M'), e["name"], e["descr"])
                        thumb = chaine[3]
                        break
            
            li = xbmcgui.ListItem(label=chaine[1])
            li.setInfo('video', {"title": chaine[1], 'plot': plot, 'mediatype': 'video', 'playcount': 1})
            poster = chaine[3].replace(" ", "%20")
            li.setArt({
                  'poster': poster,
                  "banner": poster,
                  'icon': poster,
                  #'icon': ADDON.getAddonInfo('icon'),
                  #'fanart': ADDON.getAddonInfo('fanart'),
                  'fanart': thumb })
            if thumb:
                li.setArt({'thumb': thumb})
            else:
                li.setArt({'thumb': poster})
            li.setProperty('IsPlayable', 'false')
            infChaine = [chaine[0], chaine[1].split("|")[-1].strip(), chaine[2], chaine[3], numId, fournisseur]
            commands = []
            commands.append(('[COLOR yellow]Programmes[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=affepgChann&channelId=%s&title=%s&fourn=%s)' %(chaine[2], chaine[1].split("|")[-1].strip(), fournisseur)))
            commands.append(('[COLOR yellow]Synchro EPG[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=mapepg&channelId=%s&fourn=%s&title=%s)' %(chaine[2], fournisseur, chaine[1].split("|")[-1].strip())))
            commands.append(('[COLOR yellow]Add Favoris[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=addFavIptv&link={}&nom={}&num={}&cover={}&numbouquet={}&fourn={})'.format(*infChaine)))
            commands.append(('[COLOR yellow]Replay[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=iptvreplay&channelId=%s&fourn=%s, return)' %(chaine[2], fournisseur)))
            for m in macs:
                if m == mac:
                    color = "green"
                else:
                    color = "red"
                commands.append(('[COLOR %s]%s[/COLOR]' %(color, m), 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=activemac&mac=%s&fourn=%s&numId=%s&typM=%s,return)' %(m, fournisseur, numId, typM)))
            li.addContextMenuItems(commands)
            link = chaine[0] 
            parameters={"action": "playMediaIptv", "lien": link, "iptv": chaine[1], "fourn": fournisseur}  
            url = sys.argv[0] + '?' + urlencode(parameters)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)               
        xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)
    else:
        return

def getNomEpgExt(tvid=""):
    database = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/epg.bd")
    cnx = sqlite3.connect(database)
    cur = cnx.cursor()
    if tvid:
        cur.execute("SELECT start, stop, title, category, plot, icon FROM progs WHERE channel=?", (tvid,))
        liste = cur.fetchall()
    else:
        cur.execute("SELECT DISTINCT channel FROM progs")
        liste = [x[0] for x in cur.fetchall()]
    cnx.commit()
    cur.close()
    cnx.close
    return liste

def gestFuseau(params):
    bd = BookmarkIPTV(BDBOOKMARK)
    url = params["fourn"]
    dialog = xbmcgui.Dialog()
    listed = [0, 1, 2, 3, 4]
    d = dialog.select("Décalage Heure", ["0", "+1 Heure", "+2 Heures", "+3 Heures", "+4 Heures"])
    if d != -1:
        bd.insertCorrectEpg(url, listed[d])
    return

def mapEpg(params):
    liste = ["Aucun"] + getNomEpgExt()
    fournisseur = params["fourn"]
    bd = BookmarkIPTV(BDBOOKMARK)
    if "channelId" in params.keys():
        tabChannels = [(params["title"], params["channelId"])]
        listeOk = []
    else:
        infosFourniseur = bd.recupToken(fournisseur)
        site, mac, token = infosFourniseur[0]
        #site = ADDON.getSetting("site1")
        #mac = str.upper(ADDON.getSetting("mac1"))
        #token = ADDON.getSetting("token1")
        iptv = IPTVMac(site, mac, token)
        numId = params["numId"]
        listeOk = [x[0] for x in bd.getMapEpg(fournisseur)] 
        chaines = bd.getChaines(fournisseur, numId)
        if not chaines:
            chaines = iptv.listeChaines(typM, numId)
        tabChannels = [(x[1].split("|")[-1].strip(), x[2]) for x in chaines] 
    for nom, numIdChannel in tabChannels:
        if numIdChannel not in listeOk:
            for i, l in enumerate(liste):
                if str.upper(nom[:2]) == str.upper(l[:2]):
                    break
            dialog = xbmcgui.Dialog()
            d = dialog.select(nom, liste, 0, i)
            if d != -1:
                bd.insertMapEpg(fournisseur, numIdChannel, liste[d])
            else:
                break


            
def playMedia(params):
    fournisseur = params["fourn"]
    bd = BookmarkIPTV(BDBOOKMARK)
    site, mac, token = bd.recupToken(fournisseur)[0]
    notice(site)
    #site = ADDON.getSetting("site1")
    #mac = str.upper(ADDON.getSetting("mac1"))
    #token = ADDON.getSetting("token1")
    iptv = IPTVMac(site, mac, token)
    linkCMD = unquote(params['lien'])
    if "typM" in params.keys():
        if params["typM"] == "episode":
            requete = iptv.createLinkSerie.format(linkCMD, params['numEpisode'])
            #notice(requete)
            link = iptv.getInfos(requete).json()["js"]["cmd"].split(" ")[1]
        else:
            link = iptv.getInfos(iptv.createLinkVod.format(params["typM"], linkCMD)).json()["js"]["cmd"].split(" ")[1]
    else:
        if "replay" in params.keys():
            iptv = IPTVMac(site, mac, token)
            link = iptv.getInfos(iptv.createLinkReplay.format(params["replay"].strip())).json()["js"]["cmd"].split(" ")[1]
        else:
            notice(linkCMD)
            n = linkCMD.split("/")[-1]
            linkCMD = "ffmpeg http://localhost/ch/%s" %n
            link = iptv.getInfos(iptv.createLink.format(linkCMD)).json()["js"]["cmd"].split(" ")[1]
            #if "localhost" not in linkCMD and "http" in linkCMD:
            #    link = linkCMD.split(" ")[1]
            #else:
            #    cmd = quote(linkCMD) 
            #    link = iptv.getInfos(iptv.createLink.format(cmd)).json()["js"]["cmd"].split(" ")[1]
    userAg = "|User-Agent=Mozilla"
    #userAg = ""
    result = {"url": link + userAg, "title": params["iptv"]}
    notice(link)
    #xbmc.Player().play(link)
    if result and "url" in result.keys():
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()
        listIt = createListItemFromVideo(result)
        #mplay = MyDialog()
        #mplay.play(result["url"])
        #xbmcplugin.setResolvedUrl(HANDLE, True, listitem=listIt)
        #notice(result["url"])
        xbmc.Player().play(result["url"], listitem=listIt)
if __name__ == '__main__':
  pass