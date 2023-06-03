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
from pastebin import Pastebin
from apiTraktHK import TraktHK
from medias import Media, TMDB
import createbdhk
import threading
import datetime
import widget
from datetime import datetime
from datetime import timedelta

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

import random

try:
    import xbmc
    import xbmcvfs
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
    import pyxbmct
    from util import *
    BDMEDIA = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/medias.bd')
    BDMEDIANew = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasNew.bd')
    ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    KEYTMDB = ADDON.getSetting("apikey")
    HANDLE = int(sys.argv[1])
    BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasHK.bd')
    BDREPO = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mymedia.db')
    BDREPONEW = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasNew.bd')
    BDHK = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/medias.bd')
    CHEMIN = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P')
    KEYFANART = ADDON.getSetting("keyfanart")
except: pass

pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor
if pyVersionM == 11:
    import cryptPaste11 as cryptage
    import scraperUPTO11 as scraperUPTO
elif pyVersionM == 8:
    import cryptPaste8 as cryptage
    import scraperUPTO8 as scraperUPTO
    #import scraperUPTO
elif pyVersionM == 9:
    import cryptPaste9 as cryptage
    import scraperUPTO9 as scraperUPTO
elif pyVersionM == 10:
    import cryptPaste10 as cryptage
    import scraperUPTO10 as scraperUPTO
else:
    notice(pyVersion)
    notice(pyVersionM)


