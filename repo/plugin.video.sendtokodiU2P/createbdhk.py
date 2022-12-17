#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import sys
import requests
import io
import unicodedata
import re
import ast
import sqlite3
import shutil
import time
from urllib.parse import unquote, urlencode
try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser
import widget
pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor
if pyVersionM == 11:
    import cryptPaste11 as cryptage
    import scraperUPTO11 as scraperUPTO
elif pyVersionM == 8:
    import cryptPaste8 as cryptage
    import scraperUPTO8 as scraperUPTO
elif pyVersionM == 9:
    import cryptPaste9 as cryptage
    import scraperUPTO9 as scraperUPTO
else:
    import cryptPaste10 as cryptage
    import scraperUPTO10 as scraperUPTO

from datetime import datetime, timedelta
import threading
from urllib.parse import quote, unquote
from medias import Media, TMDB
from apiTraktHK import TraktHK
try:
    from util import *
    import xbmc
    import xbmcvfs
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
    ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    KEYTMDB = ADDON.getSetting("apikey")
    LIMIT = ADDON.getSetting("nb_items")
    LIMITSCRAP = ADDON.getSetting("nbupto")
    HANDLE = int(sys.argv[1])
    BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasHK.bd')
    BDREPO = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mymedia.db')
    BDREPONEW = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasNew.bd')
    BDHK = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/medias.bd')
    CHEMINPASTES = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/pastes/')
    CHEMIN = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P')
    DIFFUSEURS = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/tvshowNetwork.json')
except: pass
import uptobox
from medias import Media, TMDB

class BdHK:

    def __init__(self, database):
      self.database = database
      cnx = sqlite3.connect(self.database)
      cur = cnx.cursor()
      #(numId, title, year, genres, saga)
      cur.execute("""CREATE TABLE IF NOT EXISTS movie(
            id INTEGER PRIMARY KEY,
            numId INTEGER,
            title TEXT,
            year INTEGER,
            genre TEXT,
            saga TEXT,
            UNIQUE (numId))
              """)
      cur.execute("""CREATE TABLE IF NOT EXISTS movieLink(
            numId INTEGER,
            link TEXT,
            UNIQUE (link))
              """)
      cur.execute("""CREATE TABLE IF NOT EXISTS movieGroupes(
            id INTEGER PRIMARY KEY,
            numId INTEGER,
            groupe TEXT,
            typ INTEGER,
            UNIQUE (numId, groupe, typ))
              """)
      cur.execute("""CREATE TABLE IF NOT EXISTS tvshow(
            id INTEGER PRIMARY KEY,
            numId INTEGER,
            title TEXT,
            year INTEGER,
            genre TEXT,
            saga TEXT,
            repo TEXT,
            UNIQUE (numId))
              """)
      cur.execute("""CREATE TABLE IF NOT EXISTS tvshowEpisodes(
            numId INTEGER,
            saison TEXT,
            episode TEXT,
            link TEXT,
            UNIQUE (link))
              """)
      cur.execute("""CREATE TABLE IF NOT EXISTS tvshowsGroupes(
            id INTEGER PRIMARY KEY,
            numId INTEGER,
            groupe TEXT,
            typ INTEGER,
            UNIQUE (numId, groupe, typ))
              """)
      cur.execute("""CREATE TABLE IF NOT EXISTS repos(
            nom TEXT,
            typ TEXT,
            paste TEXT,
            UNIQUE (nom, paste))
              """)
      cnx.commit()
      cur.close()
      cnx.close()

    def getRepos(self):
      cnx = sqlite3.connect(self.database)
      cur = cnx.cursor()
      sql = "SELECT nom, typ FROM repos GROUP BY nom, typ"
      cur.execute(sql)
      liste = cur.fetchall()
      cur.close()
      cnx.close()
      return liste

    def executeSQL(self, sql, unique=0):
      cnx = sqlite3.connect(self.database)
      cur = cnx.cursor()
      cur.execute(sql)
      liste = cur.fetchall()
      cur.close()
      cnx.close()
      if unique:
        liste = [x[0] for x in liste]
      return liste


class ExtractPaste:
    def __init__(self, kwargs):
        for attr_name, attr_value in kwargs.items():
            setattr(self, attr_name, attr_value)
        self.cr = cryptage.Crypt()
        try:
            os.mkdir(self.chemin)
        except: pass
        self.getGenresFilm()
        self.getGenresSerie()

    def getPaste(self, num):
        """import liste media via un paste """
        self.numPaste = num

        lignes = self.cr.loadFile(self.numPaste)
        lignesSauve = lignes
        if not lignes or self.maj:
            self.gestionMedia = False
            if os.path.isfile(self.numPaste + ".txt"):
                notice("recup num paste => %s" %self.numPaste)
                with io.open(os.path.join(self.chemin, self.numPaste + ".txt"), "r", encoding="utf-8") as f:
                    lignesOld = ast.literal_eval(f.read())
            else:
              lignesOld = []
            if not lignes:
                lignes = lignesOld
            lignesSauve = lignes
            pos = 1
            if self.maj:
              lignes = [ligne for ligne in lignes[:] if ligne not in lignesOld]
            tabLignes = [l.split(";") for l in lignes[:]]
        else:
            tabLignes = [l.split(";") for l in lignes[1:]]
        #notice("nb lignes media", len(tabLignes), self.numPaste)
        with io.open(os.path.join(self.chemin, self.numPaste + ".txt"), "w", encoding="utf-8") as f:
            f.write(str(lignesSauve))
        self.tabMedias = []
        for ligne in tabLignes:
          #print(ligne)
          if ligne[0] == "film":
            self.tabMedias.append(self.makeFilm(ligne[1], ligne[2], ligne[8], ligne[9], ligne[11], ligne[10], ligne[3]))
          elif ligne[0] in ["serie", "anime"]:
            self.tabMedias.append(self.makeSerie(ligne[1], ligne[2], ligne[8], ligne[9], ligne[11], ligne[10], ligne[3]))

        #notice(len(self.tabMedias))
        return self.tabMedias

    def makeFilm(self, numId, title, year, tabGenres, tabLiens, tabResos, saga):
        #'CAT;TMDB;TITLE;SAISON;GROUPES;CAST;DIRECTOR;NETWORK;YEAR;GENRES;RES;URLS=ht tps:// uptobox.com/'
        tabLiens = ast.literal_eval(tabLiens)
        tabResos = ast.literal_eval(tabResos)
        genres = ",".join([self.dictGenreFilm[x] for x in ast.literal_eval(tabGenres) if x])
        fiche = (numId, title, year, genres, saga.split(":")[0])
        tabFinalLiens = [(numId, "%s@%s#%s" %(self.numPaste, x, tabResos[i])) for i, x in enumerate(tabLiens)]
        return ("film", fiche, tabFinalLiens)

    def makeSerie(self, numId, title, year, tabGenres, dictLiens, tabResos, saison):
        dictLiens = ast.literal_eval(dictLiens)
        tabResos = ast.literal_eval(tabResos)
        reso = ""
        if tabResos:
          reso = tabResos[0]
        genres = ",".join([self.dictGenreSerie[x] for x in ast.literal_eval(tabGenres) if x])
        fiche = (numId, title, year, genres, "")
        tabFinalLiens = [(numId, saison, k, "%s@%s#%s" %(self.numPaste, v, reso)) for k, v in dictLiens.items()]
        return ("serie", fiche, tabFinalLiens)

    def getGenresFilm(self):
        url1 = "https://api.themoviedb.org/3/genre/movie/list?api_key=%s&language=fr" %self.key
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()
        self.dictGenreFilm = {x["id"]: x["name"] for x in dictInfos["genres"]}

    def getGenresSerie(self):
        url1 = "https://api.themoviedb.org/3/genre/tv/list?api_key=%s&language=fr" %self.key
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()
        self.dictGenreSerie = {x["id"]: x["name"] for x in dictInfos["genres"]}
        self.dictGenreSerie.update(self.dictGenreFilm)

    def filmNumIdLight(self, numId):
        """infos films suivant numID"""
        url1 = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=fr&append_to_response=images".format(numId, self.key)
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()
        try:
          saga = dictInfos.get("belongs_to_collection", {}).get("id", 0)
        except:
          saga = 0
        title = dictInfos.get("title", "")
        poster = dictInfos.get("poster_path", "")
        backdrop = dictInfos.get("backdrop_path", "")
        try:
            genres = ", ".join([z for y in dictInfos["genres"] for x, z in y.items() if x =="name"])
        except:
            genres = ""
        year = dictInfos.get("release_date", '2010')[:4]
        overview = dictInfos.get("overview", "sans synopsis.....")
        popu = dictInfos.get("vote_average", 0.0)
        lang = dictInfos.get("original_language", "")
        votes = dictInfos.get("vote_count", 0)
        dateRelease = dictInfos.get("release_date", "2010-06-10")
        runTime = dictInfos.get("runtime", 0)
        try:
            logo = dictInfos["images"]["logos"][0]["file_path"]
        except:
            logo = ""
        return numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga

    def serieNumIdLight(self, numId):
        """infos series suivant numID"""
        url1 = "https://api.themoviedb.org/3/tv/{}?api_key={}&language=fr&append_to_response=images".format(numId, self.key)
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()

        title = dictInfos.get("title", "")
        poster = dictInfos.get("poster_path", "")
        backdrop = dictInfos.get("backdrop_path", "")
        try:
            genres = ", ".join([z for y in dictInfos["genres"] for x, z in y.items() if x =="name"])
        except:
            genres = ""
        year = dictInfos.get("first_air_date", '2010')[:4]
        overview = dictInfos.get("overview", "sans synopsis.....")
        popu = dictInfos.get("vote_average", 0.0)
        lang = dictInfos.get("original_language", "")
        votes = dictInfos.get("vote_count", 0)
        dateRelease = dictInfos.get("first_air_date", "2010-06-10")
        runTime = dictInfos.get("episode_run_time", [0])[0]
        try:
            logo = dictInfos["images"]["logos"][0]["file_path"]
        except:
            logo = ""
        return numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, ""

