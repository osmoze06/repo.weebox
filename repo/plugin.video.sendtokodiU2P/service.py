# -*- coding: utf-8 -*-
import json
import os
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import requests
import io
import unicodedata
import re
import ast
import sqlite3
import shutil
import time
import imp
from pastebin import Pastebin
from medias import Media, TMDB
import zipfile
import threading
import datetime
#import pyxbmct

try:
    # Python 3
    from urllib.parse import parse_qsl
except ImportError:
    from urlparse import parse_qsl
try:
    # Python 3
    from urllib.parse import unquote, urlencode
    unichr = chr
except ImportError:
    # Python 2
    from urllib import unquote, urlencode
try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser

pyVersion = sys.version_info.major
import imp
if pyVersion == 2:
    moduleC = xbmc.translatePath("special://home/addons/plugin.video.sendtokodiU2P/pasteCrypt2.pyc")
else:
    moduleC = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/pasteCrypt3.pyc")
cryptage = imp.load_compiled("cryptage", moduleC)
#import cryptPaste  as cryptage


class replacement_stderr(sys.stderr.__class__):
    def isatty(self): return False

sys.stderr.__class__ = replacement_stderr


def debug(content):
    log(content, xbmc.LOGDEBUG)


def notice(content):
    log(content, xbmc.LOGINFO)



def log(msg, level=xbmc.LOGINFO):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level)


def linkDownload1Fichier(key, linkUrl):
    params = {
            'url' : linkUrl,
            'inline' : 0,
            'cdn' : 0,
            'restrict_ip':  0,
            'no_ssl' : 0,
            }
    url = 'https://api.1fichier.com/v1/download/get_token.cgi'
    r = requests.post(url, json=params, headers={'Authorization':'Bearer {}'.format(key),'Content-Type':'application/json'})
    try:
        o = r.json()
    except JSONDecodeError:
        pass
    message = ""
    url = ""
    if 'status' in o:
        if o['status'] != 'OK':
            message = r.json()['message']
            o['url'] = ""
        return o["url"], message

    else:
        #key out => No such user
        return url, message

def showInfoNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message, xbmcgui.NOTIFICATION_INFO, 5000)

def showErrorNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message,
                                  xbmcgui.NOTIFICATION_ERROR, 5000)

def getkeyUpto():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    Apikey = addon.getSetting("keyupto")
    #notice("apikey Upto: %s" %Apikey)

    if not Apikey:
        dialog = xbmcgui.Dialog()
        d = dialog.input("ApiKey UptoBox: ", type=xbmcgui.INPUT_ALPHANUM)
        #notice(d)
        addon.setSetting(id="keyupto", value=d)
        key = d
    else:
        key = Apikey
    return key

def getkey1fichier():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    Apikey = addon.getSetting("key1fichier")

    if not Apikey:
        dialog = xbmcgui.Dialog()
        d = dialog.input("ApiKey 1fichier: ", type=xbmcgui.INPUT_ALPHANUM)
        addon.setSetting(id="key1fichier", value=d)
        key = d
    else:
        key = Apikey
    return key

def getresos():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    resos = addon.getSetting("resos")
    try:
        resos, timing =  resos.split("-")
        resos = [x.strip() for x in resos.split("=")[1].split(",")]
        timing = timing.split("=")[1]
    except:
        resos = ("720", "1080", "2160")
        timing = 0
    return resos, timing

def getkeyAlldebrid():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    Apikey = addon.getSetting("keyalldebrid")
    return Apikey

def getkeyRealdebrid():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    Apikey = addon.getSetting("keyrealdebrid")
    return Apikey

