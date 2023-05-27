# -*- coding: utf-8 -*-
import requests
from urllib.parse import quote, urlparse, parse_qs, unquote, urlencode
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