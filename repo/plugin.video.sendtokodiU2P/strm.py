import json
import os
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import pyxbmct
import requests
import io
import unicodedata
import re
import ast
import sqlite3
import shutil
import time
from medias import Media, TMDB
import medias
import zipfile
import threading
import datetime
from upNext import upnext_signal
from uptobox import getEpisodesSaison
import widget
from datetime import datetime
from datetime import timedelta
try:
    import iptv
    vIPTV = True
except ImportError:
    vIPTV = False
try:
    # Python 3
    from urllib.parse import parse_qsl
    from util import *
except ImportError:
    from urlparse import parse_qsl
try:
    # Python 3
    from urllib.parse import unquote, urlencode, quote
    unichr = chr
except ImportError:
    # Python 2
    from urllib import unquote, urlencode, quote
try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser


def notice(content):
    log(content, xbmc.LOGINFO)


def log(msg, level=xbmc.LOGINFO):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s (strm.py): %s' % (addonID, msg), level)


def configureSTRM():
    Strm().configure()


class Strm():
    BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db')
    NEWSERIES = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/newserie.txt')
    def __init__(self, bdd=None):
        self.limitPerWidget = 1000
        self.bd = bdd
        #notice("-----------------------------------------------")


        self.addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
        self.strmFolder = self.addon.getSetting("strmFolder")


        if "WIN" in self.strmFolder:
            self.repKodiName = "D:\\kodiBase\\"
        elif "LIBREELEC" in self.strmFolder:
            self.repKodiName = "/storage/downloads/Kodi/"
        elif "LINUX" in self.strmFolder:
            self.repKodiName = "/storage/downloads/Kodi/"
        elif "ANDROID" in self.strmFolder:
            self.repKodiName = "/storage/emulated/0/kodiBase/"
        elif "XBOX" in self.strmFolder:
            self.repKodiName = "U:\\Users\\UserMgr0\\AppData\\Local\\Packages\\XBMCFoundation.Kodi_4n2hpmxwrvr6p\\LocalState\\userdata\\"
        else:
            self.repKodiName = self.strmFolder

        self.initBDD()
        pass

    def configure(self):
        dialog = xbmcgui.Dialog()
        notice("STRM - Configure")
        cnx = sqlite3.connect(self.BDBOOKMARK)
        cur = cnx.cursor()
        cur.execute("SELECT id,title,type FROM listes")
        listes = cur.fetchall()
        cur.execute("SELECT id FROM strm")
        oldIdSelected = cur.fetchall()
        #notice("oldid %s "%oldIdSelected)
        oldIdSelected = [x[0] for x in oldIdSelected]
        cnx.commit()
        #notice("oldid %s "%oldIdSelected)


        sorted_by_first = sorted(listes, key=lambda tup: tup[0])
        listes = ["["+y[2].title() +"] "+ y[1] for y in sorted_by_first]
        listesId = [y[0] for y in sorted_by_first]

        presel = [sorted_by_first.index(y) for y in sorted_by_first if y[0] in oldIdSelected]

        #notice("presel %s "%presel)

        chListes = dialog.multiselect("Selectionner la/les liste(s) à importer", listes, preselect=presel)
        if chListes != None and len(chListes) != 0:
            cur.execute("DELETE FROM strm")
            cnx.commit()
            goodId = [[listesId[x]] for x in chListes]
            sql = "INSERT  INTO strm (id) VALUES(?)"
            cur.executemany(sql, goodId)
            cnx.commit()
            cur.close()
            cnx.close()

        pass


    def initBDD(self):
        cnx = sqlite3.connect(self.BDBOOKMARK)
        cur = cnx.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS strm(`id` INTEGER PRIMARY KEY)""")
        cnx.commit()
        cur.close()
        cnx.close()


    def internalExtractList(self,t="film"):
        cnx = sqlite3.connect(self.BDBOOKMARK)
        cur = cnx.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS listes(
        `id`    INTEGER PRIMARY KEY,
        title TEXT,
        sql TEXT,
        type TEXT,
        UNIQUE (title))
            """)
        cnx.commit()
        if t == "all":
            sql = "SELECT t.title FROM listes AS t INNER JOIN strm AS tr ON t.id = tr.id"
            cur.execute(sql)
        else:
            sql = "SELECT t.title FROM listes AS t INNER JOIN strm AS tr ON t.id = tr.id and t.type=?"
            cur.execute(sql, (t, ))
        listes = [x[0] for x in cur.fetchall() if x]
        cur.close()
        cnx.close()
        return listes

    def makeStrms(self, clear=0):
        self.pDialog = xbmcgui.DialogProgressBG()
        self.pDialog.create('U2P - STRM Generation', 'STRM Generation ...')


        listeRep = list(self.internalExtractList(t="film"))
        for widgetName in listeRep:
            movies = self.getList(widgetName)
            self.makeMovieSTRM(liste=movies,nomRep=widgetName)


        listSeries = list(self.internalExtractList(t="serie"))
        for widgetSName in listSeries:
            series = self.getSerieList(widgetSName)
            self.makeSeriesSTRM(liste=series, nomRep=widgetSName, clear=clear)
        self.pDialog.close()

    def getSerieList(self, widgetName=""):
        sql = widget.getListe(widgetName, "serie")
        sql = sql.replace("SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m", \
            "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m")
        sql = sql.replace("genre ", "genres ")
        series = uExtractMedias(self.bd,sql=sql)
        return series

    def getList(self, widgetName=""):
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='docu'"
        liste = uExtractMedias(self.bd, sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='concert'"
        liste += uExtractMedias(self.bd, sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='spectacle'"
        liste += uExtractMedias(self.bd, sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='sport'"
        liste += uExtractMedias(self.bd, sql=sql, unique=1)
        sql = "SELECT f.numId FROM filmsRepos as f WHERE f.famille='quebec'"
        liste += uExtractMedias(self.bd, sql=sql, unique=1)

        sql = widget.getListe(widgetName, "film")

        sql = sql.replace("SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id                         FROM movie as m",
                          "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id FROM filmsPub as m")

        sql = sql.replace("m.numId NOT IN (SELECT sp.numId FROM movieFamille as sp WHERE sp.famille == '#Spectacles') AND genre NOT LIKE '%%Documentaire%%' AND genre NOT LIKE '%%Animation%%' AND genre != 'Musique' AND ",
                          "m.numId NOT IN ({}) AND genres NOT LIKE '%%Documentaire%%' AND genres NOT LIKE '%%Animation%%' AND ".format(",".join([str(x) for x in list(set(liste))])))
        sql = sql.replace("genre ", "genres ")

        #notice("getList - sql - %s"%sql)

        movies = uExtractMedias(self.bd, sql=sql)
        return movies

    def makeMovieSTRM(self, liste, clear=0, nomRep=""):

        nomRep = makeNameRep(nomRep)
        if nomRep:
            repFilm = os.path.join(self.repKodiName+"/Movies/", nomRep + "/")
            try:
                os.makedirs(repFilm)
            except: pass
        else:
            repFilm = self.repKodiName

        repFilm = os.path.normpath(repFilm)

        #notice("makeMovieNFO - repFilm : %s"%repFilm)

        if clear == 1:
            try:
                shutil.rmtree(repFilm, ignore_errors=True)
            except:
                pass

        try:
            os.makedirs(repFilm)
        except Exception as e:
            pass

        maxItem = min(len(liste),self.limitPerWidget)

        nb = len(liste)
        for i, movie in enumerate(liste):
            if i >= maxItem:
                 break
            #notice(movie)
            percentage = int((i/(float)(maxItem))*100.0)
            self.pDialog.update(percentage, 'Films %s/%s' % (i, maxItem))
            time.sleep(0.001)
            title=movie[0]
            numId=movie[4]

            links=movie[7]
            if links != None:
                titreStrm = self.makeNameRep(title)
                urlFilm = "*".join(links.split(","))
                textStream = u"plugin://plugin.video.sendtokodiU2P/?action=play&lien={}".format(urlFilm)
                strm = "%s.strm" %numId

                repStream = os.path.join(repFilm , "%s - (%s)" %(titreStrm, numId))
                repMovie = os.path.join(repStream, strm)
                repMovie = os.path.normpath(repMovie)
                repNFO = os.path.join(repStream, "%s.nfo" %numId)
                repNFO = os.path.normpath(repNFO)
                try:
                    os.mkdir(repStream)
                except Exception as e:
                    pass
                    #notice("erreur rep: %s" %(unicodedata.normalize('NFD', repStream).encode('ascii','ignore').decode("latin-1")))

                self.saveFile(repMovie, textStream)

                textNFO = u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<movie>
<tmdbid>{0}</tmdbid>
</movie>
http://www.themoviedb.org/movie/{0}""".format(numId)
                self.saveFile(repNFO, textNFO)


    def makeSeriesSTRM(self, liste, clear=0, nomRep=""):
        #notice(clear)
        nomRep = makeNameRep(nomRep)
        if nomRep:
            repSerie = os.path.join(self.repKodiName+"/Series/", nomRep + "/")
            try:
                os.makedirs(repSerie)
            except: pass
        else:
            repSerie = self.repKodiName

        repSerie = os.path.normpath(repSerie)

        #notice("makeSeriesSTRM - repSerie : %s"%repSerie)

        try:
            os.makedirs(repSerie)
        except Exception as e:
            pass

        maxItem = min(len(liste),self.limitPerWidget)

        #notice(len(liste))

        dictSerie  = {}
        fNewSerie = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/newserie.txt')
        if os.path.exists(fNewSerie) and not clear:
            with open(fNewSerie, "r") as f:
                tx = f.read()
            tx = [int(x) for x in tx.split("\n") if x]
            liste = [x for x in liste if int(x[4]) in tx]
            #notice(tx)
        else:
            if not clear:
                liste = []

        #notice(len(liste))
        for i, movie in enumerate(liste[::-1]):
            if i >= maxItem:
                break

            serieDir = os.path.join(repSerie , self.makeNameRep(movie[0]) + "/")

            if repSerie not in serieDir:
                serieDir = os.path.join(repSerie , str(movie[4]) + "/")
            try:
                os.makedirs(serieDir)
            except Exception as e:
                pass

            #notice(movie)
            #notice(serieDir)
            percentage = int((i/(float)(maxItem))*100.0)
            self.pDialog.update(percentage, 'STRMS Series', message='%s (%s/%s)' % (movie[0],i,maxItem))

            #notice("----------------------------------------------------------------")
            #notice("-------------------------------%s---------------------------------"%movie[0])
            numId = movie[4]

            notice("maj strms :: %d" %int(numId))
            repNFO = os.path.join(serieDir, "tvshow.nfo")
            repNFO = os.path.normpath(repNFO)
            textNFO = u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<tvshow>
<tmdbid>{0}</tmdbid>
</tvshow>
https://www.themoviedb.org/tv/{0}&islocal=True""".format(numId)
            if not os.path.isfile(repNFO):
                self.saveFile(repNFO, textNFO)

            dictSaisonsVU, tabFiles = getEpisodesSaison(movie[4])
            saisons = [x for x in sorted(dictSaisonsVU)]
            #notice("dictSaisonsVU:%s"%dictSaisonsVU)
            dictSaison = {x: sorted([z[1:] for z in tabFiles if x == z[0]])  for x in list(set([y[0] for y in tabFiles]))}
            for saison in saisons:
                saisonDir = self.makeNameRep(saison)
                r = re.search(r"(?P<num>\d+)", saison)
                if r:
                    numSaison = int(r.group('num'))
                    try:
                        os.makedirs(os.path.join(serieDir, saisonDir))
                    except Exception as e:
                        #notice(e)
                        pass
                    self.createEpisodeSTRM(numId,numSaison,dictSaison[saison],serieDir,saisonDir)


    def createEpisodeSTRM(self,numId,saison, episodes,SerieDir,saisonDir):

        Tsaison = str(saison).zfill(2)

        mDB = TMDB(KEYTMDB)
        # episodes existants tmdb
        tabEpisodes = [x[-1] for x in mDB.saison(numId, saison)]
        for episode in list(set([x[0] for x in episodes])):
            # test si episode existe chez tmdb
            if episode in tabEpisodes:
                lNameDirName = ("S%sE%s" %(str(saison).zfill(2), str(episode).zfill(4)))

                #limitations a 60 liens du a plantage, a affiner
                urlFilm = "*".join([x[1] for x in episodes[:60] if x[0] == episode])
                textStream = u"plugin://plugin.video.sendtokodiU2P/?action=play&lien={}".format(urlFilm)
                strm = "%s.strm" %lNameDirName

                finalRep = os.path.join(SerieDir, saisonDir, strm)
                self.saveFile(finalRep, textStream)


    def makeNameRep(self, title):
        title = unquote(title)#, encoding='latin-1', errors='replace')
        title = unicodedata.normalize('NFD', title).encode('ascii','ignore').decode("latin-1")
        tab_remp = [r''',|\\|/|:|\*|\?|"|<|>|\|| {2,}''', ' ']
        title = re.sub(tab_remp[0], tab_remp[1], title)
        title = title[:64].strip()
        return title

    def saveFile(self, fileIn, textOut):
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