def gestionBD(*argvs):
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/serie.db'))
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS serie(
                      `id`    INTEGER PRIMARY KEY,
                      numId TEXT,
                      title TEXT,
                      saison TEXT,
                      reso TEXT,
                      pos INTEGER,
                      UNIQUE (title, saison))
                        """)
    cnx.commit()
    if argvs[0] == "update":
        cur.execute("REPLACE INTO serie (numId, title, saison, reso, pos) VALUES (?, ?, ?, ?, ?)", argvs[1:])
        cnx.commit()
        return True
    elif argvs[0] == "get":
        cur.execute("SELECT reso FROM serie WHERE title=? AND saison=?", argvs[1:])
        reso = cur.fetchone()
        return reso
    elif argvs[0] == "last":
        cur.execute("SELECT numId, title, saison, reso FROM serie ORDER BY id DESC LIMIT 1")
        liste = cur.fetchone()
        if liste:
            return liste
        else:
            return ["", "", "", ""]
    cur.close()
    cnx.close()

def detailsMedia(params):
    paramstring = params["lien"].split("*")
    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typMedia:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    numId = params["u2p"]  
    u2p = params["u2p"]  
    dialog = xbmcgui.Dialog()
    if u2p and numId != "divers":
        choix = ["Bande Annonce", "Lire", "Acteurs", "Similaires", "Recommendations"]
        selected = dialog.select("Choix", choix, 0, 0)
        if selected != -1:
            if u2p  and numId != "divers":
                if "Bande Annonce" == choix[selected]:
                    mdb = TMDB(__keyTMDB__)
                    tabBa = mdb.getNumIdBA(numId, typMedia)
                    if tabBa:
                        selectedBa = dialog.select("Choix B.A", ["%s (%s)" %(x[0], x[1]) for x in tabBa], 0, 0)
                        if selectedBa  != -1:
                            keyBa = tabBa[selectedBa][2] 
                            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/?action=play_video&videoid={})".format(keyBa), True)                            
                    return
                elif choix[selected] in ["Similaires", "Recommendations"]:
                    loadSimReco(numId, typMedia, choix[selected])
                    return
                elif "Acteurs" == choix[selected]:
                        affCast(numId, typMedia)
                elif "Lire" == choix[selected]:
                    cr = cryptage.Crypt()
                    dictResos = cr.extractReso([(x.split("#")[0].split("@")[0], x.split("#")[0].split("@")[1]) for x in paramstring])
                    dictResos = {x.split("#")[0].split("@")[1]: dictResos[x.split("#")[0].split("@")[1]] if dictResos[x.split("#")[0].split("@")[1]] else x.split("#")[1] for x in paramstring}
                    tabNomLien = ["Lien N° %d (%s - %.2fGo)" %(i + 1, dictResos[x.split("#")[0].split("@")[1]][0], (int(dictResos[x.split("#")[0].split("@")[1]][1]) / 1000000000.0)) for i, x in enumerate(paramstring)]
                    tabRelease = [dictResos[x.split("#")[0].split("@")[1]][2] for i, x in enumerate(paramstring)]
                    tabLiens = [(x, paramstring[i], tabRelease[i]) for i, x in enumerate(tabNomLien)]
                    affLiens(numId, typMedia, tabLiens)

def detailsTV(params):
    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typMedia:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    numId = params["u2p"]  
    u2p = params["u2p"]  
    dialog = xbmcgui.Dialog()
    if u2p and numId != "divers":
        sql = "SELECT DISTINCT saison FROM tvshowEpisodes WHERE numId={}".format(numId)
        saisons = extractMedias(sql=sql, unique=1)
        choix = ["Bande Annonce"] + saisons + ["Similaires", "Recommendations"]
        selected = dialog.select("Choix", choix, 0, 0)
        if selected != -1:
            if u2p  and numId != "divers":
                if "Bande Annonce" == choix[selected]:
                    mdb = TMDB(__keyTMDB__)
                    tabBa = mdb.getNumIdBA(numId, typMedia)
                    if tabBa:
                        selectedBa = dialog.select("Choix B.A", ["%s (%s)" %(x[0], x[1]) for x in tabBa], 0, 0)
                        if selectedBa  != -1:
                            keyBa = tabBa[selectedBa][2] 
                            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/?action=play_video&videoid={})".format(keyBa), True)                            
                    return
                elif choix[selected] in ["Similaires", "Recommendations"]:
                    loadSimReco(numId, typMedia, choix[selected])
                    return
                else:
                    affEpisodes(numId, choix[selected])

def affEpisodes(numId, saison):
    typM = "episode"
    xbmcplugin.setPluginCategory(__handle__, "Episodes")
    xbmcplugin.setContent(__handle__, 'episodes')
    sql = "SELECT * FROM tvshowEpisodes WHERE numId={} AND saison='{}'".format(numId, saison)
    liste = extractMedias(sql=sql)
    mdb = TMDB(__keyTMDB__)
    tabEpisodes = mdb.saison(numId, saison.replace("Saison ", ""))
    for l in liste:
        notice(l)
        try:
            lFinale = list(l) + list([episode for episode in tabEpisodes if int(l[2].split("E")[1]) == episode[-1]][0])
        except:
            lFinale = list(l) + ["Episode", "Pas de synopsis ....", "", "", "", int(saison.replace("Saison ", "")) , int(l[2].split("E")[1])]
        #notice(lFinale) 
        media = Media("episode", *lFinale)
        media.typeMedia = typM
        media.numId = int(numId)
        addDirectoryEpisodes("%s" %(media.title), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def addDirectoryEpisodes(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=("%s (%s)" %(name, media.year)))
    if isFolder:
        li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, "dbid": media.numId + 500000,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu})
    else:
        li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, "dbid": media.numId + 500000,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu})
    
    li.setArt({'icon': media.backdrop,})
    
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
                
def affLiens(numId, typM, liste):
    xbmcplugin.setPluginCategory(__handle__, "Liens")
    xbmcplugin.setContent(__handle__, 'movies')
    for l in liste:
        media = Media("lien", *l)
        media.typeMedia = typM
        media.numId = int(numId)
        if typM == "movie":
            addDirectoryFilms("%s" %(media.title), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def getParams(paramstring, u2p=0):
    result = {}
    paramstring = paramstring.split("*")

    # ===================================================================== resos ===========================================================
    resos, timing = getresos()
    histoReso = None
    cr = cryptage.Crypt()
    dictResos = cr.extractReso([(x.split("#")[0].split("@")[0], x.split("#")[0].split("@")[1]) for x in paramstring])
    dictResos = {x.split("#")[0].split("@")[1]: dictResos[x.split("#")[0].split("@")[1]] if dictResos[x.split("#")[0].split("@")[1]] else x.split("#")[1] for x in paramstring}
    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typMedia:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    #notice("type media " + typMedia)
    #notice(xbmc.getInfoLabel('ListItem.DBID'))
    #notice(xbmc.getInfoLabel('ListItem.DBTYPE'))
    #numId = xbmc.getInfoLabel('ListItem.DBID')
    
    if typMedia != "movie":
        title = xbmc.getInfoLabel('ListItem.TVShowTitle')
        saison = xbmc.getInfoLabel('ListItem.Season')
        #notice("title " + xbmc.getInfoLabel('Player.Title'))
        if xbmc.Player().isPlaying():
            infoTag = xbmc.Player().getVideoInfoTag()
            title = infoTag.getTVShowTitle()
            saison = infoTag.getSeason()
        notice("serie" + title)
        histoReso = None
        if title:
            idDB = xbmc.getInfoLabel('ListItem.DBID')
            histoReso = gestionBD("get", title, saison)
            notice("histo %s" %histoReso)
        else:
            liste = gestionBD("last")
            if liste:
                idDB, title, saison, reso = liste
                histoReso = (reso, )

    pos = 0
    if histoReso and histoReso[0]:
        resos = [histoReso[0]] + resos
        timing = 2
    if u2p:
        timing = 0
        numId = u2p
    try:
        for reso in resos:
            notice(reso)
            for i, lien in enumerate(paramstring):
                if reso in dictResos[lien.split("#")[0].split("@")[1]][0]:
                    pos = i
                    raise StopIteration
    except StopIteration: pass
    # ========================================================================================================================================

    selected = 0
    if len(paramstring) == 1:
        result['url'] = paramstring[0].split("#")[0]
    else:
        dialog = xbmcgui.Dialog()
        #if u2p and numId != "divers":
        #    tabNomLien = ["Bande Annonce"]
        #else:
        #    tabNomLien = []
        tabNomLien = []

        try:
            tabNomLien += ["Lien N° %d (%s - %.2fGo)" %(i + 1, dictResos[x.split("#")[0].split("@")[1]][0], (int(dictResos[x.split("#")[0].split("@")[1]][1]) / 1000000000.0)) for i, x in enumerate(paramstring)]
        except:
            tabNomLien += ["Lien N° %d (ind)" %(i + 1) for i, x in enumerate(paramstring)]
        #if u2p and numId != "divers":    
        #    tabNomLien += ["Casting", "Similaires", "Recommendations"]
        selected = dialog.select("Choix lien", tabNomLien, int(timing) * 1000, pos)
        if selected != -1:
            if u2p  and numId != "divers":
                if "Bande Annonce" == tabNomLien[selected]:
                    mdb = TMDB(__keyTMDB__)
                    tabBa = mdb.getNumIdBA(numId, typMedia)
                    if tabBa:
                        selectedBa = dialog.select("Choix B.A", ["%s (%s)" %(x[0], x[1]) for x in tabBa], 0, 0)
                        if selectedBa  != -1:
                            keyBa = tabBa[selectedBa][2] 
                            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/?action=play_video&videoid={})".format(keyBa), True)
                            
                    return
                elif tabNomLien[selected] in ["Similaires", "Recommendations"]:
                    loadSimReco(numId, typMedia, tabNomLien[selected])
                    return
                else:
                    result['url'] = paramstring[selected - 1].split("#")[0]
                    reso = dictResos[paramstring[selected - 1].split("#")[0].split("@")[1]][0]
            else:
                result['url'] = paramstring[selected].split("#")[0]
                reso = dictResos[paramstring[selected].split("#")[0].split("@")[1]][0]
        else:
            return

    if typMedia != "movie" and title:
        gestionBD("update", idDB, title, saison, reso, pos)

    # debridage
    ApikeyAlldeb = getkeyAlldebrid()
    ApikeyRealdeb = getkeyRealdebrid()
    if ApikeyAlldeb:
        erreurs = ["AUTH_MISSING_AGENT", "AUTH_BAD_AGENT", "AUTH_MISSING_APIKEY", "AUTH_BAD_APIKEY"]
        urlDedrid, status = cr.resolveLink(result['url'].split("@")[0], result['url'].split("@")[1], keyAllD=ApikeyAlldeb)
        result['url'] = urlDedrid.strip()
        if status in erreurs:
                addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
                addon.setSetting(id="keyalldebrid", value="")
    elif ApikeyRealdeb:
        urlDedrid, status = cr.resolveLink(result['url'].split("@")[0], result['url'].split("@")[1], keyRD=ApikeyRealdeb)
        result['url'] = urlDedrid.strip()
        if status == "err":
                addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
                addon.setSetting(id="keyrealdebrid", value="")
    else:
        urlDedrid, status = cr.resolveLink(result['url'].split("@")[0], result['url'].split("@")[1], key=getkeyUpto())
        result['url'] = urlDedrid.strip()
        if status == 16:
            addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
            addon.setSetting(id="keyupto", value="")

    if result['url'][:-4] in [".mkv", ".mp4"]:
        title = unquote(result['url'][:-4].split("/")[-1])#, encoding='latin-1', errors='replace')
    else:
        title = unquote(result['url'].split("/")[-1])#, encoding='latin-1', errors='replace')
    try:
        title = unicode(title, "utf8", "replace")
    except: pass
    result["title"] = title
    #notice(result)
    return result

def loadSimReco(numId, typM, recherche):
    notice("typ demande " + recherche)
    dictTyp = {"tvshow": "tv", "movie": "movie"}
    mdb = TMDB(__keyTMDB__)
    if recherche == "Similaires":
        liste = mdb.suggReco(numId, dictTyp[typM], "similar")
    elif recherche == "Recommendations":
        liste = mdb.suggReco(numId, dictTyp[typM], "recommendations")
    if typM == "movie":
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) FROM movie as m \
                        WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
    else:
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu FROM tvshow as m \
                        WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
    movies = extractMedias(sql=sql)
    affMovies(typM, movies)

def extractMedias(limit=0, offset=1, sql="", unique=0):
    cnx = sqlite3.connect(__repAddon__ + "medias.bd")
    cur = cnx.cursor()
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
    cur.close()
    cnx.close()
    return requete

def ventilationHK():
    xbmcplugin.setPluginCategory(__handle__, "Menu")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choix = [("Films, Docu, concerts....", {"action":"MenuFilm"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Bibliothéque de films, concerts, spectacles et documentaires"),
    ("Divers....", {"action":"MenuDivers"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Sports, Show TV, FANKAI, etc..."),
    ("Series & Animes", {"action":"MenuSerie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Bibliothéque séries , animation & animes japonais"),
    ]
    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte,'mediatype': 'video'})
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def diversHK():
    if "groupe" in __params__.keys():
        #title, overview, year, poster, link, numId
        sql = "SELECT title, groupe||' ('||repo||')', '', '', 'divers', '', '', link FROM divers WHERE repo='{}' AND groupe='{}'".format(__params__["repo"].replace("'", "''"), __params__["groupe"].replace("'", "''"))
        movies = extractMedias(sql=sql)
        #notice(movies)
        affMovies("movie", sorted(movies))

    elif "repo" in __params__.keys():
        if __params__["repo"] == "adulte":
            dialog = xbmcgui.Dialog()
            d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if d == "x2015x":
                ok = True
            else:
                ok = False 
        else:
            ok = True
        if ok:
            sql = "SELECT DISTINCT groupe FROM divers WHERE repo='{}'".format(__params__["repo"].replace("'", "''")) 
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuDivers", "repo":__params__["repo"], "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
    else:
        sql = "SELECT DISTINCT repo FROM divers"
        listeRep = extractMedias(sql=sql, unique=1)
        choix = [(x, {"action":"MenuDivers", "repo":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
        addCategorieMedia(choix)
    

def mediasHK():
    typM = "movie"
    if "famille" in __params__.keys():
        movies = []
        if __params__["famille"] == "Last View":
            liste = bdHK(extract=1)
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) FROM movie as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Last In":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) FROM movie as m ORDER BY m.id DESC LIMIT 2000 "
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "cast":
            mdb = TMDB(__keyTMDB__)
            liste = mdb.person(__params__["u2p"])
            notice(__params__["u2p"])
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) FROM movie as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Liste Aléatoire":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId)  FROM movie as m ORDER BY RANDOM() LIMIT 200 "
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Search":
            dialog = xbmcgui.Dialog()
            d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
            if len(d) > 2:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) \
                        FROM movie as m WHERE m.title LIKE {} ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Groupes Contrib":
            sql = "SELECT DISTINCT groupeParent FROM movieGroupe"
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuFilm", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        elif __params__["famille"] == "Saga":
            sql = "SELECT numId, title, overview, poster FROM saga"
            movies = extractMedias(sql=sql)
            typM = "saga"
        elif __params__["famille"] == "sagaListe":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) \
                    FROM movie as m WHERE m.numId IN (SELECT f.numId FROM sagaTitle as f WHERE f.numIdSaga={})".format(__params__["numIdSaga"])
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Année(s)":
            dialog = xbmcgui.Dialog()
            d = dialog.input("Entrer Année => 2010 / Groupe d'années => 2010:2014", type=xbmcgui.INPUT_ALPHANUM)
            if d:
                an = d.split(":")
                if len(an) == 1:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) \
                        FROM movie as m WHERE m.year={}".format(an[0])
                else:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) \
                        FROM movie as m WHERE m.year>={} and m.year<={}".format(an[0], an[1])
                movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Genre(s)":
            mdb = TMDB(__keyTMDB__)
            tabGenre = mdb.getGenre()
            dialog = xbmcgui.Dialog()
            genres = dialog.multiselect("Selectionner le/les genre(s)", tabGenre, preselect=[])
            if genres:
                genresOk = " or ".join(["m.genre LIKE '%%%s%%'" %tabGenre[x] for x in genres])
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) \
                        FROM movie as m WHERE " + genresOk
                movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Favoris":
            pass
        else:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) \
                    FROM movie as m WHERE m.numId IN (SELECT f.numId FROM movieFamille as f WHERE f.famille='{}') ORDER BY m.title COLLATE NOCASE ASC".format(__params__["famille"])
            movies = extractMedias(sql=sql)
            #notice(movies)
        affMovies(typM, movies)
    if "groupe" in __params__.keys():
        sql = "SELECT  groupeFille FROM movieGroupe WHERE groupeParent='{}'".format(__params__["groupe"].replace("'", "''"))
        listeRep = extractMedias(sql=sql, unique=1)
        if len(listeRep) == 1 or not listeRep:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) FROM movie as m \
                            WHERE m.numId IN (SELECT d.numId FROM movieGroupeDetail as d WHERE d.groupe='{}')".format(__params__["groupe"].replace("'", "''"))
            movies = extractMedias(sql=sql)
            affMovies(typM, movies)
        else:
            choix = [(x, {"action":"MenuFilm", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
    else:
        sql = "SELECT DISTINCT famille FROM movieFamille"
        listeRep = extractMedias(sql=sql, unique=1)
        for cat in ["Last In", "Last View", "Liste Aléatoire", "Search", "Groupes Contrib", "Saga", "Année(s)", "Genre(s)"]:
            listeRep.append(cat)
        choix = [(x, {"action":"MenuFilm", "famille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in listeRep]
        addCategorieMedia(choix)

def seriesHK():
    typM = "tvshow"
    if "famille" in __params__.keys():
        movies = []
        if __params__["famille"] == "Last View":
            liste = bdHK(extract=1, typM="tvshow")
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu FROM tvshow as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Last In":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu FROM tvshow as m ORDER BY m.id DESC LIMIT 300 "
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Liste Aléatoire":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu FROM tvshow as m ORDER BY RANDOM() LIMIT 200 "
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Search":
            dialog = xbmcgui.Dialog()
            d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
            if len(d) > 2:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu \
                        FROM tvshow as m WHERE m.title LIKE {} ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Année(s)":
            dialog = xbmcgui.Dialog()
            d = dialog.input("Entrer Année => 2010 / Groupe d'années => 2010:2014", type=xbmcgui.INPUT_ALPHANUM)
            if d:
                an = d.split(":")
                if len(an) == 1:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu \
                        FROM tvshow as m WHERE m.year={}".format(an[0])
                else:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu \
                        FROM tvshow as m WHERE m.year>={} and m.year<={}".format(an[0], an[1])
                movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Genre(s)":
            mdb = TMDB(__keyTMDB__)
            tabGenre = mdb.getGenre(typM="tv")
            dialog = xbmcgui.Dialog()
            genres = dialog.multiselect("Selectionner le/les genre(s)", tabGenre, preselect=[])
            if genres:
                genresOk = " or ".join(["m.genre LIKE '%%%s%%'" %tabGenre[x] for x in genres])
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu \
                        FROM tvshow as m WHERE " + genresOk
                movies = extractMedias(sql=sql)
        elif __params__["famille"] == "#Documentaires":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu \
                        FROM tvshow as m WHERE m.genre like '%%Documentaire%%'" 
            movies = extractMedias(sql=sql)
        elif __params__["famille"] == "Groupes Contrib":
            sql = "SELECT DISTINCT groupeParent FROM tvshowGroupe"
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuSerie", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        else:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu \
                    FROM tvshow as m WHERE m.numId IN (SELECT f.numId FROM tvshowFamille as f WHERE f.famille='{}') ORDER BY m.title COLLATE NOCASE ASC".format(__params__["famille"])
            movies = extractMedias(sql=sql)
            #notice(movies)
        affMovies(typM, movies)
    if "groupe" in __params__.keys():
        sql = "SELECT  groupeFille FROM tvshowGroupe WHERE groupeParent='{}'".format(__params__["groupe"].replace("'", "''"))
        listeRep = extractMedias(sql=sql, unique=1)
        notice(listeRep)
        if len(listeRep) == 1 or not listeRep:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu FROM tvshow as m \
                            WHERE m.numId IN (SELECT d.numId FROM tvshowGroupeDetail as d WHERE d.groupe='{}')".format(__params__["groupe"].replace("'", "''"))
            movies = extractMedias(sql=sql)
            affMovies(typM, movies)
        else:
            choix = [(x, {"action":"MenuSerie", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
    else:
        sql = "SELECT DISTINCT famille FROM tvshowFamille"
        listeRep = extractMedias(sql=sql, unique=1)
        for cat in ["#Documentaires", "Last In", "Last View", "Liste Aléatoire", "Search", "Groupes Contrib", "Année(s)", "Genre(s)"]:
            listeRep.append(cat)
        choix = [(x, {"action":"MenuSerie", "famille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in listeRep]
        addCategorieMedia(choix)

def addCategorieMedia(choix):
        xbmcplugin.setPluginCategory(__handle__, "Choix Categorie")
        addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
        isFolder = True
        for ch in sorted(choix):
            name, parameters, picture, texte = ch
            li = xbmcgui.ListItem(label=name)
            li.setInfo('video', {"title": name, 'plot': texte, 'mediatype': 'video'})
            li.setArt({'thumb': picture,
                      'icon': addon.getAddonInfo('icon'),
                      'fanart': addon.getAddonInfo('fanart')})
            url = sys.argv[0] + '?' + urlencode(parameters)

            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def affCast(numId, typM):
    xbmcplugin.setPluginCategory(__handle__, "Acteurs / Réalisateur")
    xbmcplugin.setContent(__handle__, 'movies')
    mdb = TMDB(__keyTMDB__)
    liste = mdb.castFilm(numId)
    notice(liste)
    for l in liste:
        media = Media("cast", *l)
        media.typeMedia = typM
        if typM == "movie":
            addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action":"MenuFilm", "famille": "cast", "u2p": media.numId}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)


def affMovies(typM, medias):
    xbmcplugin.setPluginCategory(__handle__, typM)
    xbmcplugin.setContent(__handle__, 'movies')
    for media in medias:
        media = Media(typM, *media)
        if typM == "saga":
            addDirectoryFilms(media.title, isFolder=True, parameters={"action":"MenuFilm", "famille": "sagaListe", "numIdSaga": media.numId}, media=media)
        else:
            if media.numId == "divers":
                media.numId = 0
                addDirectoryFilms("%s (%s)" %(media.title, media.year), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId}, media=media)
            else:
                if typM == "movie":
                    addDirectoryFilms("%s (%s)" %(media.title, media.year), isFolder=True, parameters={"action": "detailM", "lien": media.link, "u2p": media.numId}, media=media)
                else:
                    addDirectoryFilms("%s (%s)" %(media.title, media.year), isFolder=True, parameters={"action": "detailT", "lien": media.link, "u2p": media.numId}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def addDirectoryFilms(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''

    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=name)
    #, "dbid": media.numId
    if isFolder:
        li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, "dbid": media.numId + 500000,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu})
    else:
        li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, "dbid": media.numId + 500000,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu, 'isplayable': True})
    
    li.setArt({'thumb': media.poster,
              'icon': addon.getAddonInfo('icon'),
              'icon': addon.getAddonInfo('icon'),
              'fanart': addon.getAddonInfo('fanart')})
    #commands = []
    #commands.append(( 'Similaires3', "RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=MenuFilm)"))
    #li.addContextMenuItems( commands )
    
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def menuPbi():
    xbmcplugin.setPluginCategory(__handle__, "Choix Pbi2kodi")
    xbmcplugin.setContent(__handle__, 'videos')
    for choix in [ ("1. OS", {"action":"os"}, "os.png", "Choix du répertoire de destination des STRM, le chemin correspondant doit exister, sinon crééz le"),
                    ("2. API key Debridage", {"action":"apiConf"}, "debrid.png", 'Alldebrid est prioritaire , et la key Alldebrid doit etre associée avec le lecteur "u2p"'),
                    ("3. Edition Paste", {"action":"ePaste"}, "pastebin.png", "Id AnotePad des Id cryptées."),
                    ("4. Création STRM", {"action":"strms"}, "strm.png", "Création des fichiers STRM et NFO dans le repertoire choisi, c'est un update donc il ne crée que les fichiers inexistants"),
                    ("5. Création GROUPE", {"action":"groupe"}, "groupe.png", "La création doit etre faite aprés le scrap kodi des films et series"),
                    ("6. Clear & Création STRM", {"action":"clearStrms"}, "cStrm.png", "Efface et recrée tous les fichiers STRM"), ("7. Resolutions et default Timing", {"action":"resos"}, "pastebin.png", "Choix des resos prioritaire & timing default lancement média en secondes (0=illimité)"),
                    ("8. Import DataBase", {"action":"bd"}, "strm.png", "Import or Update DATEBASE Kodi (version beta test)"),
                    ("9. Gestion Thumbnails", {"action":"thmn"}, "cStrm.png", "Taille du répertoire thumbnails 7000=800M environ, au dela les plus anciennes seront effacées (0=illimité)"),
                    ("10. Choix Repo", {"action":"choixrepo"}, "pastebin.png", "Choix des catégories à ajouter dans le skin (Estuary)"),
                    ("11. Choix Listes Intelligentes", {"action":"choixliste"}, "pastebin.png", "Choix des listes intelligentes"),
                    ("12. Choix Films", {"action":"movies"}, "pastebin.png", "Complement films"),]:
        addDirectoryItemLocal(choix[0], isFolder=True, parameters=choix[1], picture=choix[2], texte=choix[3])

    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)
    
def addDirectoryItemLocal(name, isFolder=True, parameters={}, picture="", texte="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=name)
    

    #'playcount':0, "status": "Continuing"
    li.setInfo('video', {"title": name, 'plot': texte, 'mediatype': 'video', "overlay": 6})
    li.setArt({'thumb': 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s' %picture,
              'icon': addon.getAddonInfo('icon'),
              'icon': addon.getAddonInfo('icon'),
              'fanart': addon.getAddonInfo('fanart')})
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def selectOS():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choixOs = ["WIN (D:\\kodiBase\\)", "LIBREELEC (/storage/downloads/Kodi/)",  "ANDROID (/storage/emulated/0/kodiBase/)",  "LINUX (/home/(user)/kodiBase/)", "XBOX (U:\\Users\\UserMgr0\\AppData\\Local\\Packages\\XBMCFoundation.Kodi_4n2hpmxwrvr6p\\LocalState\\userdata\\)", 'LOCAL', "Mon repertoire"]
    dialogOS = xbmcgui.Dialog()
    selectedOS = dialogOS.select("Choix OS", choixOs)
    if selectedOS != -1:
        if selectedOS == len(choixOs) - 1:
            osVersion = addon.getSetting("osVersion")
            dialogPaste = xbmcgui.Dialog()
            d = dialogPaste.input("Repertoire STRM", type=xbmcgui.INPUT_ALPHANUM, defaultt=osVersion)
            addon.setSetting(id="osVersion", value=d)
        else:
            addon.setSetting(id="osVersion", value=choixOs[selectedOS])

def configKeysApi():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    dictApi = {"Uptobox": ["keyupto", "Key Api Uptobox"], "Alldebrid": ["keyalldebrid", "Key Api Alldebrid"], "RealDebrid": ["keyrealdebrid", "Key Api RealDebrid"]}
    choixApi = list(dictApi.keys())
    dialogApi = xbmcgui.Dialog()
    selectedApi = dialogApi.select("Choix Api", choixApi)
    if selectedApi != -1:
        key = addon.getSetting(dictApi[choixApi[selectedApi]][0])
        d = dialogApi.input(dictApi[choixApi[selectedApi]][1], type=xbmcgui.INPUT_ALPHANUM, defaultt=key)
        addon.setSetting(id=dictApi[choixApi[selectedApi]][0], value=d)

def makeStrms(clear=0):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Pbi2kodi', 'Extraction Paste... .')
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    osVersion = addon.getSetting("osVersion")
    if "WIN" in osVersion:
        repKodiName = "D:\\kodiBase\\"
    elif "LIBREELEC" in osVersion:
        repKodiName = "/storage/downloads/Kodi/"
    elif "LINUX" in osVersion:
        repKodiName = "/storage/downloads/Kodi/"
    elif "ANDROID" in osVersion:
        repKodiName = "/storage/emulated/0/kodiBase/"
    elif "XBOX" in osVersion:
        repKodiName = "U:\\Users\\UserMgr0\\AppData\\Local\\Packages\\XBMCFoundation.Kodi_4n2hpmxwrvr6p\\LocalState\\userdata\\"
    else:
        repKodiName = osVersion
    lePaste = addon.getSetting("paste")
    dictPaste = idPaste(lePaste)
    for nomRep, tabPaste in dictPaste.items():
        notice(nomRep)
        paramPaste = {"tabIdPbi": tabPaste, "namePbi": 'test', "repKodiName": repKodiName, "clear": clear}
        pbi = Pastebin(**paramPaste)
        pbi.makeMovieNFO(pbi.dictFilmsPaste.values(), clear=clear, progress=pDialog, nomRep=nomRep)
        pDialog.update(0, 'SERIES')
        pbi.makeSerieNFO(pbi.dictSeriesPaste.values(), clear=clear, progress=pDialog, nomRep=nomRep)
        pDialog.update(0, 'ANIMES')
        pbi.makeAnimeNFO(pbi.dictAnimesPaste.values(), clear=clear, progress=pDialog, nomRep=nomRep)
        pDialog.update(0, 'DIVERS')
        pbi.makeDiversNFO(pbi.dictDiversPaste.values(), clear=clear, progress=pDialog, nomRep=nomRep)
    showInfoNotification("strms créés!")

def idPaste(lePaste):
    html_parser = HTMLParser()
    motifAnotepad = r'.*<\s*div\s*class\s*=\s*"\s*plaintext\s*"\s*>(?P<txAnote>.+?)</div>.*'
    rec = requests.get("https://anotepad.com/note/read/" + lePaste, timeout=3)
    r = re.match(motifAnotepad, rec.text, re.MULTILINE|re.DOTALL|re.IGNORECASE)
    tx = r.group("txAnote")
    tx = html_parser.unescape(tx)
    dictLignes = {x.split("=")[0].strip(): [y.strip() for y in x.split("=")[1].split(",")]  for x in tx.splitlines() if x and x[0] != "#"}
    return dictLignes

def editPaste():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    paste = addon.getSetting("paste")
    dialogPaste = xbmcgui.Dialog()
    d = dialogPaste.input("Num AnotePad Pastes", type=xbmcgui.INPUT_ALPHANUM, defaultt=paste)
    addon.setSetting(id="paste", value=d)

def editNbThumbnails():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    paste = addon.getSetting("thumbnails")
    dialogPaste = xbmcgui.Dialog()
    d = dialogPaste.input("Nombre d'images THUMBNAILS conservées (0=illimité)", type=xbmcgui.INPUT_ALPHANUM, defaultt=paste)
    addon.setSetting(id="thumbnails", value=d)


def editResos():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    paste = addon.getSetting("resos")
    dialogPaste = xbmcgui.Dialog()
    d = dialogPaste.input("resos prioritaire & timing", type=xbmcgui.INPUT_ALPHANUM, defaultt=paste)
    addon.setSetting(id="resos", value=d)

def delTag(dataBaseKodi):
    cnx = sqlite3.connect(dataBaseKodi)
    cur = cnx.cursor()
    cur.execute("DELETE FROM tag")
    cur.execute("DELETE FROM tag_link")
    cnx.commit()
    cur.close()
    cnx.close()

def creaGroupe():
    showInfoNotification("Création groupes!")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    osVersion = addon.getSetting("osVersion")
    lePaste = addon.getSetting("paste")
    dictPaste = idPaste(lePaste)
    delTag(__database__)
    for nomRep, tabPaste in dictPaste.items():
        pDialog2 = xbmcgui.DialogProgressBG()
        pDialog2.create('Pbi2kodi', 'Création Groupes (%s)...' %nomRep)
        #notice(nomRep)
        paramPaste = {"tabIdPbi": tabPaste, "namePbi": 'test', "repKodiName": "", "clear": 0}
        pbi = Pastebin(**paramPaste)
        pbi.UpdateGroupe(pbi.dictGroupeFilms, __database__, progress= pDialog2, gr=nomRep)
        #pDialog2.update(10, 'SERIES')
        pbi.UpdateGroupe(pbi.dictGroupeSeries, __database__, mediaType="tvshow", progress= pDialog2, gr=nomRep)
        pDialog2.close()
    showInfoNotification("Groupes créés!")


def getTimeBookmark(numId, dataBaseKodi, typMedia):
    cnx = sqlite3.connect(dataBaseKodi)
    cur = cnx.cursor()
    if typMedia == "movie":
        sql = "SELECT timeInSeconds FROM bookmark WHERE idFile=(SELECT m.idFile FROM movie as m WHERE m.idMovie=%s)" %(numId)
    else:
        sql = "SELECT timeInSeconds FROM bookmark WHERE idFile=(SELECT m.idFile FROM episode as m WHERE m.idEpisode=%s)" %(numId)
    cur.execute(sql)
    seek = [x[0] for x in cur.fetchall() if x]
    cur.close()
    cnx.close()
    if seek:
        return seek[0]
    else:
        return 0

def getSeasonU2P(numId, dataBaseKodi , numEpisode):
    cnx = sqlite3.connect(dataBaseKodi)
    sql = "SELECT c18 FROM episode WHERE c19=(SELECT m.c19 FROM episode as m WHERE m.idEpisode=%s)" %(numId)
    cur = cnx.cursor()
    cur.execute(sql)
    tabEpisodes = sorted([x[0] for x in cur.fetchall() if x])
    cur.close()
    cnx.close()
    return tabEpisodes[int(numEpisode):]


def createListItemFromVideo(video):
    url = video['url']
    title = video['title']
    list_item = xbmcgui.ListItem(title, path=url)
    list_item.setInfo(type='Video', infoLabels={'Title': title})
    return list_item

def getIDfile(f):
    try:
        cnx = sqlite3.connect(__database__)
        cur = cnx.cursor()
        sql = "SELECT idFile FROM files WHERE strFilename=? AND dateAdded IS NOT NULL"
        cur.execute(sql, (f,))
        return cur.fetchone()[0]
    except Exception as e:
        notice("get infos file " + str(e))

def bdHK(sauve=1, pos=0, tt=0, numId=0, extract=0, typM="movie"):
    rPos = 0
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS movie(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      UNIQUE (numId))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS tvshow(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      UNIQUE (numId))
        """)
    cnx.commit()
    if extract:
        cur.execute("SELECT numId FROM %s" %typM)
        rPos = [x[0] for x in cur.fetchall()]
    elif sauve:
        cur.execute("REPLACE iNTO {} (numId, pos, tt) VALUES ({}, {}, {}}])".formt(typM, numId, pos, tt))
        cnx.commit()
    else:
        cur.execute("SELECT pos FROM {} WHERE numId={}".format(typM, numId))
        try:
            rPos = cur.fetchone()[0]
        except: pass
    cur.close()
    cnx.close()
    return rPos