class LoadPastes:
    def __init__(self):
        self.tabMediasTotal = []

    def idPaste(self, lePaste):
        """extraction id paste d'un anopad"""
        html_parser = HTMLParser()
        motifAnotepad = r'.*<\s*div\s*class\s*=\s*"\s*plaintext\s*"\s*>(?P<txAnote>.+?)</div>.*'
        try:
            rec = requests.get("https://anotepad.com/note/read/" + lePaste, timeout=5)
            letx = rec.text
        except Exception as e:
            letx = ""
            notice(e)
        r = re.match(motifAnotepad, letx, re.MULTILINE|re.DOTALL|re.IGNORECASE)
        lignes = []
        try:
            tx = r.group("txAnote")
            tx = html_parser.unescape(tx)

            lignes = [x.split("=") for x in tx.splitlines() if x and x[0] != "#"]
        except Exception as e:
            notice("erreur id pastes", e)
        return lignes

    def gestion(self, paste, maj, repo, chemin):
        ep = ExtractPaste({"chemin": chemin, "key": KEYTMDB, "maj": maj, "repo": repo})
        self.tabMediasTotal += ep.getPaste(paste)

    def testThread(self):
        a = 0
        tActif = True
        while tActif:
            tActif = False
            for t in threading.enumerate():
                if "bdhk" == t.getName():
                    tActif = True
            time.sleep(0.1)
            a += 1
            if a > 15000:
                break
        return True