class FenInfo(pyxbmct.BlankDialogWindow):

    def __init__(self, argvs):
        """Class constructor"""
        numId, title, typM = argvs
        #pyxbmct.skin.estuary = True

        # Call the base class' constructor.
        super(FenInfo, self).__init__()
        # Set width, height and the grid parameters
        self.numId = numId
        self.typM = typM
        self.setGeometry(1250, 700, 50, 30)

        self.infosComp()
        # Call set controls method
        self.set_controls()

        # Call set navigation method.
        self.set_navigation()

        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def infosComp(self):
        mdb = TMDB(KEYTMDB)
        dictInfos =  mdb.movieNumIdFull(self.numId)
        self.tagline = dictInfos.get("tagline", "")
        self.vote_average = dictInfos.get("vote_average", 0)
        self.vote_count = dictInfos.get("vote_count", 0)
        original_title = dictInfos.get("original_title", "")
        self.budget = dictInfos.get("budget", 0)
        self.revenue = dictInfos.get("revenue", 0)
        try:
            production_companies = ", ".join([x["name"] for x in dictInfos["production_companies"]])
        except:
            production_companies = ""

    def set_controls(self):

        """Set up UI controls"""
        self.colorMenu = '0xFFFFFFFF'
        size = self.getTaille()

        sql = "SELECT title, overview, year, genres, backdrop, popu, numId, poster, runtime, saga FROM filmsPub WHERE numId={}".format(self.numId)
        liste = createbdhk.extractMedias(sql=sql)
        try:
            title, overview, year, genre, backdrop, popu, numId, poster, duration, self.saga = liste[0]
            backdrop = "http://image.tmdb.org/t/p/" + size[1] + backdrop
        except:
            backdrop = ""
        try:
            poster = "http://image.tmdb.org/t/p/" + size[0] + poster
        except Exception as e:
            poster = ""
            #notice(e)

        if backdrop:
            image = pyxbmct.Image(backdrop)
            self.placeControl(image, 0, 7, rowspan=42, columnspan=23)


        f = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/png/fond.png')
        fond = pyxbmct.Image(f)
        self.placeControl(fond, 0, 0, rowspan=54, columnspan=30)


        try:
            logo = getFanart(self.numId)
        except:
            logo = ""
        #clearlogo ou title
        if logo:
            imageLogo = pyxbmct.Image(logo[0][3])
            self.placeControl(imageLogo, 0, 0, rowspan=10, columnspan=7)
        else:
            label = pyxbmct.Label(title, font='font_MainMenu')
            self.placeControl(label, 2, 0, columnspan=15)

        #budjet
        labBudj = pyxbmct.FadeLabel()
        self.placeControl(labBudj, 29, 25, columnspan=5)
        labBudj.addLabel("Budget: %.2f M$" %(self.budget / 1000000.0))

        #revenue
        labRev = pyxbmct.FadeLabel()
        self.placeControl(labRev, 31, 25, columnspan=5)
        labRev.addLabel("Revenu: %.2f M$" %(self.revenue / 1000000.0))

        #vote nb
        labNbC = pyxbmct.FadeLabel()
        self.placeControl(labNbC, 33, 25, columnspan=5)
        labNbC.addLabel("Nb Votes: %s" %(self.vote_count))

        #note
        labNote = pyxbmct.FadeLabel()
        self.placeControl(labNote, 35, 25, columnspan=5)
        labNote.addLabel("Note: %s" %(self.vote_average))

        #labelMenu = pyxbmct.Label('MENU', textColor=self.colorMenu)
        #self.placeControl(labelMenu, 31, 0, columnspan=10)
        self.menu = pyxbmct.List('font13', _itemHeight=30, _alignmentY=90)
        self.placeControl(self.menu, 29, 0, rowspan=12, columnspan=24)
        #, "Acteurs & Réalisateur"
        if self.saga:
            self.menu.addItems(["[COLOR blue]Bande Annonce[/COLOR]", "[COLOR green]Lire[/COLOR]", "Saga", "Suggestions", "Similaires"])
        else:
            self.menu.addItems(["[COLOR blue]Bande Annonce[/COLOR]", "[COLOR green]Lire[/COLOR]", "Suggestions", "Similaires"])
        #self.menu.addItems(self.tabNomLien)
        self.connect(self.menu, lambda: self.listFunction(self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()))


        self.setCasting()

        #overview
        if self.tagline:
            synopText = "\n[B][I]%s[/I][/B]\n\n[COLOR white]SYNOPSIS: [/COLOR]" %self.tagline
        else:
            synopText = "[COLOR red]SYNOPSIS: [/COLOR]"
        self.synop = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.synop, 10, 0, rowspan=16, columnspan=18)
        self.synop.setText(synopText + overview)
        self.synop.autoScroll(4000, 2000, 3000)

        #============================================================================ ligne notation duree =========================================
        ligneNot = 26
        #duree
        text = "0xFFFFFFFF"
        current_time = datetime.now()
        future_time = current_time + timedelta(minutes=duration)
        heureFin = future_time.strftime('%H:%M')

        label = pyxbmct.Label('%s       %d mns (se termine à %s)' %(year, duration, heureFin), textColor=self.colorMenu)
        self.placeControl(label, ligneNot, 0, columnspan=12)


        #notation
        label = pyxbmct.Label('%0.1f/10' %float(popu),textColor=self.colorMenu)
        self.placeControl(label, ligneNot, 12, columnspan=12)

        #fav HK
        self.radiobutton = pyxbmct.RadioButton("Ajouter Fav's HK", textColor=self.colorMenu)
        self.placeControl(self.radiobutton, 26, 25, columnspan=5, rowspan=3)
        self.connect(self.radiobutton, self.radio_update)
        if ADDON.getSetting("bookonline") != "false":
            listeM = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=movies" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
            listeM = [int(x) for x in listeM]
        else:
            listeM = list(widget.extractFavs())
        if int(self.numId) in listeM:
            self.radiobutton.setSelected(True)
            self.radiobutton.setLabel("Retirer Fav's HK")
        #=============================================================================================================================================

        #genres
        label = pyxbmct.FadeLabel()
        self.placeControl(label, 26, 17, columnspan=5)
        label.addLabel(genre)




    def affSaga(self, numId):
        createbdhk.mediasHKFilms({"famille": "sagaListe", "numIdSaga": numId})
        self.close()

    def getBa(self, params):
        numId = params["u2p"]
        typMedia = params["typM"]
        mdb = TMDB(KEYTMDB)
        tabBa = mdb.getNumIdBA(numId, typMedia)
        if tabBa:
            dialog = xbmcgui.Dialog()
            selectedBa = dialog.select("Choix B.A", ["%s (%s)" %(x[0], x[1]) for x in tabBa], 0, 0)
            if selectedBa  != -1:
                keyBa = tabBa[selectedBa][2]
                xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/?action=play_video&videoid={})".format(keyBa), True)
        self.close()

    def setCasting(self):
        # cast
        posy = 0
        posx = 15
        pos = 0
        posh = 38
        mdb = TMDB(KEYTMDB)
        liste = mdb.castFilm(self.numId)
        nbListe = len(liste)
        self.tabCast = []
        if pos in range(nbListe):
            casting1 = liste[pos]
            if casting1[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting1[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting1[0], casting1[1])
            bcast1 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast1, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast1, lambda: self.affCastingFilmo(str(casting1[3])))
            self.tabCast.append(bcast1)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting2 = liste[pos]
            if casting2[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting2[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting2[0], casting2[1])
            bcast2 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast2, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast2, lambda: self.affCastingFilmo(str(casting2[3])))
            self.tabCast.append(bcast2)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting3 = liste[pos]
            if casting3[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting3[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting3[0], casting3[1])
            bcast3 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast3, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast3, lambda: self.affCastingFilmo(str(casting3[3])))
            self.tabCast.append(bcast3)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting4 = liste[pos]
            if casting4[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting4[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting4[0], casting4[1])
            bcast4 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast4, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast4, lambda: self.affCastingFilmo(str(casting4[3])))
            self.tabCast.append(bcast4)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting5 = liste[pos]
            if casting5[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting5[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting5[0], casting5[1])
            bcast5 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast5, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast5, lambda: self.affCastingFilmo(str(casting5[3])))
            self.tabCast.append(bcast5)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting6 = liste[pos]
            if casting6[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting6[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting6[0], casting6[1])
            bcast6 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast6, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast6, lambda: self.affCastingFilmo(str(casting6[3])))
            self.tabCast.append(bcast6)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting7 = liste[pos]
            if casting7[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting7[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting7[0], casting7[1])
            bcast7 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast7, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast7, lambda: self.affCastingFilmo(str(casting7[3])))
            self.tabCast.append(bcast7)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting8 = liste[pos]
            if casting8[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting8[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting8[0], casting8[1])
            bcast8 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast8, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast8, lambda: self.affCastingFilmo(str(casting8[3])))
            self.tabCast.append(bcast8)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting9 = liste[pos]
            if casting9[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting9[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting9[0], casting9[1])
            bcast9 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast9, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast9, lambda: self.affCastingFilmo(str(casting9[3])))
            self.tabCast.append(bcast9)
            posy += 3
            pos += 1
        if pos in range(nbListe):
            casting10 = liste[pos]
            if casting10[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting10[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting10[0], casting10[1])
            bcast10 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast10, posh, posy, rowspan=posx, columnspan=3)
            self.connect(bcast10, lambda: self.affCastingFilmo(str(casting10[3])))
            self.tabCast.append(bcast10)
            posy += 3
            pos += 1

    def setCasting2(self):
        mdb = TMDB(KEYTMDB)
        liste = mdb.castFilm(self.numId)
        nbListe = len(liste)
        posy = 0
        self.tabCast = []
        for i, casting1 in enumerate(liste[:10]):
            if casting1[2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + casting1[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting1[0], casting1[1])
            self.tabCast.append(pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000'))
            self.placeControl(self.tabCast[i], 38, posy, rowspan=15, columnspan=3)

            posy += 3
        for j in range(len(self.tabCast)):
            notice(liste[j][3])
            self.connect(self.tabCast[j], lambda: self.affCastingFilmo(str(liste[j][3])))

    def affCastingFilmo(self, numId):
        #mediasHK({"famille": "cast", "u2p": numId})
        notice(numId)
        createbdhk.mediasHKFilms({"famille": "cast", "u2p": numId})
        self.close()



    def getTaille(self):
      dictSize = {"Basse": ("w185/", "w780/"),
                "Moyenne": ("w342/", "w1280/"),
                "Haute": ("w500/", "original/")}
      v = ADDON.getSetting("images_sizes")
      return dictSize[v]

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=200 time=700',),
                                ('WindowClose', 'effect=fade start=200 end=0 time=700',)])

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        self.menu.controlUp(self.radiobutton)

        if self.tabCast:
            self.menu.controlDown(self.tabCast[0])
            self.menu.controlLeft(self.tabCast[0])
            self.radiobutton.controlUp(self.tabCast[0])

        self.menu.controlRight(self.radiobutton)
        self.radiobutton.controlRight(self.menu)
        self.radiobutton.controlLeft(self.menu)
        self.radiobutton.controlDown(self.menu)
        self.setFocus(self.menu)


        if self.tabCast:
            for i in range(len([x for x in self.tabCast if x])):
                self.tabCast[i].controlUp(self.menu)
                self.tabCast[i].controlDown(self.radiobutton)
                if (i + 1) < len([x for x in self.tabCast if x]):
                    self.tabCast[i].controlRight(self.tabCast[i + 1])
                if (i - 1) > -1:
                    self.tabCast[i].controlLeft(self.tabCast[i - 1])



    def radio_update(self):
        # Update radiobutton caption on toggle
        #liste favs
        if self.radiobutton.isSelected():
            self.radiobutton.setLabel("Retirer Fav's HK")
            gestionFavHK({"mode": "ajout", "u2p": self.numId, "typM": "movies"})
        else:
            self.radiobutton.setLabel("Ajouter Fav's HK")
            gestionFavHK({"mode": "sup", "u2p": self.numId, "typM": "movies"})

    def listFunction(self, tx):
        #lsite fonction du menu
        self.close()
        if "Bande" in tx:
            self.getBa({"u2p": self.numId, "typM": "movie"})

        elif "Saga" in tx:
            self.affSaga(self.saga)

        elif "Lire" in tx:
            sql =  "SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId={}".format(self.numId)
            links = createbdhk.extractMedias(sql=sql, unique=1)[0]
            affLiens2({"u2p": self.numId, "lien": links})

        elif "Simi" in tx:
            self.simi("Similaires")
        elif "Sugg" in tx:
            self.simi("Recommendations")

    def simi(self, recherche="Similaires"):
        mdb = TMDB(KEYTMDB)
        if recherche == "Similaires":
            liste = mdb.suggReco(self.numId, "movie", "similar")
        elif recherche == "Recommendations":
            liste = mdb.suggReco(self.numId, "movie", "recommendations")

        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
            FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
        movies = createbdhk.extractMedias(sql=sql)
        if movies:
            #affMovies("movie", movies[:-1])
            createbdhk.affMedias("movie", movies[:-1])