def playMediaHK(params):
    #notice(params)
    numId = params["u2p"]     
    result = getParams(params['lien'], u2p=numId)
    if result and "url" in result.keys():
        url = str(result['url'])
        showInfoNotification("playing title " + result['title'])
        try:
            listIt = createListItemFromVideo(result)
            xbmc.Player().play(url, listIt)
        except Exception as e:
            notice("erreur Play " + str(e))
        threading.Thread(target=gestionThumbnails).start()
        count = 0
        time.sleep(2)
        while not xbmc.Player().isPlaying():
            count = count + 1
            if count >= 20:
                return
            else:
                time.sleep(1)
        notice("numId " + str(numId))
        if numId != "divers" and str(numId) != "0":
            seek = bdHK(sauve=0, numId=int(numId))      
        else:
            seek = 0    
        if seek > 0:
            dialog = xbmcgui.Dialog()
            resume = dialog.yesno('Play Video', 'Resume last position?')
            if resume:
                notice(xbmc.getInfoLabel('Player.Title'))
                xbmc.Player().seekTime(int(seek))
            else:
                notice("delete")

        tt = xbmc.Player().getTotalTime()
        while xbmc.Player().isPlaying():
            t = xbmc.Player().getTime()
            notice(t)
            time.sleep(1)
        if t > 180 and numId != "divers" and str(numId) != "0":
            bdHK(numId=numId, pos=t, tt=tt)
    return