#================================================================================================= fonctions ==============================================================================
def affbaext():
    choix  = []
    if os.path.isfile(os.path.join(CHEMIN, "ba.db")):
        bdba = os.path.join(CHEMIN, "ba.db")
        cnx = sqlite3.connect(bdba)
        cur = cnx.cursor()
        sql = 'SELECT DISTINCT repo from images'
        cur.execute(sql)
        liste = [x[0] for x in cur.fetchall()]
        cur.close()
        cnx.close()
        choix += [(x, {"action": "affbacat", "cat": x, "offset": 0}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(liste)]
        choix.append(("The Movie DB UpComing", {"action": "affbacattmdb", "cat": "upcoming", "limit": LIMITSCRAP, "offset": 0}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "bandes Annonce The Movie DB"))
    choix.append(("Import ou Update", {"action": "updateba"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Import ou update DB bandes Annonce"))
    addCategorieMedia(choix)

def affbacattmdb(params):
    offset = params["offset"]
    cat = params["cat"]
    limit = int(params["limit"])
    bdba = os.path.join(CHEMIN, "ba.db")
    cnx = sqlite3.connect(bdba)
    cur = cnx.cursor()
    if cat == "upcoming":
        sql = 'SELECT numId, link from filmBa ORDER BY id DESC LIMIT ? OFFSET ?'
    cur.execute(sql, (limit, offset,))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    medias = uptobox.getFilmsUptoNews(liste)
    cr = cryptage.Crypt()
    fI = cr.fileInfo([x[1] for x in liste])
    xbmcplugin.setPluginCategory(HANDLE, "Bandes Annonce")
    xbmcplugin.setContent(HANDLE, "movies")
    i = 0
    for i, media in enumerate(medias):
        notice(media)
        try:
            media = Media("movie", *media[1:-1])
        except:
            media = Media("movie", *media[1:])
        try:
            media.overview = "------------------------------------\nType BA: %s\n------------------------------------\n" %fI[i]['file_name'][:-4].replace(".", " ") \
                    + media.overview
        except: pass
        ok = addDirectoryMedia("%s" %(media.title), isFolder=False, parameters={"action": "playMediabaext", "lien": media.link}, media=media)
    if i >= limit - 1:
        addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)


def affbacat(params):
    offset = params["offset"]
    limit = int(LIMIT)
    bdba = os.path.join(CHEMIN, "ba.db")
    cnx = sqlite3.connect(bdba)
    cur = cnx.cursor()
    cur.execute('SELECT nom, link, linkUpto from images WHERE repo=? ORDER BY id DESC LIMIT ? OFFSET ?', (params["cat"], limit, offset))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    xbmcplugin.setPluginCategory(HANDLE, "Bandes Annonce")
    xbmcplugin.setContent(HANDLE, "episodes")
    i = 0
    for i, ba in enumerate(liste):
        li = xbmcgui.ListItem(label=ba[0])
        li.setInfo('video', {"title": ba[0], 'plot': ba[0], 'mediatype': 'video'})
        li.setArt({"fanart": ba[1], "thumb": ba[1]})
        li.setProperty('IsPlayable', 'true')
        parameters={"action": "playMediabaext", "lien": ba[2]}
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)
    if i >= int(LIMIT) - 1:
        addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)


def addCategorieMedia(choix):
    dictChoix = {"Derniers Ajouts": "Liste des derniers, tous types, entrés dans pastebin (nouveauté ou pas, et update)", "Derniers Ajouts Films": "Liste ,uniquement ,films des derniers entrés dans pastebin (nouveauté ou pas, et update)",\
     "Mon historique": "La liste de médias commencés ou la reprise est possible", "Liste Aléatoire": "Liste de médias sortis au hazard, quand tu ne sais pas quoi regarder",\
         "Recherche": "ben recherche ..... (astuce le _ remplace n'importe quel caractére ex search => r_m donnera tous les titres qui contiennent ram, rom , rum etc... Interressant pour la recherche simultanées de 'e é è ê'",\
          "Groupes Contrib": "Les groupes classés des conributeurs", "Les plus populaires TMDB/trakt": "Les mieux notés ou populaires chez movieDB et trakt",\
          "Année(s)": "Recherche par années ex 2010 ou groupe d'années 2010:2013 => tous les medias 2010 2011 2012 2013", "Genre(s)": "vos genres préféres avec le multi choix ex choix sience-fiction et fantatisque => la liste gardera les 2 genres", \
          "Alpha(s)": "liste suivant dont le titre commence pas la lettre choisie ou le debut du mot ex ram donnera tous les titres commencant par ram (astuce le _ remplace n'importe quel caractére",
          "Filtres": "les filtres search, Alphanumérique, genres, Années etc.... Cela est fait sur ensemble des médias",
          "Nouveautés par année": "Classement medias par ordre d'année ensuite par date entrée dans pastebin (Documentaires, concerts, spectacles, animations exclues)",
          "Les mieux notés": "Classement notation descroissant > 7 et < 9", "Mes favoris HK": "liste de vos favoris"}

    content = ""
    try:
        if "network" in choix[0][1].keys():
            nomF = "Diffuseurs"
            #content = "files"
        else:
            nomF = "Choix Gatégories"
    except:
        nomF =  "Choix Gatégories"

    xbmcplugin.setPluginCategory(HANDLE, nomF)
    if content:
        xbmcplugin.setContent(HANDLE, content)
    isFolder = True

    for ch in choix:
        name, parameters, picture, texte = ch
        if texte in dictChoix.keys():
            texte = dictChoix[texte]
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte, 'mediatype': 'video'})
        #vinfo = li.getVideoInfoTag()
        #vinfo.setPlot(texte)
        if "http" not in picture and not os.path.isfile(xbmcvfs.translatePath(picture)):
            picture = 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png'
        li.setArt({'thumb': picture,
                  'fanart': ADDON.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def mediasHKFilms(params):
    notice("params: " + str(params))
    typM = "movie"
    try:
        offset = int(params["offset"])
    except:
        offset = 0
    try:
        limit = int(params["limit"])
    except:
        limit = int(LIMIT)
    orderDefault = getOrderDefault()

    year = datetime.today().year
    lastYear = year - 1

    if "famille" in params.keys():
        famille = params["famille"]
        movies = None
        #===============================================================================================================================================================================================
        if famille in ["groupes"]:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM filmsPub as m WHERE m.numId IN (SELECT f.numId FROM filmsRepos as f WHERE f.nom='{}')".format(params["nom"])\
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================================
        elif famille in ["sagaListe"]:
            numsaga = params["numIdSaga"]
            mDB = TMDB(KEYTMDB)
            tabId = mDB.getSaga(numsaga)
            if tabId:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                            FROM filmsPub as m WHERE m.numId IN ({}) ORDER BY m.year".format(",".join([str(x[1]) for x in sorted(tabId)]))
                movies = extractMedias(sql=sql)
            else:
                return
        #====================================================================================================================================================================================
        elif famille == "cast":
            mdb = TMDB(KEYTMDB)
            liste = mdb.person(params["u2p"])
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille in ["nouveau"]:
            sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='docu'"
            liste = extractMedias(sql=sql, unique=1)
            sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='concert'"
            liste += extractMedias(sql=sql, unique=1)
            sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='spectacle'"
            liste += extractMedias(sql=sql, unique=1)
            sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='sport'"
            liste += extractMedias(sql=sql, unique=1)
            sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='quebec'"
            liste += extractMedias(sql=sql, unique=1)
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM filmsPub as m WHERE m.numId NOT IN ({})  AND m.year!=''  AND m.year>={} AND genres NOT LIKE '%%Documentaire%%' AND genres NOT LIKE '%%Animation%%' ORDER BY ".\
                        format(",".join([str(x) for x in list(set(liste))]), lastYear) + " id DESC"\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #================================================================================================================================================================================================
        elif famille in ["specialWid"]:
            if "nomListe" in params.keys():
                nomListe = params["nomListe"]
                mdb = TMDB(KEYTMDB)
                liste = mdb.getListeFilm(nomListe)
                tabMovies = []
                for n in liste:
                    if n:
                        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                            FROM filmsPub as m  WHERE m.numId={}".format(n)
                        movies = extractMedias(sql=sql)
                        if movies:
                            tabMovies.append(movies[0])
                #params["suite"] = 1
                movies = tabMovies[:]

                #sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                #    FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
                #movies = extractMedias(sql=sql)
            else:
                wids = ['Tendances du jour', 'Tendances de la semaine', 'Nouveautés', 'Les plus populaires', 'Films français récents', 'Films français populaires', "Films d'animation récents",\
                        "Films d'animation populaires", 'Films famille récents', 'Films famille populaires', 'Animes populaires', 'Animes récents']
                choix = [(x, {"action": "mediasHKFilms", "famille": "specialWid", "nomListe": x, "typM": "movie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/film.png', x) for x in sorted(wids)]
                addCategorieMedia(choix)
        #================================================================================================================================================================================================
        elif famille in ["genres"]:
            genre = params["typgenre"]
            dictCat = {"Documentaire": "docu", "Spectacles": "spectacle", "Sports": "sport", "Concerts": "concert", "QC": "quebec"}
            if genre in ["Spectacles", "Sports", "Concerts", "QC"]:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM filmsPub as m WHERE m.numId IN (SELECT f.numId FROM filmsRepos as f WHERE f.famille='{}')".format(dictCat[genre])\
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            elif genre == "Anime-Jap":
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                            FROM filmsPub as m WHERE m.genres LIKE '%%Animation%%' AND m.lang='ja' ORDER BY m.id DESC" + " LIMIT {} OFFSET {}".format( limit, offset)
            elif genre in ["Documentaire"]:
                sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='{}'".format(dictCat[genre])
                liste = extractMedias(sql=sql, unique=1)
                sql = "SELECT m.numID FROM filmsPub as m WHERE m.genres LIKE '%%{}%%' ORDER BY m.id DESC".format(genre)
                liste += extractMedias(sql=sql, unique=1)
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in list(set(liste))]))\
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                            FROM filmsPub as m WHERE m.genres LIKE '%%{}%%' ORDER BY m.id DESC".format(genre) + " LIMIT {} OFFSET {}".format( limit, offset)

            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #================================================================================================================================================================================================
        elif famille in ["Search", "Recherche"]:
            if "nom" not in params.keys():
                dialog = xbmcgui.Dialog()
                d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
            else:
                d = params["nom"]
            if len(d) > 2:
                movies = []
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                            FROM filmsPub as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                movies += extractMedias(sql=sql)
                if os.path.isfile(BDHK):
                    try:
                        sql = "SELECT m.title||' (HK)', m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                                FROM movie as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                        movies += extractMedias(bd=BDHK, sql=sql)
                    except: pass
        #====================================================================================================================================================================================
        elif famille == "Listes Trakt":
            listeRep = list(widget.getListesT("movie"))
            listeRep = list(set([x[3] for x in listeRep]))
            choix = [(x, {"action": "mediasHKFilms", "listeT": x, "typM": "movie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif famille == "Listes lecture":
            listeRep = list(widget.getListesV("movie"))
            choix = [(x, {"action":"mediasHKFilms", "listeV": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif famille == "Liste Aléatoire":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id\
            FROM filmsPub as m ORDER BY RANDOM() LIMIT {}".format(LIMIT)
            movies = extractMedias(sql=sql)

        #====================================================================================================================================================================================
        elif params["famille"] == "cast":
            mdb = TMDB(__keyTMDB__)
            liste = mdb.person(params["u2p"])
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id\
                FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille == "Année(s)":
            if "an" in params.keys():
                an = [int(x) for x in params["an"].split(":")]
            else:
                dialog = xbmcgui.Dialog()
                d = dialog.input("Entrer Année => 2010 / Groupe d'années => 2010:2014", type=xbmcgui.INPUT_ALPHANUM)
                if d:
                    an = d.split(":")
            params["an"] = ":".join([str(x) for x in an])
            if len(an) == 1:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM filmsPub as m WHERE m.year={}".format(int(an[0])) + " ORDER BY m.year DESC, m.Title ASC" + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM filmsPub as m WHERE m.year>={} and m.year<={}".format(an[0], an[1]) + " ORDER BY m.year DESC, m.Title ASC" + " LIMIT {} OFFSET {}".format(limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille in ["Last View", "Mon historique"]:
            if ADDON.getSetting("bookonline") != "false":
                liste = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=movie" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
            else:
                liste = widget.bdHK(extract=1)
            tabMovies = []
            for n in liste:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id\
                      FROM filmsPub as m WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
            movies = tabMovies[:]
        #====================================================================================================================================================================================
        elif famille == "Mes Widgets":
            listeRep = list(widget.extractListe())
            choix = [(x, {"action":"mediasHKFilms", "widget": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #===============================================================================================================================================================================
        elif famille in ["Fav'S HK", "Mes favoris HK"]:
            if ADDON.getSetting("bookonline") != "false":
                liste = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=movies" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
            else:
                liste = widget.extractFavs("movies")
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM filmsPub as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            params["favs"] = ADDON.getSetting("bookonline_name")
            movies = extractMedias(sql=sql)

        #================================================================================================================================================================================================
        else:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM filmsPub as m WHERE m.numId IN (SELECT f.numId FROM filmsRepos as f WHERE f.famille='{}')".format(famille)\
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(bd=BDREPONEW,sql=sql)
        #affichage
        if movies:
            affMedias(typM, movies, params=params)

    elif "groupes" in params.keys():
        sql = "SELECT DISTINCT nom FROM filmsRepos WHERE nom!='concert' AND nom!='sport' AND nom!='docu' AND nom!='film' AND nom!='spectacle'"
        sql = "SELECT DISTINCT nom FROM filmsRepos"
        liste = extractMedias(sql=sql, unique=1)
        choix = [(x.capitalize(), {"action":"mediasHKFilms", "famille":"groupes", "offset": "0", "nom":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in liste]
        addCategorieMedia(choix)

    elif "listeT" in params.keys():
        if "listeTfille" in params.keys():
            liste = list(widget.getListesT("movie"))
            liste = [(x[0], x[1], "movie") for x in liste if x[3] == params["listeT"] and x[4] == params["listeTfille"]][0]
            trk = TraktHK()
            tabNumId = trk.extractList(*liste)
            tabNumId = [x for x in tabNumId if x]
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))
            movies = extractMedias(sql=sql)
            affMedias(typM, movies, params={})
        else:
            listeRep = list(widget.getListesT("movie"))
            listeRep = list(set([x[4] for x in listeRep if x[3] == params["listeT"]]))
            choix = [(x, {"action": "mediasHKFilms", "listeT": params["listeT"], "listeTfille": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)

    #===============================================================================================================================================================================
    elif "widget" in params.keys():

        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='docu'"
        liste = extractMedias(sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='concert'"
        liste += extractMedias(sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='spectacle'"
        liste += extractMedias(sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='sport'"
        liste += extractMedias(sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='quebec'"
        liste += extractMedias(sql=sql, unique=1)

        sql = widget.getListe(params["widget"], "film")

        sql = sql.replace("SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id                         FROM movie as m", \
            "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id FROM filmsPub as m")

        sql = sql.replace("m.numId NOT IN (SELECT sp.numId FROM movieFamille as sp WHERE sp.famille == '#Spectacles') AND genre NOT LIKE '%%Documentaire%%' AND genre NOT LIKE '%%Animation%%' AND genre != 'Musique' AND ",\
            "m.numId NOT IN ({}) AND genres NOT LIKE '%%Documentaire%%' AND genres NOT LIKE '%%Animation%%' AND ".format(",".join([str(x) for x in list(set(liste))])))
        sql = sql.replace("genre ", "genres ")

        movies = extractMedias(sql=sql)
        affMedias(typM, movies, params={})

    #===============================================================================================================================================================================
    elif "listeV" in params.keys():
        tabNumId = widget.getListesVdetail(params["listeV"], "movie")
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id\
             FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
        params["offset"] = offset
        movies = extractMedias(sql=sql)
        affMedias(typM, movies, params)

    else:
        choix = [("Nouveautés %d-%d" %(lastYear, year), {"action":"mediasHKFilms", "famille": "nouveau"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Nouveautés %d-%d" %(lastYear, year))]
        sql = "SELECT DISTINCT famille FROM filmsRepos"
        liste = extractMedias(sql=sql, unique=1)
        choix += [(x.capitalize(), {"action":"mediasHKFilms", "famille":x, "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in liste]
        choix += [("Liste Aléatoire", {"action":"mediasHKFilms", "famille": "Liste Aléatoire"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Liste Aléatoire.png', "Liste Aléatoire")]
        choix += [("Listes Trakt", {"action":"mediasHKFilms", "famille": "Listes Trakt"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/trakt.png', "Liste trakt de users")]
        choix += [("Listes Spécial Widget", {"action":"mediasHKFilms", "famille": "specialWid"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/films.png', "Liste Spécial Widget")]
        choix += [("Mes Widgets", {"action":"mediasHKFilms", "famille": "Mes Widgets"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Listes Widgets perso")]
        choix += [("Listes Lecture", {"action":"mediasHKFilms", "famille": "Listes lecture"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Listes lecture ou favoris dédiés")]
        choix += [("Mes favoris HK", {"action":"mediasHKFilms", "famille": "Mes favoris HK", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Mes favoris HK")]
        choix += [("Mon historique", {"action":"mediasHKFilms", "famille": "Mon historique", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Mon historique.png', "Mon historique")]
        choix += [("Année(s)", {"action":"mediasHKFilms", "famille": "Année(s)", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "filtres par Année(s)")]
        choix += [("Recherche", {"action":"mediasHKFilms", "famille": "Recherche"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "Recherche")]
        choix += [("Groupes", {"action":"mediasHKFilms", "groupes": "groupe", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "groupes")]
        choix.append(("Genres", {"action":"genresHK", "typM": "movie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Genres"))
        addCategorieMedia(choix)

def rechercheFilm(params):
    nom = params["nom"].replace("recherche", "")
    mediasHKFilms({"famille": "Recherche", 'nom': nom})

def rechercheSerie(params):
    nom = params["nom"].replace("recherche", "")
    mediasHKSeries({"famille": "Recherche", 'nom': nom})

def mediasHKSeries(params):
    notice("params: " + str(params))
    typM = "tvshow"
    try:
        offset = int(params["offset"])
    except:
        offset = 0
    try:
        limit = int(params["limit"])
    except:
        limit = int(LIMIT)
    orderDefault = getOrderDefault()

    year = datetime.today().year
    lastYear = year - 1

    if "famille" in params.keys():
        famille = params["famille"]
        movies = None
        #===============================================================================================================================================================================================
        if famille in ["groupes"]:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m\
                WHERE m.numId IN (SELECT f.numId FROM seriesRepos as f WHERE f.nom='{}')".format(params["nom"])\
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille == "cast":
            mdb = TMDB(KEYTMDB)
            liste = mdb.person(params["u2p"], typM="tvshow")
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m\
                 WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif famille == "Liste Aléatoire":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m ORDER BY RANDOM() LIMIT 200 "
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille == "Listes lecture":
            listeRep = list(widget.getListesV("tvshow"))
            choix = [(x, {"action":"mediasHKSeries", "listeV": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #===============================================================================================================================================================================
        elif famille == "seriesall":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m"\
                + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif famille == "serieserie":
            sql = "SELECT f.numId FROM seriesRepos as f WHERE f.nom='docu' OR f.nom='anime' OR f.nom='manga' OR f.nom='quebec'"
            liste = extractMedias(sql=sql, unique=1)
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m"\
                + "  WHERE m.numId NOT IN ({}) AND m.genres NOT LIKE '%%Animation%%' AND m.genres NOT LIKE '%%Documentaire%%'".format(",".join([str(x) for x in list(set(liste))])) \
                + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille in ["Last View", "Mon historique"]:
            if "suite" in params.keys():
                try:
                    if ADDON.getSetting("bookonline") != "false":
                        listeVus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
                    else:
                        listeVus =  widget.getVu("tvshow")
                except:
                    listeVus = []
                listeOC = widget.extractOC()
                liste = list(set([x.split("-")[0] for x in listeVus if int(x.split("-")[0]) in listeOC]))

            else:
                if ADDON.getSetting("bookonline") != "false":
                    liste = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=tvshow" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
                else:
                    liste = widget.bdHK(extract=1, typM="tvshow")
            tabMovies = []
            for n in liste:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                      FROM seriesPub as m WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
            #params["suite"] = 1
            movies = tabMovies[:]
        #================================================================================================================================================================================================
        elif famille in ["specialWid"]:
            dictIm = {"Netflix": "netflix", "Prime Video": "primevideo", "Disney+": "disneyplus", "Apple TV+": "appletv", "HBO Max": "hbomax", "CANAL+": "canalplus", "SALTO": "salto", "ARTE": "arte"}

            if "nomListe" in params.keys():
                nomListe = params["nomListe"]
                mdb = TMDB(KEYTMDB)
                liste = mdb.getListeSerie(nomListe)
                tabMovies = []
                for n in liste:
                    if n:
                        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                          FROM seriesPub as m WHERE m.numId={}".format(n)
                        movies = extractMedias(sql=sql)
                        if movies:
                            tabMovies.append(movies[0])
                #params["suite"] = 1
                movies = tabMovies[:]

                #sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                #      FROM seriesPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in liste[::-1]]))
                #movies = extractMedias(sql=sql)
            elif "diffus" in params.keys():
                diffuseur = params["diffus"]
                wids = ["Populaires", "Nouveautés"]
                choix = [(x, {"action": "mediasHKSeries", "famille": "specialWid", "nomListe": '%s : %s' %(diffuseur, x), "typM": "tvshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.jpg'\
                        %dictIm[diffuseur], x) for x in sorted(wids)]
                addCategorieMedia(choix)
            else:
                wids = ['Tendances du jour', 'Tendances de la semaine', 'Nouveautés', 'Les plus populaires', "Séries d'animation récentes",\
                        "Séries d'animation populaires", 'Séries récentes', 'Séries populaires', 'Animes populaires', 'Animes récents']
                choix = [(x, {"action": "mediasHKSeries", "famille": "specialWid", "nomListe": x, "typM": "tvshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/serie.png', x) for x in sorted(wids)]
                diff  = ["Netflix", "Prime Video", "Disney+", "Apple TV+", "HBO Max", "CANAL+", "SALTO", "ARTE"]
                choix += [("# %s" %x, {"action": "mediasHKSeries", "famille": "specialWid", "diffus": x, "typM": "tvshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.jpg' %dictIm[x], x) for x in sorted(diff)]
                addCategorieMedia(choix)
        #================================================================================================================================================================================================
        elif famille in ["genres"]:
            genre = params["typgenre"]
            dictCat = {"Documentaire": "docu", "QC": "quebec"}
            if genre in ["QC"]:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id  \
                        FROM seriesPub as m WHERE m.numId IN (SELECT f.numId FROM filmsRepos as f WHERE f.nom='{}')".format(dictCat[genre])\
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            elif genre == "Anime-Jap":
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                            FROM seriesPub as m WHERE m.genres LIKE '%%Animation%%' AND m.lang='ja' ORDER BY m.id DESC" + " LIMIT {} OFFSET {}".format( limit, offset)
            elif genre in ["Documentaire"]:
                sql = "SELECT f.numId FROM seriesRepos as f WHERE f.nom='{}'".format(dictCat[genre])
                liste = extractMedias(sql=sql, unique=1)
                sql = "SELECT m.numID FROM seriesPub as m WHERE m.genres LIKE '%%{}%%' ORDER BY m.id DESC".format(genre)
                liste += extractMedias(sql=sql, unique=1)
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                        FROM seriesPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in list(set(liste))]))\
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                            FROM seriesPub as m WHERE m.genres LIKE '%%{}%%' ORDER BY m.id DESC".format(genre) + " LIMIT {} OFFSET {}".format( limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif famille in ["Fav'S HK", "Mes favoris HK"]:
            if ADDON.getSetting("bookonline") != "false":
                liste = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=tvshow" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
            else:
                liste = widget.extractFavs("tvshow")
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            params["favs"] = ADDON.getSetting("bookonline_name")
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille == "Listes Trakt":
            listeRep = list(widget.getListesT("show"))
            listeRep = list(set([x[3] for x in listeRep]))
            choix = [(x, {"action":"mediasHKSeries", "listeT": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif famille == "Année(s)":
            if "an" in params.keys():
                an = [int(x) for x in params["an"].split(":")]
            else:
                dialog = xbmcgui.Dialog()
                d = dialog.input("Entrer Année => 2010 / Groupe d'années => 2010:2014", type=xbmcgui.INPUT_ALPHANUM)
                if d:
                    an = d.split(":")
            params["an"] = ":".join([str(x) for x in an])
            if len(an) == 1:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m\
                  WHERE m.year={}".format(an[0]) + " ORDER BY m.year DESC, m.Title ASC" + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m\
                    WHERE m.year>={} and m.year<={}".format(an[0], an[1]) + " ORDER BY m.year DESC, m.Title ASC" + " LIMIT {} OFFSET {}".format(limit, offset)
            params["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif famille == "Mes Widgets":
            listeRep = list(widget.extractListe("serie"))
            choix = [(x, {"action":"mediasHKSeries", "widget": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #===============================================================================================================================================================================
        elif famille in ["Search", "Recherche"]:
            if "nom" not in params.keys():
                dialog = xbmcgui.Dialog()
                d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
            else:
                d = params["nom"]
            if len(d) > 2:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                                FROM seriesPub as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                movies = extractMedias(sql=sql)
                if os.path.isfile(BDHK):
                    try:
                        sql = "SELECT m.title ||' (HK)', m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                                FROM tvshow as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                        movies += extractMedias(bd=BDHK, sql=sql)
                    except: pass

        #affichage
        if movies:
            affMedias(typM, movies, params=params)

    elif "groupes" in params.keys():
        sql = "SELECT DISTINCT nom FROM seriesRepos"
        liste = extractMedias(sql=sql, unique=1)
        choix = [(x.capitalize(), {"action":"mediasHKSeries", "famille":"groupes", "offset": "0", "nom":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in liste]
        addCategorieMedia(choix)

    #===============================================================================================================================================================================
    elif "listeT" in params.keys():
        if "listeTfille" in params.keys():
            liste = list(widget.getListesT("show"))
            liste = [(x[0], x[1], "show") for x in liste if x[3] == params["listeT"] and x[4] == params["listeTfille"]][0]
            trk = TraktHK()
            tabNumId = trk.extractList(*liste)
            tabNumId = [x for x in tabNumId if x]
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                                FROM seriesPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))
            movies = extractMedias(sql=sql)
            affMedias(typM, movies, params={})
        else:
            listeRep = list(widget.getListesT("show"))
            listeRep = list(set([x[4] for x in listeRep if x[3] == params["listeT"]]))
            choix = [(x, {"action":"mediasHKSeries", "listeT": params["listeT"], "listeTfille": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)

    #===============================================================================================================================================================================
    elif "network" in params.keys():
        if "namenetwork" in params.keys():
            page = int(params["page"])
            numId = params["namenetwork"]
            mDB = TMDB(KEYTMDB)
            tabNumId = mDB.getIdDiffuseur(numId, page=page)
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
                                FROM seriesPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))
            movies = extractMedias(sql=sql)
            affMedias(typM, movies, params=params)
        else:
            f = io.open(DIFFUSEURS, encoding="utf-8")
            listeRepData = [(x["network"], x["poster"], x["numId"]) for x in json.load(f)]
            choix = [(x[0], {"action":"mediasHKSeries", "network":"1", "namenetwork": x[2], "page": "1"}, "http://image.tmdb.org/t/p/w500%s" %x[1], x[0]) for x in listeRepData]
            addCategorieMedia(choix)
    #===============================================================================================================================================================================
    elif "widget" in params.keys():
        sql = widget.getListe(params["widget"], "serie")
        notice(sql)
        sql = sql.replace("SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m", \
            "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m")
        sql = sql.replace("genre ", "genres ")
        notice(sql)
        movies = extractMedias(sql=sql)
        affMedias(typM, movies, params={})

    #===============================================================================================================================================================================
    elif "listeV" in params.keys():
        tabNumId = widget.getListesVdetail(params["listeV"], "tvshow")
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m\
             WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
        params["offset"] = offset
        movies = extractMedias(sql=sql)
        affMedias(typM, movies, params)

    else:
        if ADDON.getSetting("ochk1") != "false" and int(ADDON.getSetting("intmaj")):
            choix = [("On continue...", {"action":"suiteSerieHK2"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Mon historique.png', "on continue nos series")]
        else:
            choix = [("On continue...", {"action":"mediasHKSeries", "famille": "Mon historique", "offset": "0", "suite": "1"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Mon historique.png', "on continue nos series")]
        choix += [("Series", {"action":"mediasHKSeries", "famille": "serieserie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Serie.png', "Liste series hors animation et documentaire")]
        choix += [("Derniers Ajouts", {"action":"mediasHKSeries", "famille": "seriesall"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Serie.png', "Liste series tous genres")]
        choix += [("Liste Aléatoire", {"action":"mediasHKSeries", "famille": "Liste Aléatoire"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Liste Aléatoire.png', "Liste Aléatoire, tous genres")]
        choix += [("Listes Trakt", {"action":"mediasHKSeries", "famille": "Listes Trakt"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/trakt.png', "Liste trakt de users")]
        choix += [("Listes Spécial Widget", {"action":"mediasHKSeries", "famille": "specialWid"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Liste Spécial Widget")]
        choix += [("Mes Widgets", {"action":"mediasHKSeries", "famille": "Mes Widgets"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Listes Widgets perso")]
        choix += [("Listes Lecture", {"action":"mediasHKSeries", "famille": "Listes lecture"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Listes lecture ou favoris dédiés")]
        choix += [("Mes favoris HK", {"action":"mediasHKSeries", "famille": "Mes favoris HK"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Mes envies de voir")]
        choix += [("Mon historique", {"action":"mediasHKSeries", "famille": "Mon historique", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Mon historique.png', "Mon historique")]
        choix += [("Année(s)", {"action":"mediasHKSeries", "famille": "Année(s)", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "filtres par Année(s)")]
        choix += [("Recherche", {"action":"mediasHKSeries", "famille": "Recherche"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "Recherche")]
        choix += [("Groupes", {"action":"mediasHKSeries", "groupes": "groupe", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "groupes")]
        choix += [("Diffuseurs", {"action":"mediasHKSeries", "network":"1"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Diffuseur")]
        choix.append(("Genres", {"action":"genresHK", "typM": "tvshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Genres"))

        #sql = "SELECT DISTINCT nom FROM seriesRepos"
        #liste = extractMedias(sql=sql, unique=1)
        #choix += [(x.capitalize(), {"action":"mediasHKSeries", "famille":x, "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in liste]
        addCategorieMedia(choix)

def genresHK(params):
    typM = params["typM"]
    xbmcplugin.setPluginCategory(HANDLE, "Choix Genres")
    isFolder = True
    mdb = TMDB(KEYTMDB)
    if typM == "movie":
        tabGenre = mdb.getGenre()
        #sql = "SELECT nom FROM movieTypeFamille WHERE typFamille='genre'"
        #liste = extractMedias(sql=sql)
        #tabGenre += sorted([x[0] for x in liste])
        liste = ["Anime-Jap", "Spectacles", "Sports", "Concerts", "QC"]
        tabGenre += liste
        choix = [(x, {"action":"mediasHKFilms", "famille": "genres", "typgenre": x, "offset": 0, "limit": LIMIT}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/genre/%s.png' %x, x) for x in tabGenre]
    else:
        tabGenre = mdb.getGenre(typM="tv")
        liste = ["Anime-Jap", "QC"]
        tabGenre += liste
        choix = [(x, {"action":"mediasHKSeries", "famille": "genres", "typgenre": x, "offset": 0, "limit": LIMIT}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/genre/%s.png' %x, x) for x in tabGenre]

    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte, 'mediatype': 'video'})
        li.setArt({'thumb': picture,
                  'icon': ADDON.getAddonInfo('icon'),
                  'fanart': ADDON.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def suiteSerie(params):
    mdb = TMDB(KEYTMDB)
    numId = params["u2p"]
    try:
        if ADDON.getSetting("bookonline") != "false":
            listeVus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
        else:
            listeVus =  widget.getVu("tvshow")
    except:
        listeVus = []
    dictSerie = {}
    for vu in listeVus:
        vu = vu.split("-")
        episode = int(vu[1].zfill(2) + vu[2].zfill(4))
        if vu[0] in dictSerie.keys() and episode > dictSerie[vu[0]]:
                dictSerie[vu[0]] = episode
        else:
            dictSerie[vu[0]] = episode
    listeSerie  = []
    try:
        episodeVu = dictSerie[numId]
    except:
        episodeVu = 0
    episodes = uptobox.getEpisodesSuite(numId)
    saison = None
    tabEpisodeOk = []
    for (episode, lien, numEpisode) in sorted(episodes):
        if episode > episodeVu:
            if not saison:
                saison = int(episode / 10000)
            if episode not in tabEpisodeOk:
                tabEpisodeOk.append(episode)
                lien = "*".join(list(set([x[1] for x in sorted(episodes) if int(episode) == int(x[0])])))
                numEpisode = episode - (saison * 10000)
                serie = [numId, saison, numEpisode, lien]
                if saison != int(episode / 10000):
                    break
                else:
                    listeSerie.append(serie)

    xbmcplugin.setPluginCategory(HANDLE, "Episodes")
    xbmcplugin.setContent(HANDLE, 'episodes')
    tabEpisodes = mdb.saison(numId, saison)

    for i, (numId, saison, numEpisode, filecodes) in enumerate(listeSerie):
        l = [numId, saison, numEpisode, filecodes]
        try:
            lFinale = list(l) + list([episode for episode in tabEpisodes if int(numEpisode) == episode[-1]][0])
        except:
            lFinale = list(l) + ["Episode", "Pas de synopsis ....", "", "", "", saison, numEpisode]
        isVu = 0
        lFinale.append(isVu)
        media = Media("episode", *lFinale)
        media.typeMedia = "episode"
        media.numId = int(l[0])
        if i == 0:
            c = "yellow"
        else:
            c = "white"
        addDirectoryEpisodes("[COLOR=%s]S%sE%d[/COLOR] - %s" %(c, str(saison).zfill(2),  int(numEpisode), media.title), isFolder=False, \
            parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode, "saison": media.saison}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)


def suiteSerie2():
    try:
        if ADDON.getSetting("bookonline") != "false":
            listeVus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
        else:
            listeVus =  widget.getVu("tvshow")
    except:
        listeVus = []
    dictSerie = {}
    for vu in listeVus:
        vu = vu.split("-")
        episode = int(vu[1].zfill(2) + vu[2].zfill(4))
        if vu[0] in dictSerie.keys() and episode > dictSerie[vu[0]]:
                dictSerie[vu[0]] = episode
        else:
            dictSerie[vu[0]] = episode
    listeSerie  = []

    databaseTV = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/tvshow.bd')
    cnxTV = sqlite3.connect(databaseTV)
    curTV = cnxTV.cursor()

    for numId, episodeVu in dictSerie.items():

        #(50001, 'IBSfuEFS2@ZJ5RDR5MhELF#2160.REMUX.Multi', 'S05E0001')
        curTV.execute("SELECT saison, episode, link FROM tvshowEpisodes WHERE numId=?", (numId,))
        listeIn = curTV.fetchall()
        episodes = [(int("%d%s" %(x[0], str(x[1]).zfill(4))), x[2], "S%sE%s" %(str(x[0]).zfill(2), str(x[1]).zfill(4))) for x in listeIn]
        #episodes = uptobox.getEpisodesSuite(numId)
        #notice(episodes)
        for (episode, lien, numEpisode) in sorted(episodes):
            if episode > episodeVu:
                lien = "*".join([x[1] for x in episodes if episode == x[0]])
                serie = [numId, "", "", lien]

                #57532  Les Rollers de Danny    Melle Marjorie reçoit les patins à propulseur de Danny. Tous deux se retrouvent perdus dans les égouts  2020-10-23  /gbxv7a21ntmIBhUzhRI30Ib1oEi.jpg    0.0 7   19
                try:
                    sql = "SELECT title, overview, year, backdrop, popu FROM tvshowEpisodesInfos WHERE numId={} AND saison={} AND episode={}".format(numId, int(numEpisode.split("E")[0][1:]), int(numEpisode.split("E")[1]))
                    #notice(sql)
                    serie += extractMedias(sql=sql, bd=databaseTV)[0]
                    sql = "SELECT Title, overview, year, backdrop, popu FROM seriesPub WHERE numId={}".format(numId)
                    title = extractMedias(sql=sql)[0][0]
                    serie[4] = title + " - " + serie[4]
                except:
                    sql = "SELECT Title, overview, year, backdrop, popu FROM seriesPub WHERE numId={}".format(numId)
                    serie += extractMedias(sql=sql)[0]


                serie += [int(numEpisode.split("E")[0][1:]), int(numEpisode.split("E")[1]), 0]
                listeSerie.append(serie)
                del serie
                break

    curTV.close()
    cnxTV.close()

    xbmcplugin.setPluginCategory(HANDLE, "Episodes")
    xbmcplugin.setContent(HANDLE, 'episodes')
    for l in listeSerie[::-1]:
        media = Media("episode", *l)
        media.typeMedia = "episode"
        media.numId = int(l[0])
        addDirectoryEpisodes("%s ([COLOR red]S%sE%s[/COLOR])" %(media.title, str(media.saison).zfill(2), str(media.episode).zfill(2)), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)


def tmdbSerie(params):
    numId = params["u2p"]
    saison = params["saison"]
    episodes = uptobox.getEpisodesSuite(numId)
    notice(episodes)
    listeSerie  = []
    listesEpisodes = []
    for (episode, lien, numEpisode) in [x for x in sorted(episodes) if "S%s" %str(saison).zfill(2) == x[2].split("E")[0]]:
        if episode not in listesEpisodes:
            lien = "*".join([x[1] for x in episodes if episode == x[0]])
            serie = [numId, "", "", lien]
            sql = "SELECT Title, overview, year, backdrop, popu FROM seriesPub WHERE numId={}".format(numId)
            serie += extractMedias(sql=sql)[0]
            serie += [int(numEpisode.split("E")[0][1:]), int(numEpisode.split("E")[1]), 0]
            listeSerie.append(serie)
            listesEpisodes.append(episode)
    xbmcplugin.setPluginCategory(HANDLE, "Episodes")
    xbmcplugin.setContent(HANDLE, 'episodes')
    for l in listeSerie:
        media = Media("episode", *l)
        media.typeMedia = "episode"
        media.numId = int(l[0])
        addDirectoryEpisodes("%s ([COLOR white]S%sE%s[/COLOR])" %(media.title, str(media.saison).zfill(2), str(media.episode).zfill(2)), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)


def extractMedias(bd=BDREPONEW, limit=0, offset=1, sql="", unique=0):
    cnx = sqlite3.connect(bd)
    cur = cnx.cursor()
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
    except:
        notice("Pb extract :" +str(sql))
    cur.close()
    cnx.close()
    return requete

def getOrderDefault():
    dictTrie = {"Année": " ORDER BY m.year DESC",
                "Titre": " ORDER BY m.title COLLATE NOCASE ASC",
                "Popularité": " ORDER BY m.popu DESC",
                "Date Release": " ORDER BY m.dateRelease DESC",
                "Date Added": " ORDER BY m.id DESC"}
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    ordre = addon.getSetting("lists_orderby")
    return dictTrie[ordre]

def menu():
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choix = [
        ("Pastes Pastebin/Anotepad", {"action":"menuPastebin"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/pastebin.png', "Partage vias les pastes", 0),
        #("Repertoires cryptés", {"action":"menuRepCrypte"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Partage alternatif via rep publique crypté", 1),
            ]
    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte, maj = ch
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte,'mediatype': 'video'})
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def detailsmenuRepCrypte(params):
    typM = params["typM"]
    bd = scraperUPTO.BDrepCrypt(BDREPONEW)
    listeReposFilms, listeReposSeries, listeReposDivers = bd.getRepoMedias()
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    if typM == "films":
        choix = [(u"[%s]" %x.capitalize(), {"action":"folderPub", "offset": "0", "typM": "films", "repo": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Partage alternatif films rep publique crypté", 2) for x in listeReposFilms]
    elif typM == "series":
        choix = [(u"[%s]" %x.capitalize(), {"action":"folderPub", "offset": "0", "typM": "series", "repo": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Partage alternatif Series rep publique crypté", 1) for x in listeReposSeries]
    elif typM == "divers":
        choix = [(u"[%s]" %x.capitalize(), {"action":"folderPub", "offset": "0", "typM": "divers", "repo": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Partage alternatif Divers rep publique crypté", 3) for x in listeReposDivers]

    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte, maj = ch
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte,'mediatype': 'video'})
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        commands = []
        if maj == 2:
            commands.append(('[COLOR yellow]Maj[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestionMajRep)'))
        elif maj == 1:
            commands.append(('[COLOR yellow]Maj[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestionMajRepSerie)'))
        elif maj == 3:
            commands.append(('[COLOR yellow]Protection Accés[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=lockRepHK&repo=%s)' %(parameters["repo"])))
        if commands:
            li.addContextMenuItems(commands)
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)


def menuPastebin():
    bd = BdHK(BDBOOKMARK)
    liste = bd.getRepos()

    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choix = [("Créér Repo", {"action":"repopastebin"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Créér un repo avec des pastes", 0)]
    if liste:
        choix += [(x[0], {"action":"affRepoPaste", "repo": x[0], "typM": x[1], "offset": 0}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', x[0], 1) for x in liste]
    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte, maj = ch
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte,'mediatype': 'video'})
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def majContenu():
    showInfoNotification("Maj!")
    for nomRep, tabPaste in dictPaste.items():
        pDialog2 = xbmcgui.DialogProgressBG()
        pDialog2.create('Pbi2kodi', 'Création Groupes (%s)...' %nomRep)
        #notice(nomRep)
        paramPaste = {"tabIdPbi": tabPaste, "namePbi": 'test', "repKodiName": "", "clear": 0}
        pbi = Pastebin(**paramPaste)
        pbi.UpdateGroupe(pbi.dictGroupeFilms, __database__, progress= pDialog2, gr=nomRep)
        pbi.UpdateGroupe(pbi.dictGroupeSeries, __database__, mediaType="tvshow", progress= pDialog2, gr=nomRep)
        pDialog2.close()
    showInfoNotification("Groupes créés!")


def menuRepCrypte():
    ADDON.setSetting("passtmp", "")
    """
    maj = int(ADDON.getSetting("nbHmaj"))
    try:
        h = int(scraperUPTO.lastMaj())
    except:
        h =0
    if (time.time() - h) > (3600 * maj):
        scraperUPTO.majHkNew()
    """
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choix = [
        #("Ajouter", {"action":"folderPastebin", "maj": "false"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Partage alternatif rep publique crypté", 0),
        #("Series", {"action":"folderPubDetails", "offset": "0", "typM": "series"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/series1.png', "Partage alternatif series rep publique crypté", 1),
        ("Series & Animes", {"action":"mediasHKSeries"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/series1.png', "Partage alternatif series rep publique crypté", 1),
        ("Films", {"action":"mediasHKFilms"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/film1.png', "Partage alternatif films rep publique crypté", 2),
        ("Divers", {"action":"folderPubDetails", "offset": "0", "typM": "divers"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', \
            "Possibilité import pack images/synop pour le contenu FANKAi (merci a didi) via le mode skin", 3),
        ("# Ma Recherche", {"action":"affSearch"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "type de recherche dispo", 10)
            ]
    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte, maj = ch
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte,'mediatype': 'video'})
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        commands = []
        commands.append(('[COLOR yellow]Maj[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=majHkNew)'))
        """
        if maj == 2:
            #commands.append(('[COLOR yellow]Maj[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestionMajRep)'))
            commands.append(('[COLOR yellow]Maj[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=majHkNew)'))
        if maj == 1:
            commands.append(('[COLOR yellow]Maj[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestionMajRepSerie)'))
        """
        if commands:
            li.addContextMenuItems(commands)
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)


def affRepo(params):
    notice(params)
    offset = int(params["offset"])
    limit = 50
    repo = params["repo"]
    typM = params["typM"]
    bd = BdHK(BDBOOKMARK)
    if typM == "film":
        sql = "SELECT numId FROM movieGroupes WHERE groupe='{}' AND typ=0 ORDER BY id DESC LIMIT {} OFFSET {}".format(repo, limit, offset)
        tab = bd.executeSQL(sql=sql, unique=1)
        sql = "SELECT link FROM movieLink WHERE numId={}"
        tabFiles = [(x, "*".join(bd.executeSQL(sql=sql.format(x), unique=1))) for x in tab]
        medias = uptobox.getFilmsUptoNews(tabFiles)
        uptobox.affUptoboxNews("movie", [x[1:]  for x in medias], params, cr=1)

    elif typM == "serie":
        sql = "SELECT numId FROM tvshowsGroupes WHERE groupe='{}' AND typ=0 ORDER BY id DESC LIMIT {} OFFSET {}".format(repo, limit, offset)
        tab = bd.executeSQL(sql=sql, unique=1)
        medias = uptobox.getSeriesUptoNews(tab)
        affPastebinSerie("movie", [x[1:]  for x in medias], params,)

def addDirectory(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(label=name)
    li.setUniqueIDs({ 'tmdb' : media.numId }, "tmdb")
    li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, "dbid": media.numId + 500000,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu, "duration": media.duration * 60 })

    li.setArt({'icon': media.backdrop,
            'thumb': media.poster,
            'poster': media.poster,
            'fanart': media.backdrop})
    li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)


def affPastebinSerie(typM, medias, params=""):
    xbmcplugin.setPluginCategory(HANDLE, typM)
    xbmcplugin.setContent(HANDLE, 'movies')
    i = -1
    for i, media in enumerate(medias):
        try:
            media = Media(typM, *media[:-1])
        except:
            media = Media(typM, *media)
        ok = addDirectory("%s" %(media.title), isFolder=True, parameters={"action": "affSaisonPastebin", "u2p": media.numId}, media=media)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    if i > -1:
        if i >= (LIMIT - 1):
            addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def affSaisonPastebin(params):
    bd = BdHK(BDBOOKMARK)
    numId = params["u2p"]
    sql = "SELECT DISTINCT saison FROM tvshowEpisodes WHERE numId={} ORDER BY saison".format(numId)
    tabFiles = bd.executeSQL(sql=sql, unique=1)
    params["tabsaison"] = "*".join([str(x) for x in tabFiles])
    loadSaisonsPastebin(params)

def addDirectoryMenu(name, isFolder=True, parameters={}, media="" ):
    li = xbmcgui.ListItem(label=name)
    if media:
        li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre,
                "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu})
        li.setArt({'icon': media.backdrop,
                    "thumb": media.poster,
                    'poster':media.poster,
                    'fanart': media.backdrop
                    })

    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def loadSaisonsPastebin(params):
    typMedia = "tvshow"
    numId = params["u2p"]
    mDB = TMDB(KEYTMDB)
    dictSaison = mDB.serieNumIdSaison(numId)
    choixsaisons = []
    tabExtract = [("", x, "") for x in params["tabsaison"].split("*")]
    for rep, saison, num in tabExtract:
        r = re.search(r"(?P<num>\d+)", saison)
        if r:
            numSaison = int(r.group('num'))
            try:
                infos = dictSaison[numSaison]
            except:
                infos = ("Saison %s" %str(numSaison).zfill(2), "", "Pas de Synopsis....")
            choixsaisons.append((infos[0], {"action": "visuEpisodesPastebin", "u2p": numId, "saison": numSaison}))
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    xbmcplugin.setContent(HANDLE, 'episodes')
    categories = [("[COLOR red]Bande Annonce[/COLOR]", {"action": "ba", "u2p": numId, "typM": typMedia})] + choixsaisons + \
        [("Acteurs", {"action": "affActeurs", "u2p": numId, "typM": typMedia}),\
        ("Similaires", {"action": "suggest", "u2p": numId, "typ": "Similaires","typM": typMedia}), \
        ("Recommandations", {"action": "suggest", "u2p": numId, "typ": "Recommendations", "typM": typMedia})]
    for cat in categories:
        if "saison" in cat[1].keys():
            numSaison = cat[1]["saison"]
            try:
                tab = dictSaison[numSaison]
                lFinale = ["", tab[2], "", "", tab[1], "", numId, tab[1]]
            except Exception as e:
                notice(str(e))

            media = Media("menu", *lFinale)
            media.saison = numSaison
            media.typeMedia = typMedia
        else:
            media = ""
        addDirectoryMenu(cat[0], isFolder=True, parameters=cat[1], media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def visuEpisodesPastebin(params):
    bd = BdHK(BDBOOKMARK)
    numId = params["u2p"]
    saison = params["saison"]
    notice(saison.zfill(2))
    sql = "SELECT DISTINCT episode FROM tvshowEpisodes WHERE saison='{}' AND numId={} ORDER BY episode".format(saison.zfill(2), numId)
    tab = bd.executeSQL(sql=sql, unique=1)
    notice(tab)
    tabFiles = [(str(x).zfill(4), "*".join(bd.executeSQL(sql="SELECT link FROM tvshowEpisodes WHERE numId={} AND saison='{}' AND episode={}"\
                .format(numId, saison.zfill(2), x), unique=1))) for x in tab]

    affEpisodesPastebin(numId, saison, tabFiles)

def affEpisodesPastebin(numId, saison, liste):
    typM = "episode"
    xbmcplugin.setPluginCategory(HANDLE, "Episodes")
    xbmcplugin.setContent(HANDLE, 'episodes')
    mdb = TMDB(KEYTMDB)
    tabEpisodes = mdb.saison(numId, saison)
    for numEpisode, filecodes in sorted(liste):
        l = [numId, saison, numEpisode, filecodes]
        try:
            lFinale = list(l) + list([episode for episode in tabEpisodes if int(numEpisode) == episode[-1]][0])
        except:
            lFinale = list(l) + ["Episode", "Pas de synopsis ....", "", "", "", saison, numEpisode]
        isVu = 0
        lFinale.append(isVu)
        media = Media("episode", *lFinale)
        media.typeMedia = typM
        media.numId = int(numId)
        addDirectoryEpisodes("E%d - %s" %(int(numEpisode), media.title), isFolder=False, \
            parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode, "saison": media.saison}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def addDirectoryEpisodes(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(label=("%s" %(name)))
    li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, 'playcount': media.vu, "dbid": media.numId + 500000,
        "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu, "episode": media.episode, "season": media.saison})
    #vinfo = li.getVideoInfoTag()
    #vinfo.setPlot(media.overview)

    li.setArt({'icon': media.backdrop,
              "fanart": media.backdrop,
              "poster": media.backdrop})
    li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

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
    if "limit" in params.keys():
            params["offset"] = str(int(params["offset"]) + int(params["limit"]))
    else:
        try:
            params["offset"] = str(int(params["offset"]) + int(LIMIT))
        except: pass
    url = sys.argv[0] + '?' + urlencode(params)
    return xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=isFolder)

def createRepo():
    a = time.time()
    BdHK(BDBOOKMARK)
    lp = LoadPastes()
    pastes = lp.idPaste(ADDON.getSetting("numpastes"))
    LesPastes  = sorted([("%s => %s" %(x[0], x[2]), x[1], x[0]) for x in pastes if len(x) > 2])
    dialog = xbmcgui.Dialog()
    pasteOk = dialog.multiselect("Choix pastes", [x[0] for x in LesPastes], preselect=[])
    if pasteOk:
        getPastes = [LesPastes[x][1] for x in pasteOk]
        dialog = xbmcgui.Dialog()
        repo = dialog.input("Nom du repo", type=xbmcgui.INPUT_ALPHANUM)
        if repo:
            maj = 0
            for i, paste in enumerate(getPastes):
                threading.Thread(name="bdhk", target=lp.gestion, args=(paste, maj, repo, CHEMINPASTES, )).start()
                print(i + 1)
                time.sleep(0.01)
            lp.testThread()
            notice(time.time() - a)
            cnx = sqlite3.connect(BDBOOKMARK)
            cur = cnx.cursor()
            cur.execute("SELECT numId FROM movie")
            listeNumIdMovie = [x[0] for x in cur.fetchall()]
            cur.execute("SELECT numId FROM tvshow")
            listeNumIdTvshow = [x[0] for x in cur.fetchall()]
            for media in lp.tabMediasTotal:

              if media[0] == "film":
                if media[1][0] not in listeNumIdMovie:
                    listeNumIdMovie.append(media[1][0])
                cur.execute("REPLACE INTO movie (numId, title, year, genre, saga) VALUES (?, ?, ?, ?, ?)", media[1])
                cur.executemany("REPLACE INTO movieLink (numId, link) VALUES (?, ?)", media[2])
                cur.executemany("REPLACE INTO movieGroupes (numId, groupe, typ) VALUES (?, ?, ?)", [(x[0], repo, 0) for x in media[2]])
              elif media[0] == "serie":
                if media[1][0] not in listeNumIdMovie:
                    listeNumIdTvshow.append(media[1][0])
                    cur.execute("REPLACE INTO tvshow (numId, title, year, genre, saga) VALUES (?, ?, ?, ?, ?)", media[1])
                cur.executemany("REPLACE INTO tvshowEpisodes (numId, saison, episode, link) VALUES (?, ?, ?, ?)", media[2])
                cur.executemany("REPLACE INTO tvshowsGroupes (numId, groupe, typ) VALUES (?, ?, ?)", [(x[0], repo, 0) for x in media[2]])
              for paste in getPastes:
                cur.execute("REPLACE INTO repos (nom, typ, paste) VALUES (?, ?, ?)", (repo, media[0], paste, ))
            cnx.commit()

            cur.close()
            cnx.close()
            notice(time.time() - a)
    return


def affGlobal():
    dictTyp = {"movie": "Film", "tvshow": "Serie"}
    dialog = xbmcgui.Dialog()
    d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
    if len(d) > 2:
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id \
            FROM seriesPub as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
        tvshows = extractMedias(sql=sql)
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM filmsPub as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
        movies = extractMedias(sql=sql)

        xbmcplugin.setContent(HANDLE, 'movies')
        for typM, medias in [("movie", movies), ("tvshow", tvshows)]:

            i = 0
            for i, media in enumerate(medias):
                media = Media(typM, *media[:-1])
                media.title = "%s (%s)" %(media.title, dictTyp[typM])
                if typM == "movie":
                    ok = addDirectoryMedia("%s" %(media.title), isFolder=True, parameters={"action": "detailM", "lien": media.link, "u2p": media.numId}, media=media)
                else:
                    ok = addDirectoryMedia("%s" %(media.title), isFolder=True, parameters={"action": "affSaisonUptofoldercrypt", "u2p": media.numId}, media=media)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        if i == (int(LIMIT) -1):
            addDirNext(params)

        xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def affMedias(typM, medias, params=""):

    xbmcplugin.setPluginCategory(HANDLE, typM)
    try:
        if medias[0][4] == "divers":
            xbmcplugin.setContent(HANDLE, 'files')
        elif typM == "movie":
            xbmcplugin.setContent(HANDLE, 'movies')
        else:
            xbmcplugin.setContent(HANDLE, 'tvshows')
    except:
        xbmcplugin.setContent(HANDLE, 'movies')
    i = 0
    for i, media in enumerate(medias):
        try:
            media = Media(typM, *media[:-1])
        except:
            media = Media(typM, *media)
        if typM == "movie":
            ok = addDirectoryMedia("%s" %(media.title), isFolder=True, parameters={"action": "detailM", "lien": media.link, "u2p": media.numId}, media=media)
        else:
            if "suite" in params.keys():
                #media.title = media.title + ", on continue..."
                ok = addDirectoryMedia("%s" %(media.title), isFolder=True, parameters={"action": "suiteSerieHK", "u2p": media.numId}, media=media)
            else:
                if " (HK)" in media.title:
                    ok = addDirectoryMedia("%s" %(media.title), isFolder=True, parameters={"action": "detailT", "lien": media.link, "u2p": media.numId}, media=media)
                else:
                    ok = addDirectoryMedia("%s" %(media.title), isFolder=True, parameters={"action": "affSaisonUptofoldercrypt", "u2p": media.numId}, media=media)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    #xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS, labelMask="Page Suivante")
    if i >= int(LIMIT) - 1:
        addDirNext(params)

    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def addDirectoryMedia(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(label=name)
    li.setUniqueIDs({ 'tmdb' : media.numId }, "tmdb")
    li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, "dbid": media.numId + 500000,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu, "duration": media.duration * 60 })

    li.setArt({'icon': media.backdrop,
            'thumb': media.poster,
            'poster': media.poster,
             'fanart': media.backdrop})
    li.setProperty('IsPlayable', 'true')

    commands = []
    commands.append(('[COLOR yellow]Bande Annonce[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=ba&u2p=%s&typM=%s)' %(media.numId, media.typeMedia)))
    if media.typeMedia == "movie":
        commands.append(('[COLOR yellow]Recherche HK²[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=mediasHKFilms&famille=Search,return)'))
        sch = 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=mediasHKFilms&famille=Search,return)'
    else:
        commands.append(('[COLOR yellow]Recherche[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=mediasHKSeries&famille=Search,return)'))
        sch = 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=mediasHKSeries&famille=Search,return)'
    commands.append(('[COLOR yellow]Gestion[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestionMedia&u2p=%s&typM=%s)'%(media.numId, media.typeMedia)))
    commands.append(('[COLOR yellow]Choix Profil[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=actifPm)'))
    commands.append(('[COLOR yellow]Reload Skin[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=rlk)'))
    li.addContextMenuItems(commands)

    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

if __name__ == '__main__':

    a = time.time()
    BdHK(BDBOOKMARK)
    keyTMDB = "2b554df34a51fab8738ad94cbdc969d9"

    lp = LoadPastes()
    pastes = list(set(lp.idPaste("3i5tnrt3")))
    TABMEDIATOTAL = []
    repo = "film"
    maj = 0
    for i, paste in enumerate(pastes):
        threading.Thread(name="bdhk", target=lp.gestion, args=(paste, maj, repo, CHEMINPASTES, )).start()
        print(i + 1)
        time.sleep(0.01)
    lp.testThread()
    print(time.time() - a)

    #(numId, title, year, genres, saga)
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    for media in lp.tabMediasTotal:
      if media[0] == "film":
        cur.execute("REPLACE INTO movie (numId, title, year, genre, saga, repo) VALUES (?, ?, ?, ?, ?, ?)", media[1])
        cur.executemany("REPLACE INTO movieLink (numId, link) VALUES (?, ?)", media[2])
      elif media[0] == "serie":
        cur.execute("REPLACE INTO tvshow (numId, title, year, genre, saga, repo) VALUES (?, ?, ?, ?, ?, ?)", media[1])
        cur.executemany("REPLACE INTO tvshowEpisodes (numId, saison, episode, link) VALUES (?, ?, ?, ?)", media[2])

    cnx.commit()
    cur.close()
    cnx.close()

    #https://api.themoviedb.org/3/movie/1368?api_key=2b554df34a51fab8738ad94cbdc969d9&language=fr&append_to_response=images