def getFanart(numId, typm="movies"):
        """ insert image de fanat.yv"""
        url = "http://webservice.fanart.tv/v3/{}/{}?api_key={}".format(typm, numId, KEYFANART)

        try:
            req = requests.request("GET", url, data=None, timeout=3)
        except:
            time.sleep(5)
            req = requests.request("GET", url, data=None, timeout=3)
        dictInfos = req.json()
        listeImages = []
        if typm == "movies":
            for typeLogo in dictInfos.keys():
                if "movie" in typeLogo:
                    try:
                        listeImages += [(dictInfos["tmdb_id"], dictInfos["name"], typeLogo, x["url"], x["lang"]) for x in dictInfos[typeLogo] if x["lang"] in ["fr", "en"]]
                    except: pass

        #clearlogo
        images = [x for x in listeImages if "logo" in x[2] and "fr" == x[-1]]
        #print(images)
        if images:
            logo = images[0][2]

        else:
            images = [x for x in listeImages if "logo" in x[2] and "en" == x[-1]]
            if images:
                logo = images[0][2]
            else:
                logo = ""

        return images


def affLiens2(params):
    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typMedia:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    paramstring = params["lien"].split("*")
    numId = params["u2p"]
    u2p = params["u2p"]
    cr = cryptage.Crypt()
    #notice(paramstring)
    tabLinkIn = [(x.split("#")[0].split("@")[0], x.split("#")[0].split("@")[1]) for x in paramstring]
    dictResos = {}
    for i in range(0, len(tabLinkIn), 100):
        dictResos.update(cr.extractReso(tabLinkIn[i: i + 100]))
    dictResos = {x.split("#")[0].split("@")[1]: dictResos[x.split("#")[0].split("@")[1]] if dictResos[x.split("#")[0].split("@")[1]] else x.split("#")[1] for x in paramstring}
    paramstring = orderLiens(dictResos, paramstring)
    tabNomLien = ["[COLOR %s]#%d[/COLOR]| %s - %.2fGo" %(colorLiens(dictResos[x.split("#")[0].split("@")[1]][0]), i + 1, dictResos[x.split("#")[0].split("@")[1]][0], (int(dictResos[x.split("#")[0].split("@")[1]][1]) / 1000000000.0)) for i, x in enumerate(paramstring)]
    tabRelease = [dictResos[x.split("#")[0].split("@")[1]][2] for i, x in enumerate(paramstring)]
    tabLiens = [(x, paramstring[i], tabRelease[i]) for i, x in enumerate(tabNomLien)]
    affLiens(numId, "movie", tabLiens)