def playMediaOld(params):
    result = getParams(params['lien'])
    if result and "url" in result.keys():
        listIt = createListItemFromVideo(result)
        xbmcplugin.setResolvedUrl(__handle__, True, listitem=listIt) 
        
def playMedia(params):
    typDB = "non auto"
    try:
        lastBD = os.path.normpath(os.path.join(__repAddon__, "lastDB.txt"))
        if "autonome" in open(lastBD, "r").readline():
            typDB = "auto"
    except: pass


    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typMedia:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if typDB == "auto":
        fPlay = sys.argv[0] + sys.argv[2]
        if typMedia != "movie":
            idfile= getIDfile(fPlay)
        else:            
            idfile = xbmc.getInfoLabel('ListItem.DBID')
    else:
        idfile = xbmc.getInfoLabel('ListItem.DBID')
    notice("idFile " + str(idfile))
    notice(xbmc.getInfoLabel('ListItem.Episode'))
    notice(xbmc.getInfoLabel('ListItem.TvShowDBID'))
    notice(xbmc.getInfoLabel('ListItem.PercentPlayed')) 
    notice(xbmc.getInfoLabel('ListItem.EndTimeResume')) 
    notice("fin listem")
    
    result = getParams(params['lien'])
    if result and "url" in result.keys():
        url = str(result['url'])
        showInfoNotification("playing title " + result['title'])
        notice("num id " + str(result))
        notice("handle " + str(__handle__))
        try:
            listIt = createListItemFromVideo(result)
            xbmcplugin.setResolvedUrl(__handle__, True, listitem=listIt) 
            #xbmc.Player().play(url, listIt)
            #xbmc.executebuiltin('PlayMedia(%s)' %url)
        except Exception as e:
            notice("erreur Play " + str(e))
        threading.Thread(target=gestionThumbnails).start()
        count = 0
        time.sleep(2)
        while not xbmc.Player().isPlaying():
            count = count + 1
            if count >= 20:
                return
            else:
                time.sleep(1)
        try:
            infoTag = xbmc.Player().getVideoInfoTag()
            notice(infoTag.getDbId())
            #idfile = infoTag.getDbId()
            notice("idFile " + str(idfile))
            #notice(xbmc.Player().getPlayingFile())
            #typMedia = infoTag.getMediaType()
            #
            seek = getTimeBookmark(idfile,  __database__, typMedia)
        except Exception as e:
            xbmc.Player().pause
            notice(str(e))
            seek = 0

        
        if seek > 0:
            dialog = xbmcgui.Dialog()
            resume = dialog.yesno('Play Video', 'Resume last position?')
            if resume:
                notice(xbmc.getInfoLabel('Player.Title'))
                xbmc.Player().seekTime(int(seek))
        
        #threading.Thread(target=correctionBookmark, args=(idfile, typMedia))
        #importDatabase(debug=0)
        #tx = testDatabase()
        #if tx:
        #    showInfoNotification("New DataBase en ligne  !!!")
        #threading.Thread(target=importDatabase)

        if typDB == "auto":
            tt = xbmc.Player().getTotalTime()
            while xbmc.Player().isPlaying():
                t = xbmc.Player().getTime()
                if tt == 0:
                    tt = xbmc.Player().getTotalTime()
                #notice(t)
                time.sleep(1)
            notice(str(typMedia) + " " + str(idfile))
            if t > 180:
                correctionBookmark(idfile, t, tt, typMedia)
            notice("ok")
        return