def affLiens(numId, typM, liste):
    xbmcplugin.setPluginCategory(HANDLE, "Liens")
    xbmcplugin.setContent(HANDLE, 'files')
    sql = "SELECT title, overview, year, poster, numId, genres, popu, backdrop, runtime, id FROM filmsPub WHERE numId={}".format(numId)
    movie = createbdhk.extractMedias(sql=sql)
    for l in liste:
        l = list(l)
        l += movie[0]
        media = Media("lien", *l)
        media.typeMedia = typM
        if typM == "movie":
            addDirectoryFilms("%s" %(l[0]), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)


def orderLiens(dictResos, paramstring):
    tabLinks = []
    tabLinks2 = []
    taille = 5000000001
    filtre = 0
    if ADDON.getSetting("filtliens") != "false":
        filtre = 1
    for k, v in dictResos.items():
        tabFiltre = []
        link = [x for x in paramstring if k in x]
        if filtre:
            notice(v)
            if re.search(r"1080", v[0], re.I) and (re.search(r"\.multi", v[0], re.I) or re.search(r"\.vf", v[0], re.I) or re.search(r"\.truefrench", v[0], re.I) or re.search(r"\.french", v[0], re.I)) and int(v[1]) < taille:
                tabLinks.append(list(v) + [k] + link)
            tabLinks2.append(list(v) + [k] + link)
        else:
            link = [x for x in paramstring if k in x]
            tabLinks.append(list(v) + [k] + link)
    if not tabLinks:
        tabLinks = tabLinks2[:]
    try:
        return [x[-1] for x in sorted(tabLinks, key=lambda taille: taille[1], reverse=True)]
    except:
        return paramstring