def correctionBookmark(idfile, t, tt, typeM):
    try:
        cnx = sqlite3.connect(__database__)
        cur = cnx.cursor()
        notice(typeM)
        if typeM == "movie":
            cur.execute("SELECT idFile FROM movie WHERE idMovie=?", (idfile,))
        #else:
        #    cur.execute("SELECT idFile FROM episode WHERE idEpisode=?", (idfile,))
            idfile = cur.fetchone()[0]
        notice("idefile " + str(idfile))
        try:
            delta = ((1 - t / tt) * 100)
        except:
            delta = 5
        if delta < 4:
            notice("del media bookmark")
            cur.execute("DELETE FROM bookmark WHERE idFile=%s" %idfile)
            cur.execute("UPDATE files SET playCount=1 WHERE idFile=%s" %idfile)
        else:
            cur.execute("SELECT idFile FROM bookmark WHERE idFile=?", (idfile,))
            if cur.fetchone():
                sql0 =  "UPDATE bookmark SET timeInSeconds=? WHERE idFile=?"
                cur.execute(sql0, (t, idfile,))
            else: 
                sql0 = "REPLACE INTO bookmark (idFile, timeInSeconds, totalTimeInSeconds, thumbNailImage, player, playerState, type) VALUES(?, ?, ?, ?, ?, ?, ? )"
                cur.execute(sql0, (idfile, t, tt, None, 'VideoPlayer', None, 1,))
             
        cnx.commit()
        cur.close()
        cnx.close()
    except Exception as e:
        notice("insert bookmark " + str(e))

def majLink(dataBaseKodi):
    lastBD = os.path.normpath(os.path.join(__repAddon__, "lastDB.txt"))
    cnx = sqlite3.connect(dataBaseKodi)
    cur = cnx.cursor()
    if "autonome" not in open(lastBD, "r").readline():
        dateTimeObj = datetime.datetime.now()
        timestampStr = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
     
        oldRep = '/storage/emulated/0/kodibase'
        #newRep = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/kodibase")
        newRep, corr = cheminOs()
        if newRep != "/storage/emulated/0/":
            newRep = os.path.normpath(os.path.join(newRep, "kodibase")) 
            cur.execute("UPDATE path SET strPath = REPLACE(strPath, '%s', '%s')" % (oldRep, newRep))
            cur.execute("UPDATE movie SET c22 = REPLACE(c22, '%s', '%s')" % (oldRep, newRep))
            cur.execute("UPDATE episode SET c18 = REPLACE(c18, '%s', '%s')" % (oldRep, newRep))
            #UPDATE art SET url = REPLACE(url,'smb://my_nas/old_share', 'smb://my_nas/new_share');
            cur.execute("UPDATE tvshow SET c16 = REPLACE(c16, '%s', '%s')" % (oldRep, newRep))
            cur.execute("UPDATE files SET strFilename = REPLACE(strFilename, '%s', '%s'), dateAdded='%s'" % (oldRep, newRep, timestampStr))
            
            if corr:
                cur.execute("UPDATE path SET strPath = REPLACE(strPath,'%s', '%s')" %("/", "\\"))
                cur.execute("UPDATE episode SET c18 = REPLACE(c18,'%s', '%s')" %("/", "\\"))
                cur.execute("UPDATE movie SET c22 = REPLACE(c22,'%s', '%s')" %("/", "\\"))
                cur.execute("UPDATE tvshow SET c16 = REPLACE(c16,'%s', '%s')" %("/", "\\"))
                cur.execute("UPDATE files SET strFilename = REPLACE(strFilename,'%s', '%s')" %("/", "\\"))    
            cnx.commit()

        
        

        # ajout sources
        with open(xbmcvfs.translatePath("special://home/userdata/sources.xml"), "r") as f:
            txSources = f.read()
        with open(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/fileSources.txt"), "r") as f:
            tx = f.read()
            dictSource = {x.split("=")[0]: x.split("=")[1] for x in tx.splitlines()}
        source = """<source>
                <name>{}</name>
                <path pathversion="1">{}</path>
                <allowsharing>true</allowsharing>
            </source>\n"""
        sources = ""
        for k, v in dictSource.items():
            depot = os.path.normpath(v.replace(oldRep, newRep))
            if v.replace(oldRep, newRep) not in txSources:
                sources += source.format(k, depot)
        with open(xbmcvfs.translatePath("special://home/userdata/sources.xml"), "w") as f:
            f.write(txSources.format(**{"sources":sources}))

    cnx2 = sqlite3.connect(__database__)
    cur2 = cnx2.cursor()
    
    cur2.execute("SELECT * FROM bookmark")
    bookmark = cur2.fetchall()
    try:
        cur.executemany("INSERT INTO bookmark VALUES(?, ?, ?, ?, ?, ?, ?, ?)", bookmark)
        cnx.commit()
    except: pass

    cur2.execute("SELECT * FROM files WHERE (lastPlayed OR playCount) AND idfile<400000")
    histoPlay = cur2.fetchall()
    histoPlay = [(x[0], x[1], x[2], x[3] if x[3] and x[3] != 'None' else "", x[4] if x[4] and x[4] != 'None' else "", x[5]) for x in histoPlay]
    #print(histoPlay)
    for h in histoPlay:
        cur.execute("UPDATE files set lastPlayed=?, playCount=? WHERE idFile=? AND idPath=?", (h[4], h[3], h[0], h[1], ))
    cnx.commit()

    cur2.execute("SELECT * FROM files WHERE idfile>400000")
    histoPlay = cur2.fetchall()
    for h in histoPlay:
        cur.execute("INSERT INTO files VALUES(?, ?, ?, ?, ?, ?)", h)
    cnx.commit()


    cur.close()
    cnx.close()
    cur2.close()
    cnx2.close()



def cheminOs():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    osVersion = addon.getSetting("osVersion")
    corr = 0
    if "WIN" in osVersion:
        corr = 1
        repKodiName = "D:\\kodiBase\\"
    elif "LIBREELEC" in osVersion:
        repKodiName = "/storage/downloads/"
    elif "LINUX" in osVersion:
        repKodiName = "/storage/downloads/"
    elif "ANDROID" in osVersion:
        repKodiName = "/storage/emulated/0/"
    elif "XBOX" in osVersion:
        corr = 1
        repKodiName = "U:\\Users\\UserMgr0\\AppData\\Local\\Packages\\XBMCFoundation.Kodi_4n2hpmxwrvr6p\\LocalState\\userdata\\"
    else:
        corr = 1
        repKodiName = osVersion
    return repKodiName, corr

def get_size(rep):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(rep):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def gestionThumbnails():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    nbT = addon.getSetting("thumbnails")
    try:
        nbT = int(nbT)
    except:
        nbT = 0
    if nbT > 0:
        dbTexture = xbmcvfs.translatePath("special://home/userdata/Database/Textures13.db")
        repThumb = xbmcvfs.translatePath("special://thumbnails")
        cnx2 = sqlite3.connect(dbTexture)
        cur2 = cnx2.cursor()
        tabFiles = []
        for dirpath, dirs, files in os.walk(repThumb): 
            for filename in files:
                fname = os.path.normpath(os.path.join(dirpath,filename))
                tabFiles.append(fname)
        if len(tabFiles) > 7000:
            tabFiles.sort(key=os.path.getmtime, reverse=True)
            for f in tabFiles[7000:]:
                head ,tail = os.path.split(f)
                cur2.execute("SELECT id FROM texture WHERE cachedurl LIKE '{}'".format("%" + tail + "%"))
                num = cur2.fetchone()
                if num:
                    cur2.execute("DELETE FROM texture WHERE id=?", (num[0],))
                    cur2.execute("DELETE FROM sizes WHERE idtexture=?", (num[0],))
                xbmcvfs.delete(f) 
        cnx2.commit()
        cur2.close()
        cnx2.close()   

def extractNews(numVersion):
    listeNews = []
    if os.path.isfile(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/u2pBD.bd')):
        cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/u2pBD.bd'))
        cur = cnx.cursor()
        cur.execute("SELECT strm FROM strms WHERE version>?", (numVersion,))
        listeNews = [x[0] for x in cur.fetchall()]
        cur.close()
        cnx.close()
    return listeNews

def testDatabase(typImport="full"):
    ApikeyAlldeb = getkeyAlldebrid()
    ApikeyRealdeb = getkeyRealdebrid()
    ApikeyUpto = getkeyUpto()
    cr = cryptage.Crypt()
    repAddon = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/")
    repStrm, _ = cheminOs()
    if ApikeyUpto:
        tx = cr.updateBD(repAddon, t=typImport, key=ApikeyUpto, typkey="upto")
    elif ApikeyAlldeb:
        tx = cr.updateBD(repAddon, t=typImport, key=ApikeyAlldeb, typkey="alldeb")
    elif ApikeyRealdeb:
        tx = cr.updateBD(repAddon, t=typImport, key=ApikeyRealdeb, typkey="realdeb")
    return tx 

def mepAutoStart():
    if not os.path.isfile(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/maj.txt")):
        repStart = xbmcvfs.translatePath("special://home/addons/service.autoexec/")
        repFileStart = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/maj/")
        try:
            os.mkdir(repStart)
        except: pass
        for f in os.listdir(repFileStart):
             xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/maj/%s" %f), xbmcvfs.translatePath("special://home/addons/service.autoexec/%s" %f))
        open(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/maj.txt"), "w")

def majDatabase():
    importDatabase(debug=0, maj=1)

def createFav():
    favBD = '''\n<favourite name="Import DataBase" thumb="special://home/addons/plugin.video.sendtokodiU2P/resources/png/database.png">PlayMedia(&quot;plugin://plugin.video.sendtokodiU2P/?action=bdauto&quot;)</favourite>'''
    favMovies = '''<favourite name="Films Hors Kodi" thumb="special://home/addons/plugin.video.sendtokodiU2P/resources/png/movies.png">ActivateWindow(10025,&quot;plugin://plugin.video.sendtokodiU2P/?action=movies&quot;,return)</favourite>'''
    try:
        with io.open(xbmcvfs.translatePath("special://home/userdata/favourites.xml"), "r", encoding="utf-8") as f:
            txFavs = f.read()
        pos = txFavs.find("<favourites>")
        pos += len("<favourites>")
        txDeb = txFavs[:pos]
        txFin = txFavs[pos:]
    except:
        txFavs = ""
        txDeb = "<favourites>"
        txFin = "\n</favourites>"

    if favBD not in txFavs: 
            txDeb += "%s\n" %favBD
    if os.path.isfile(os.path.normpath(os.path.join(__repAddon__, "medias.bd"))) and favMovies not in txFavs:  
            txDeb += favMovies 
    with io.open(xbmcvfs.translatePath("special://home/userdata/favourites.xml"), "w", encoding="utf-8") as f:
        f.write(txDeb + txFin)


def importDatabase(typImport="full", debug=1, maj=0):
    repAddon = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/")
    fileBD = os.path.normpath(os.path.join(repAddon, "fichierDB.txt"))
    lastBD = os.path.normpath(os.path.join(repAddon, "lastDB.txt"))
    if os.path.isfile(fileBD):
        tx = open(fileBD, 'r').read().splitlines()
        dictDB = {x.split("=")[0]: x.split("=")[1] for x in tx}
    else:
        dictDB = {"full": ""}
    choixDB = sorted(list(dictDB.keys()))
    if maj:
        try:
            selectedDB = choixDB.index(open(lastBD, 'r').readline())
            notice("position " + str(selectedDB))
        except:
            selectedDB = -1
    else:
        dialogApi = xbmcgui.Dialog()
        if typImport == "autonome":
            choixDB = [x for x in choixDB if "autonome" in x]
        selectedDB = dialogApi.select("Choix DATABASE", choixDB)
    
    if selectedDB != -1:
        # debridage
        tps = time.time()
        a = time.time()
        numRecup = dictDB[choixDB[selectedDB]]
        if debug:
            showInfoNotification("Verif Update")
        ApikeyAlldeb, ApikeyRealdeb, ApikeyUpto = "", "", ""    
        ApikeyAlldeb = getkeyAlldebrid()
        if not ApikeyAlldeb:
            ApikeyRealdeb = getkeyRealdebrid()
            if not ApikeyRealdeb:
                ApikeyUpto = getkeyUpto()
        cr = cryptage.Crypt()
        repStrm, _ = cheminOs()
        try:
            c = open(lastBD, 'r').readline()
            if choixDB[selectedDB] == c:
                fDOWN = 0
            else:
                fDOWN = 1
        except:
            fDOWN = 1
        open(lastBD, 'w').write(choixDB[selectedDB])
        if numRecup:
            if ApikeyUpto:
                tx = cr.updateBD(repAddon, key=ApikeyUpto, typkey="upto", numRentry=numRecup, forceDownload=fDOWN)
            elif ApikeyAlldeb:
                tx = cr.updateBD(repAddon, key=ApikeyAlldeb, typkey="alldeb", numRentry=numRecup, forceDownload=fDOWN)
            elif ApikeyRealdeb:
                tx = cr.updateBD(repAddon, key=ApikeyRealdeb, typkey="realdeb", numRentry=numRecup, forceDownload=fDOWN)
        else:
            if ApikeyUpto:
                tx = cr.updateBD(repAddon, key=ApikeyUpto, typkey="upto", forceDownload=fDOWN)
            elif ApikeyAlldeb:
                tx = cr.updateBD(repAddon, key=ApikeyAlldeb, typkey="alldeb", forceDownload=fDOWN)
            elif ApikeyRealdeb:
                tx = cr.updateBD(repAddon, key=ApikeyRealdeb, typkey="realdeb", forceDownload=fDOWN)
        notice("download %0.2f" %(time.time() - a))
        a = time.time()
        if tx:
            if debug == 0:
                showInfoNotification("Update DataBase en cours, wait ....")
            pDialogBD2 = xbmcgui.DialogProgressBG()
            pDialogBD2.create('U2Pplay', 'Update en cours')
            try:
                shutil.rmtree(os.path.normpath(os.path.join(repStrm, "xml")), ignore_errors=True)
            except: pass
            try:
                shutil.rmtree(os.path.normpath(os.path.join(repStrm, "xsp")), ignore_errors=True)
            except: pass
            if os.path.isfile(os.path.normpath(os.path.join(repAddon, "version.txt"))):
                shutil.move(os.path.normpath(os.path.join(repAddon, "version.txt")), os.path.normpath(os.path.join(repStrm, "version.txt")))

            if os.path.isfile(os.path.normpath(os.path.join(repStrm, "version.txt"))):
                numVersion = int(open(os.path.normpath(os.path.join(repStrm, "version.txt")), 'r').readline())
            else:
                numVersion = 0
            
            with zipfile.ZipFile(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/MyVideos119-U2P.zip"), 'r') as zipObject:
                zipObject.extract("MyVideos119-U2P.db", repAddon)
                listOfFileNames = zipObject.namelist()
                nbFiles = len(listOfFileNames)
                try: 
                   zipObject.extract("u2pBD.bd", xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/'))
                   listeNews = extractNews(numVersion)
                   for i, f in enumerate(listOfFileNames):
                        nbGroupe = int((i / float(nbFiles)) * 100.0)
                        pDialogBD2.update(nbGroupe, 'U2Pplay', message="verif STRMS")
                        if (numVersion == 0 and f[-5:] == ".strm") or f in listeNews:
                            zipObject.extract(f, repStrm)
                        elif f[-4:] in [".xml", ".xsp"]: 
                                zipObject.extract(f, repAddon)
                        elif f in ["version.txt"]:
                            zipObject.extract(f, repStrm)
                        else:
                            if f in ["fileSources.txt", "sources.xml", "fichierDB.txt"] or f[-4:] in [".xml", ".xsp"]:
                                zipObject.extract(f, repAddon)
                except:
                    try:
                        zipObject.extract("medias.bd", repAddon)
                    except: pass
                    for i, f in enumerate(listOfFileNames):
                        nbGroupe = int((i / float(nbFiles)) * 100.0)
                        pDialogBD2.update(nbGroupe, 'U2Pplay', message="verif STRMS")
                        if f in ["fileSources.txt", "sources.xml", "fichierDB.txt"] or f[-4:] in [".xml", ".xsp"]:
                            zipObject.extract(f, repAddon)
                   
               
            pDialogBD2.close()
            showInfoNotification("Mise en place new database !!!")
            notice("extraction %0.2f" %(time.time() - a))
            a = time.time()
            try:
                shutil.move(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/sources.xml"), xbmcvfs.translatePath("special://home/userdata/sources.xml"))
            except: pass
            majLink(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/MyVideos119-U2P.db"))
            xbmcvfs.delete(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/MyVideos119-U2P.zip"))
            shutil.move(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/MyVideos119-U2P.db"), __database__)
            #xbmcvfs.delete(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/MyVideos119-U2P.db"))
            try:
                showInfoNotification("Update terminée (%d News)" %len(listeNews))
            except:
                showInfoNotification("Update terminée database-autonome (test)")
            notice("maj DATABASE %0.2f" %(time.time() - a))
            a = time.time()
        
        else:
            if debug:
                showInfoNotification("Pas d'update")
        if debug:
            showInfoNotification("Durée Update : %d s" %(time.time() - tps))
            gestionThumbnails()

        createFav()
        time.sleep(0.5)
        xbmc.executebuiltin('ReloadSkin')
        return
        

def choixRepo():
    repReposFilm = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/xml/movie/") 
    repCatFilm = xbmcvfs.translatePath("special://home/userdata/library/video/movies/")
    filesRepo = os.listdir(repReposFilm)
    try:
        filesCat = os.listdir(repCatFilm)
    except:
        showInfoNotification("Installer Library Node Editor")
        return
    dialog = xbmcgui.Dialog()
    repos = dialog.multiselect("Selectionner les repos à installer", [x[:-4].replace("_", " ") for x in filesRepo], preselect=[])
    if repos:
        [xbmcvfs.delete(repCatFilm + x) for x in filesRepo if x in filesCat]
        for repo in repos:
            shutil.copy(repReposFilm + filesRepo[repo], repCatFilm + filesRepo[repo]) 
    xbmc.sleep(500)
    xbmc.executebuiltin('ReloadSkin')

def choixliste():
    repListes = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/xsp/") 
    dictRep = {"Listes intélligentes made in %s" %x: [x] for x in os.listdir(repListes)}
    
    #dictApi = {"Uptobox": ["keyupto", "Key Api Uptobox"], "Alldebrid": ["keyalldebrid", "Key Api Alldebrid"], "RealDebrid": ["keyrealdebrid", "Key Api RealDebrid"]}
    dialogApi = xbmcgui.Dialog()
    choixRep = list(dictRep.keys())
    selectedApi = dialogApi.select("Choix Contrib", choixRep)
    
    if selectedApi != -1:
        contrib = dictRep[choixRep[selectedApi]][0]
        repReposFilm = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/xsp/%s/" %contrib)  
        repCatFilm = xbmcvfs.translatePath("special://home/userdata/playlists/video/")
        filesRepo = os.listdir(repReposFilm)
        filesCat = os.listdir(repCatFilm)
        dialog = xbmcgui.Dialog()
        repos = dialog.multiselect("Selectionner les listes à installer", ["Toutes les listes"] + [x[:-4].replace("_", " ") for x in filesRepo], preselect=[])
        if repos:
            [xbmcvfs.delete(repCatFilm + x) for x in filesRepo if x in filesCat]
            if 0 in repos:
                repos = range(len(filesRepo) - 1)
            for repo in repos:
                shutil.copy(repReposFilm + filesRepo[repo], repCatFilm + filesRepo[repo]) 
        xbmc.sleep(500)
        xbmc.executebuiltin('ReloadSkin')

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'play':
            playMedia(params)
        elif params['action'] == 'playHK':
            playMediaHK(params)
        elif params['action'] == 'os':
            selectOS()
        elif params['action'] == 'apiConf':
            configKeysApi()
        elif params['action'] == 'strms':
            makeStrms()
        elif params['action'] == 'clearStrms':
            makeStrms(1)
        elif params['action'] == 'ePaste':
            editPaste()
        elif params['action'] == 'thmn':
            editNbThumbnails()
        elif params['action'] == 'groupe':
            creaGroupe()
        elif params['action'] == 'resos':
            editResos()
        elif params['action'] == 'bd':
            importDatabase()
        elif params['action'] == 'bdauto':
            importDatabase(typImport="autonome")
        elif params['action'] == 'maj':
            majDatabase()
        elif params['action'] == 'choixrepo':
            choixRepo()
        elif params['action'] == 'choixliste':
            choixliste()
        elif params['action'] == 'MenuFilm':
            mediasHK()
        elif params['action'] == 'MenuDivers':
            diversHK()
        elif params['action'] == 'MenuSerie':
            seriesHK()
        elif params['action'] == 'detailM':
            detailsMedia(params)
        elif params['action'] == 'detailT':
            detailsTV(params)
        elif params['action'] == 'movies':
            #affMovies()
            #list_videos()
            #mediasHK()
            ventilationHK()
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        menuPbi()
        #affMovies()
        #list_videos()

if __name__ == '__main__':
    nameExploit = sys.platform

    notice(nameExploit)
    # Get the plugin url in plugin:// notation.
    __url__ = sys.argv[0]
    # Get the plugin handle as an integer number.
    __handle__ = int(sys.argv[1])
    #  database video kodi
    if pyVersion == 2:
        bdKodi = "MyVideos116.db"
    else:
        bdKodi = "MyVideos119.db"
    try:
        __database__ = xbmc.translatePath("special://home/userdata/Database/%s" %bdKodi)
    except:
        __database__ = xbmcvfs.translatePath("special://home/userdata/Database/%s" %bdKodi)
    #Deprecated xbmc.translatePath. Moved to xbmcvfs.translatePath
    __repAddon__ = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/")
    __repAddonData__ = xbmcvfs.translatePath("special://home/userdata/addon_data/plugin.video.sendtokodiU2P")
    __keyTMDB__ = "96139384ce46fd4ffac13e1ad770db7a"
    notice(__database__)
    notice(sys.argv)
    __params__ = dict(parse_qsl(sys.argv[2][1:]))
    mepAutoStart()
    createFav()
    #notice(sys.version_info)
    #notice(__url__)
    #notice(__handle__)
    #smb://<nvidiashieldurl>/internal/Android/data/org.xbmc.kodi/files/.kodi/userdata 
    router(sys.argv[2][1:])