def colorLiens(lien):
    #for c in [("2160", "[COLOR fuchsia]2160[/COLOR]"), ("3D", "[COLOR yellow]3D[/COLOR]"),\
    #     ("1080", "[COLOR goldenrod]1080[/COLOR]"), ("720", "[COLOR seagreen]720[/COLOR]"), ("480", "[COLOR dodgerblue]480[/COLOR]")]:
    #    lien = lien.replace(c[0], c[1])
    if "2160" in lien or re.search("4K", lien, re.I):
        c = "red"
    elif re.search("3D", lien, re.I):
        c = "yellow"
    elif "1080" in lien:
        c = "fuchsia"
    elif "720" in lien:
        c = "seagreen"
    elif "480" in lien:
        c = "dodgerblue"
    else:
        c = "white"
    return c

def addDirectoryFilms(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=name)
    updateInfoTagVideo(li,media,True,False,True,False,False)
    #liz.setPath("plugin://%s/play/%s" % (ADDON.getAddonInfo("id"),urllib.quote(url, safe='')) )
    li.setArt({'icon': media.backdrop,
            'thumb': media.poster,
            'poster': media.poster,
            #'icon': addon.getAddonInfo('icon'),
             'fanart': media.backdrop})
    if media.clearlogo :
        li.setArt({'clearlogo': media.clearlogo})
    if media.clearart :
        li.setArt({'clearart': media.clearart})
    commands = []
    #commands.append(("Ajout Fav'S HK", 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=fav&mode=ajout&u2p=%s&typM=movies)' %media.numId, ))
    commands.append(('[COLOR yellow]Bande Annonce[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=ba&u2p=%s&typM=%s)' %(media.numId, media.typeMedia)))
    if media.typeMedia == "movie":
        #trk = actifTrakt()
        #if trk and  media.typeMedia == "movie":
        #   commands.append(('[COLOR yellow]Cocher Vu dans Trakt[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=vuMovieTrakt&u2p=%s,return)' %media.numId))
        commands.append(('[COLOR yellow]Recherche[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=MenuFilm&famille=Search,return)'))
        sch = 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=MenuFilm&famille=Search,return)'
    else:
        commands.append(('[COLOR yellow]Recherche[/COLOR]', 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=MenuSerie&famille=Search,return)'))
        sch = 'ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=MenuSerie&famille=Search,return)'
    commands.append(('[COLOR yellow]Gestion[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestionMedia&u2p=%s&typM=%s)'%(media.numId, media.typeMedia)))
    commands.append(('[COLOR yellow]Choix Profil[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=actifPm)'))
    commands.append(('[COLOR yellow]Reload Skin[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=rlk)'))
    #commands.append(("[COLOR yellow]Refresh[/COLOR]", "Container.Refresh"))
    li.addContextMenuItems(commands)
    """
    isWidget = xbmc.getInfoLabel('Container.PluginName')
    if "U2P" not in isWidget:
        li.setProperty('widget', 'true')
        if media.typeMedia == "movie":
            li.setProperty('widgetmovie', 'true')
            li.setProperty('lire', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=visuFenmovie&u2p=%s&title=%s&lien=%s)' %(media.numId, media.title, media.link))
            #li.setProperty('lire', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=playHK&u2p=%s&typM=%s&lien=%s)' %(media.numId, media.typeMedia, media.link))
        li.setProperty('ba', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=ba&u2p=%s&typM=%s)' %(media.numId, media.typeMedia))
        li.setProperty('gestion', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=gestionMedia&u2p=%s&typM=%s)'%(media.numId, media.typeMedia))
        li.setProperty('search', sch)
        li.setProperty('profil', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=actifPm)')
        li.setProperty("reloadSkin", 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=rlk)')
        #li.setProperty("Refresh", "Container.Refresh")
    """
    li.setProperty('IsPlayable', 'true')
    url = "plugin://plugin.video.sendtokodiU2P/" + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=isFolder)

def actifTrakt():
    trk = None
    if ADDON.getSetting("traktperso") != "false":
        if ADDON.getSetting("bookonline") != "false":
            userPass = [x[1] for x in widget.usersBookmark() if x[0] == __addon__.getSetting("profiltrakt")]
            if userPass and ADDON.getSetting("bookonline_name") == userPass[0]:
                    trk = TraktHK()
        else:
            trk = TraktHK()
    return trk


def gestionFavHK(params):
    trk = actifTrakt()
    if params["mode"] == "ajout":
        typAjout = "add"
        if ADDON.getSetting("bookonline") != "false":
            widget.pushSite("http://%s/requete.php?name=%s&type=infavs&media=%s&numid=%s" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name"), params["typM"], params["u2p"]))
        else:
            widget.ajoutFavs(params["u2p"], params["typM"])
    else:
        typAjout = "remove"
        if ADDON.getSetting("bookonline") != "false":
            widget.pushSite("http://%s/requete.php?name=%s&type=supfavs&media=%s&numid=%s" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name"), params["typM"], params["u2p"]))
        else:
            widget.supFavs(params["u2p"], params["typM"])
    if trk:
        if params["typM"] == "movies":
            trk.gestionWatchlist(numId=[int(params["u2p"])], typM="movie", mode=typAjout)
        else:
            trk.gestionWatchlist(numId=[int(params["u2p"])], typM="show", mode=typAjout)
    return