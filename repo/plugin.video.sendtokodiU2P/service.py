# -*- coding: utf-8 -*-
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


from pastebin import Pastebin
from apiTraktHK import TraktHK
import createbdhk
import random
import uptobox
from strm import Strm, configureSTRM
import feninfo
try:
    BDMEDIA = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/medias.bd')
    BDMEDIANew = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasNew.bd')
except: pass

class FenInfo(pyxbmct.AddonFullWindow):


    #def __init__(self, numId, title="", typM="film"):
    def __init__(self, title=""):
        """Class constructor"""
        # Call the base class' constructor.
        self.numId = title.split("*")[0]
        title = title.split("*")[1]
        self.typM = "film"
        super(FenInfo, self).__init__(title)
        # Set width, height and the grid parameters


        self.setGeometry(1250, 700, 50, 30)
        self.setBackground(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/png/fond.png'))

        # Call set controls method
        self.set_controls()

        # Call set navigation method.
        self.set_navigation()

        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):
        """Set up UI controls"""
        notice(self.numId)
        self.colorMenu = '0xFFFFFFFF'
        size = self.getTaille()

        sql = "SELECT title, overview, year, genres, backdrop, popu, numId, poster, runtime, saga FROM filmsPub WHERE numId={}".format(self.numId)
        liste = createbdhk.extractMedias(sql=sql)
        try:
            title, overview, year, genre, backdrop, popu, numId, poster, duration, saga = liste[0]
            backdrop = "http://image.tmdb.org/t/p/" + size[1] + backdrop
            poster = "http://image.tmdb.org/t/p/" + size[0] + poster
        except:
            return


        #backdrop
        #image = pyxbmct.Image(backdrop, colorDiffuse='0x22FFFFFF')

        image = pyxbmct.Image(backdrop)
        self.placeControl(image, 0, 7, rowspan=42, columnspan=23)

        f = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/png/fond.png')
        fond = pyxbmct.Image(f)
        self.placeControl(fond, 0, 0, rowspan=54, columnspan=30)

        #f = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/png/fond.png')
        #fond = pyxbmct.Image(f)
        #self.placeControl(fond, 0, 14, rowspan=25, columnspan=15)


        logo = ""
        #logo, clearart, banner = extractFanart(self.numId)
        #urlFanart = "http://assets.fanart.tv/fanart/movie/"

        #clearlogo ou title
        if logo:
            imageLogo = pyxbmct.Image(urlFanart + logo)
            self.placeControl(imageLogo, 0, 0, rowspan=8, columnspan=7)
        else:
            label = pyxbmct.Label(title, font='font_MainMenu')
            self.placeControl(label, 2, 0, columnspan=15)

        #poster
        #if clearart:
        #    imageClearart = pyxbmct.Image(urlFanart + clearart)
        #    self.placeControl(imageClearart, 35, 25, rowspan=12, columnspan=5)
        #else:

        #poster = pyxbmct.Image(poster)
        #self.placeControl(poster, 29, 25, rowspan=24, columnspan=5)

        """
        #menu
        paramstring = self.links.split("*")
        cr = cryptage.Crypt()

        dictResos = cr.extractReso([(x.split("#")[0].split("@")[0], x.split("#")[0].split("@")[1]) for x in paramstring])
        dictResos = {x.split("#")[0].split("@")[1]: dictResos[x.split("#")[0].split("@")[1]] if dictResos[x.split("#")[0].split("@")[1]] else x.split("#")[1] for x in paramstring}
        self.paramstring = orderLiens(dictResos, paramstring)
        tabRelease = [dictResos[x.split("#")[0].split("@")[1]][2] for i, x in enumerate(self.paramstring)]
        self.tabNomLien = ["#%d [COLOR red][%s - %.2fGo][/COLOR] -- [Release: %s]" %(i + 1, dictResos[x.split("#")[0].split("@")[1]][0], (int(dictResos[x.split("#")[0].split("@")[1]][1]) / 1000000000.0), tabRelease[i]) for i, x in enumerate(self.paramstring)]
        """

        #labelMenu = pyxbmct.Label('MENU', textColor=self.colorMenu)
        #self.placeControl(labelMenu, 31, 0, columnspan=10)
        self.menu = pyxbmct.List('font13', _itemHeight=30, _alignmentY=90)
        self.placeControl(self.menu, 29, 0, rowspan=12, columnspan=30)
        #, "Acteurs & Réalisateur"
        self.menu.addItems(["[COLOR blue]Bande Annonce[/COLOR]", "[COLOR green]Links[/COLOR]", "Saga", "Suggestions", "Similaires", "Studio"])
        #self.menu.addItems(self.tabNomLien)
        self.connect(self.menu, lambda: self.listFunction(self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()))


        #overview
        #labelSynop = pyxbmct.Label('SYNOPSIS', textColor=colorMenu)
        #self.placeControl(labelSynop, 14, 0, columnspan=10)
        self.synop = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.synop, 10, 0, rowspan=16, columnspan=18)
        self.synop.setText("[COLOR green]SYNOPSIS: [/COLOR]" + overview)
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
        #self.slider = pyxbmct.Slider(orientation=xbmcgui.HORIZONTAL)
        #self.placeControl(self.slider, ligneNot + 1, 14, pad_y=1, rowspan=2, columnspan=4)
        #self.slider.setPercent(media.popu * 10)

        """
        #play
        p = 0
        self.buttonLinks = pyxbmct.Button("Links")
        self.placeControl(self.buttonLinks, 31, p, columnspan=3, rowspan=5)
        self.connect(self.buttonLinks, self.buttonFx)

        p += 3
        self.buttonBa = pyxbmct.Button("Bande Annonce")
        self.placeControl(self.buttonBa, 31, p, columnspan=3, rowspan=5)

        p += 3
        self.buttonSaga = pyxbmct.Button("Saga")
        self.placeControl(self.buttonSaga, 31, p, columnspan=3, rowspan=5)

        p += 3
        self.buttonReco = pyxbmct.Button("Recommendations")
        self.placeControl(self.buttonReco, 31, p, columnspan=3, rowspan=5)

        p += 3
        self.buttonSimi = pyxbmct.Button("Similaires")
        self.placeControl(self.buttonSimi, 31, p, columnspan=3, rowspan=5)

        p += 3
        self.buttonStudio = pyxbmct.Button("Studio")
        self.placeControl(self.buttonStudio, 31, p, columnspan=3, rowspan=5)
        """

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

        # sagas
        self.sagaOk = False
        #sql = "SELECT s.title, s.poster, s.numId FROM saga AS s WHERE s.numId=(SELECT t.numIdSaga FROM sagaTitle AS t WHERE t.numId={})".format(self.numId)
        #saga = extractMedias(sql=sql)
        #notice(saga)
        saga =0
        if saga:
            self.sagaOk = True
            label = pyxbmct.Label("SAGA", textColor=self.colorMenu)
            self.placeControl(label, 43, 22, columnspan=4)
            if saga[0][1]:
                imFoc = "http://image.tmdb.org/t/p/w92" + saga[0][1]
            else:
                imFoc = ""
            txRea = saga[0][0]
            self.bSaga = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(self.bSaga, 40, 24, rowspan=10, columnspan=2)
            self.connect(self.bSaga, lambda: self.affSaga(str(saga[0][2])))

        self.setCasting()

        # cast
        #mdb = TMDB(__keyTMDB__)
        #liste = mdb.castFilm(self.numId)
        #notice(liste)
        #label = pyxbmct.Label('REALISATEUR:',textColor=colorMenu)
        #self.placeControl(label, 8, 0, columnspan=5)
        #rea = ", ".join([x[0] for x in liste if x[1] == "Réalisateur"])
        #label = pyxbmct.Label(rea)
        #self.placeControl(label, 8, 4, columnspan=8)
        #label = pyxbmct.Label('ACTEURS:',textColor=colorMenu)
        #self.placeControl(label, 11, 0, columnspan=5)
        #acteurs = ", ".join(["%s (%s)" %(x[0], x[1]) for x in liste if x[1] != "Réalisateur"][:3])
        #label = pyxbmct.FadeLabel(font="font12")
        #self.placeControl(label, 11, 4, columnspan=10)
        #label.addLabel(acteurs)

    def buttonFx(self):
        sql =  "SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId={}".format(self.numId)
        links = createbdhk.extractMedias(sql=sql, unique=1)[0]
        #self.close()
        #affLiens2({"u2p":self.numId, "lien": links})

        #xbmc.executebuiltin('Dialog.Close(busydialog)')
        #xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=afficheLiens&lien={}&u2p={})".format(links, self.numId), True)
        #xbmc.executebuiltin("ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=afficheLiens&lien={}&u2p={},return)".format(links, self.numId))
        #xbmc.executebuiltin("ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=playHK&lien=IBSfuEFS2%404U3iXKqCCQZq%231080.Multi.WEB&u2p=852830,return)")

        #self.close()

    def affSaga(self, numId):
        showInfoNotification(numId)
        mediasHK({"famille": "sagaListe", "u2p": numId})
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
        mdb = TMDB(KEYTMDB)
        liste = mdb.castFilm(self.numId)
        nbListe = len(liste)
        posy = 0
        self.tabCast = [None] * 20
        self.tabCast2 = [None] * 20
        for i, casting1 in enumerate(liste[:10]):
            self.tabCast2[i] = casting1
            if self.tabCast2[i][2]:
                imFoc = "http://image.tmdb.org/t/p/w342" + self.tabCast2[i][2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(self.tabCast2[i][0], self.tabCast2[i][1])
            self.tabCast[i] = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(self.tabCast[i], 38, posy, rowspan=15, columnspan=3)
            self.connect(self.tabCast[i], lambda: self.affCastingFilmo(str(self.tabCast2[i][3])))
            posy += 3


    def affCastingFilmo(self, numId):
        mediasHK({"famille": "cast", "u2p": numId})
        self.close()



    def getTaille(self):
      dictSize = {"Basse": ("w185/", "w780/"),
                "Moyenne": ("w342/", "w1280/"),
                "Haute": ("w500/", "original/")}
      v = ADDON.getSetting("images_sizes")
      return dictSize[v]

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
                                ('WindowClose', 'effect=fade start=100 end=0 time=500',)])

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
                else:
                    if self.sagaOk:
                        self.tabCast[i].controlRight(self.bSaga)
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
        #self.close()
        if "Bande" in tx:
            self.getBa({"u2p": self.numId, "typM": "movie"})
        elif "Links" in tx:
            sql =  "SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId={}".format(self.numId)
            links = createbdhk.extractMedias(sql=sql, unique=1)[0]
            #affLiens2({"u2p": self.numId, "lien": links})
            #xbmc.executebuiltin("ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=playHK&lien=IBSfuEFS2%404U3iXKqCCQZq%231080.Multi.WEB&u2p=852830,return)")
            #xbmc.executebuiltin("ActivateWindow(10025,plugin://plugin.video.sendtokodiU2P/?action=afficheLiens&lien={}&u2p={},return)".format(links, self.numId))
            playMediaHK({"lien": "IBSfuEFS2@4U3iXKqCCQZq#1080.Multi.WEB", "u2p": "852830"})
        elif "Simi" in tx:
            loadSimReco2({"u2p": self.numId, "typ": "Similaires", "typM": "movie"})
        elif "Sugg" in tx:
            loadSimReco2({"u2p": self.numId, "typ": "Recommendations", "typM": "movie"})


class FenFilmDetail(pyxbmct.AddonDialogWindow):

    def __init__(self, title='', numId="", links=""):
        """Class constructor"""
        # Call the base class' constructor.
        super(FenFilmDetail, self).__init__(title)
        # Set width, height and the grid parameters
        self.numId = numId
        self.links = links
        self.setGeometry(1000, 560, 50, 30)
        # Call set controls method
        self.set_controls()
        # Call set navigation method.
        self.set_navigation()
        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):
        """Set up UI controls"""
        self.colorMenu = '0xFFFFFFFF'

        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId={}".format(self.numId)
        movies = extractMedias(sql=sql)
        media = Media("movie", *movies[0])


        #backdrop
        image = pyxbmct.Image(media.backdrop, colorDiffuse='0x22FFFFFF')
        self.placeControl(image, 0, 0, rowspan=50, columnspan=30)
        logo, clearart, banner = extractFanart(self.numId)
        urlFanart = "http://assets.fanart.tv/fanart/movie/"

        #clearlogo ou title
        if logo:
            imageLogo = pyxbmct.Image(urlFanart + logo)
            self.placeControl(imageLogo, 0, 0, rowspan=8, columnspan=7)
        else:
            label = pyxbmct.Label(media.title, font='font_MainMenu')
            self.placeControl(label, 2, 0, columnspan=15)

        #poster
        #if clearart:
        #    imageClearart = pyxbmct.Image(urlFanart + clearart)
        #    self.placeControl(imageClearart, 35, 25, rowspan=12, columnspan=5)
        #else:
        poster = pyxbmct.Image(media.poster)
        self.placeControl(poster, 0, 25, rowspan=23, columnspan=5)

        #menu
        paramstring = self.links.split("*")
        cr = cryptage.Crypt()

        dictResos = cr.extractReso([(x.split("#")[0].split("@")[0], x.split("#")[0].split("@")[1]) for x in paramstring])
        dictResos = {x.split("#")[0].split("@")[1]: dictResos[x.split("#")[0].split("@")[1]] if dictResos[x.split("#")[0].split("@")[1]] else x.split("#")[1] for x in paramstring}
        self.paramstring = orderLiens(dictResos, paramstring)
        tabRelease = [dictResos[x.split("#")[0].split("@")[1]][2] for i, x in enumerate(self.paramstring)]
        self.tabNomLien = ["#%d [COLOR red][%s - %.2fGo][/COLOR] -- [Release: %s]" %(i + 1, dictResos[x.split("#")[0].split("@")[1]][0], (int(dictResos[x.split("#")[0].split("@")[1]][1]) / 1000000000.0), tabRelease[i]) for i, x in enumerate(self.paramstring)]


        #labelMenu = pyxbmct.Label('MENU', textColor=self.colorMenu)
        #self.placeControl(labelMenu, 31, 0, columnspan=10)
        self.menu = pyxbmct.List('font13', _itemHeight=30)
        self.placeControl(self.menu, 29, 0, rowspan=24, columnspan=25)
        #, "Acteurs & Réalisateur"
        #self.menu.addItems(["[COLOR blue]Bande Annonce[/COLOR]", "[COLOR green]Lire[/COLOR]", "Suggestions", "Similaires"])
        self.menu.addItems(self.tabNomLien)
        self.connect(self.menu, lambda: self.listFunction(self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()))

        #overview
        #labelSynop = pyxbmct.Label('SYNOPSIS', textColor=colorMenu)
        #self.placeControl(labelSynop, 14, 0, columnspan=10)
        self.synop = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.synop, 10, 0, rowspan=16, columnspan=25)
        self.synop.setText("[COLOR green]SYNOPSIS: [/COLOR]" + media.overview)
        self.synop.autoScroll(1000, 2000, 3000)

        #============================================================================ ligne notation duree =========================================
        ligneNot = 26
        #duree
        text = "0xFFFFFFFF"
        current_time = datetime.now()
        future_time = current_time + timedelta(minutes=media.duration)
        heureFin = future_time.strftime('%H:%M')

        label = pyxbmct.Label('%s       Durée: %d mns (se termine à %s)' %(media.year, media.duration, heureFin), textColor=self.colorMenu)
        self.placeControl(label, ligneNot, 0, columnspan=12)


        #notation
        label = pyxbmct.Label('Note %0.1f/10' %float(media.popu),textColor=self.colorMenu)
        self.placeControl(label, ligneNot, 12, columnspan=12)
        #self.slider = pyxbmct.Slider(orientation=xbmcgui.HORIZONTAL)
        #self.placeControl(self.slider, ligneNot + 1, 14, pad_y=1, rowspan=2, columnspan=4)
        #self.slider.setPercent(media.popu * 10)

        #fav HK

        self.radiobutton = pyxbmct.RadioButton("Ajouter Fav's HK", textColor=self.colorMenu)
        self.placeControl(self.radiobutton, 26, 20, columnspan=5, rowspan=3)
        self.connect(self.radiobutton, self.radio_update)
        if __addon__.getSetting("bookonline") != "false":
            listeM = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=movies" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            listeM = [int(x) for x in listeM]
        else:
            listeM = list(widget.extractFavs())
        if int(self.numId) in listeM:
            self.radiobutton.setSelected(True)
            self.radiobutton.setLabel("Retirer Fav's HK")
        #=============================================================================================================================================

        #genres
        label = pyxbmct.Label('    GENRES')
        self.placeControl(label, 23, 26, columnspan=3)

        genres = [x.strip() for x in media.genre.split(",")]
        x, y = 25, 25
        for i, genre in enumerate(genres):
            f = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/png/genre/%s.png' %genre)
            image = pyxbmct.Image(f)
            pas = 9
            self.placeControl(image, x, y, rowspan=pas, columnspan=3)
            if i % 2:
                x += (pas - 2)
                y -= 2
            else:
                y += 2
            if i == 3:
                break


    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""

        self.menu.controlUp(self.radiobutton)
        #self.menu.controlDown(self.tabCast[0])
        #self.menu.controlLeft(self.tabCast[0])
        #self.radiobutton.controlUp(self.tabCast[0])
        self.menu.controlRight(self.radiobutton)
        self.radiobutton.controlRight(self.menu)
        self.radiobutton.controlLeft(self.menu)
        self.radiobutton.controlDown(self.menu)
        self.setFocus(self.menu)



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
        link = self.paramstring[self.tabNomLien.index(tx)]
        #showInfoNotification(link)
        #
        playMediaHK({"u2p":self.numId, "typM": "movies", "lien": link, "skin": "1"})

        """
        if "Bande" in tx:
            getBa({"u2p": self.numId, "typM": "movie"})
        elif "Lire" in tx:
            affLiens2({"u2p": self.numId, "lien": self.links})
        elif "Simi" in tx:
            loadSimReco2({"u2p": self.numId, "typ": "Similaires", "typM": "movie"})
        elif "Sugg" in tx:
            loadSimReco2({"u2p": self.numId, "typ": "Recommendations", "typM": "movie"})
        elif "Act" in tx:
            affCast2({"u2p": self.numId, "typM": "movie"})
        """




class replacement_stderr(sys.stderr.__class__):
    def isatty(self): return False

sys.stderr.__class__ = replacement_stderr


def debug(content):
    log(content, xbmc.LOGDEBUG)


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

def notice(content):
    log(content, xbmc.LOGINFO)

def log(msg, level=xbmc.LOGINFO):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level)

def showInfoNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message, xbmcgui.NOTIFICATION_INFO, 5000)

def showErrorNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message,
                                  xbmcgui.NOTIFICATION_ERROR, 5000)

def getkeyUpto():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    Apikey = addon.getSetting("keyupto")
    return Apikey

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
    resos = [addon.getSetting("resos")]
    timing = addon.getSetting("autoplay_delay")
    return resos, timing

"""
def getresosOld():
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
"""

def getNbMedias():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    nb = addon.getSetting("nb_items")
    return nb

def getOrderDefault():
    dictTrie = {"Année": " ORDER BY m.year DESC",
                "Titre": " ORDER BY m.title COLLATE NOCASE ASC",
                "Popularité": " ORDER BY m.popu DESC",
                "Date Release": " ORDER BY m.dateRelease DESC",
                "Date Added": " ORDER BY m.id DESC"}
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    ordre = addon.getSetting("lists_orderby")
    return dictTrie[ordre]

def getkeyTMDB():
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    Apikey = addon.getSetting("apikey")
    return Apikey

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
                      UNIQUE (numId, title, saison))
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
    elif argvs[0] == "getHK":
        cur.execute("SELECT reso FROM serie WHERE numId=? AND saison=?", argvs[1:])
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

'''
def detailsMediaOld(params):
    notice(params)
    paramstring = params["lien"].split("*")
    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typMedia:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    #typMedia = params["typM"]
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
'''

def getBa(params):
    numId = params["u2p"]
    typMedia = params["typM"]
    mdb = TMDB(__keyTMDB__)
    tabBa = mdb.getNumIdBA(numId, typMedia)
    if tabBa:
        dialog = xbmcgui.Dialog()
        selectedBa = dialog.select("Choix B.A", ["%s (%s)" %(x[0], x[1]) for x in tabBa], 0, 0)
        if selectedBa  != -1:
            keyBa = tabBa[selectedBa][2]
            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/?action=play_video&videoid={})".format(keyBa), True)


def gestionMedia(params):
    typMedia = params["typM"]
    numId = params["u2p"]
    if typMedia == "movie":
        media = "movies"
    else:
        media = "tvshow"
    dictA =  {}

    # on continue
    listeView = widget.extractOC()
    if int(numId) in listeView:
        #categories.append(("Retirer fav's-HK", {"action": "fav", "mode": "sup", "u2p": numId, "typM": "movies"}))
        dictA['Retirer de "On continue..."'] = (gestionoc, {"mode": "sup", "u2p": numId, "typM": media})
    else:
        dictA['Ajouter à "On continue..."'] = (gestionoc, {"mode": "ajout", "u2p": numId, "typM": media})
        #categories.append(("Ajouter fav's-HK", {"action": "fav", "mode": "ajout", "u2p": numId, "typM": "movies"}))


    #liste last view
    if __addon__.getSetting("bookonline") != "false":
        listeView = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=%s" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), typMedia))
        listeView = [int(x) for x in listeView]
    else:
        listeView = list(widget.extractIdInVu(t=media))
    if int(numId) in listeView:
        dictA["Retirer de l'historique"] = (supView, {"u2p": numId, "typM": media})
        #categories.append(("Retirer Last/View", {"action": "supView", "u2p": numId, "typM": "movies"}))

    #liste favs
    if __addon__.getSetting("bookonline") != "false":
        listeM = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=%s" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), media))
        listeM = [int(x) for x in listeM]
    else:
        listeM = list(widget.extractFavs(t=media))
    if int(numId) in listeM:
        #categories.append(("Retirer fav's-HK", {"action": "fav", "mode": "sup", "u2p": numId, "typM": "movies"}))
        dictA["Retirer des Favoris HK"] = (gestionFavHK, {"mode": "sup", "u2p": numId, "typM": media})
    else:
        dictA["Ajouter aux Favoris HK"] = (gestionFavHK, {"mode": "ajout", "u2p": numId, "typM": media})
        #categories.append(("Ajouter fav's-HK", {"action": "fav", "mode": "ajout", "u2p": numId, "typM": "movies"}))

    trk = actifTrakt()
    if trk and  typMedia == "movie":
        dictA["Cocher Vu dans Trakt"] = (vuMovieTrakt, {"u2p": numId})

    # listes vierge
    liste = widget.getListesV(typMedia)
    for l in liste:
        listeV = widget.getListesVdetail(l, typMedia)
        if int(numId) in listeV:
            dictA["Retirer de %s" %l] = (gestionListeV, {"mode": "sup", "u2p": numId, "typM": typMedia, "nom": l})
        else:
            dictA["Ajouter à %s" %l] = (gestionListeV, {"mode": "ajout", "u2p": numId, "typM": typMedia, "nom": l})
    dictA["Correction Certification"] = (correctCertif, {"u2p": numId, "typM": typMedia})
    tab = list(dictA.keys())
    dialog = xbmcgui.Dialog()
    ret = dialog.contextmenu(tab)
    if ret != -1:
        argv = dictA[tab[ret]][1]
        dictA[tab[ret]][0](argv)

def gestionListeV(params):
    typMedia = params["typM"]
    numId = params["u2p"]
    mode = params["mode"]
    nom = params["nom"]
    widget.gestionListeVdetail(nom, numId, typMedia, mode)

def fenInfo(params):
    u2p = params["u2p"]
    title = ""
    try:
        typM = params["typm"]
    except :
        typM = "film"

    #xbmc.executebuiltin('Dialog.Close(busydialog)')
    #window = feninfo.FenInfo(title)
    #window = FenInfo("%s*%s" %(u2p, title))

    window = feninfo.FenInfo([u2p, title, typM])
    # Show the created window.
    window.doModal()

    del window

#def detailsMedia(params):
#    detailsMedia2(params)
#    time.sleep(0.5)
#    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')
#    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')
#    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')
    #xbmc.executebuiltin('ReloadSkin')
#    xbmc.executebuiltin("Input.Back")
#    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Input.Back", "id": 1}')

def detailsMedia(params):
    notice("detailM")
    notice(params)
    if __addon__.getSetting("newfen") != "false":
        typM = "movie"
        title = ""
        numId = params["u2p"]
        #xbmc.executebuiltin('Dialog.Close(busydialog)')
        #window = feninfo.FenInfo(title)
        #window = FenInfo("%s*%s" %(u2p, title))

        window = feninfo.FenInfo([numId, title, typM])
        # Show the created window.
        window.doModal()

        del window
        #xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)
        #xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')
    else:
        try:
            links = params["lien"]
        except:
            try:
                if __addon__.getSetting("actifnewpaste") != "false":
                    sql =  "SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId={}".format(params["u2p"])
                    links = createbdhk.extractMedias(sql=sql, unique=1)[0]
                else:
                    sql = "SELECT link FROM movieLink WHERE numId={}".format(params["u2p"])
                    links = extractMedias(sql=sql, unique=1)[0]
            except:
                return False
        #typMedia = params["typM"]
        typMedia = "movie"
        numId = params["u2p"]
        u2p = params["u2p"]
        try:
            sql = "SELECT title, overview, year, genre, backdrop, popu, numId, poster, runtime FROM movie WHERE numId={}".format(numId)
            liste = extractMedias(sql=sql)
        except:
            liste = []
        if liste:
            title, overview, year, genre, backdrop, popu, numId, poster, runtime = liste[0]
        else:
            sql = "SELECT title, overview, year, genres, backdrop, popu, numId, poster, runtime FROM filmsPub WHERE numId={}".format(numId)
            liste = createbdhk.extractMedias(sql=sql)
            try:
                title, overview, year, genre, backdrop, popu, numId, poster, runtime = liste[0]
            except:
                return
        try: int(runtime)
        except: runtime = 0
        overview = "%s\nsynopsis: %s \nAnnée: %s\nGenre: %s\nNote: %.2f\nDurée: %.d mns" %(title, overview[:150] + "...", year, genre, popu, runtime)
        #fnotice(overview)
        xbmcplugin.setPluginCategory(__handle__, "Menu")
        xbmcplugin.setContent(__handle__, 'episodes')

        categories = [("[COLOR red]Bande Annonce[/COLOR]", {"action": "ba", "u2p": numId, "typM": typMedia}), ("[COLOR green]Lire[/COLOR]", {"action": "afficheLiens", "lien": links, "u2p": numId})]
        """
        if __addon__.getSetting("actifnewpaste")  != "false":
            sql = "SELECT t.saga FROM filmsPub AS t WHERE t.numId={}".format(u2p)
            saga = createbdhk.extractMedias(sql=sql, unique=1)
            if saga and saga[0]:
                categories += [("Saga", {"action": "mediasHKFilms", "famille": "sagaListe", "numIdSaga":saga[0]})]
        elif __addon__.getSetting("actifhk") != "false":
            sql = "SELECT s.title, s.poster, s.overview, s.numId FROM saga AS s WHERE s.numId=(SELECT t.numIdSaga FROM sagaTitle AS t WHERE t.numId={})".format(u2p)
            saga = extractMedias(sql=sql)
            if saga:
                categories += [("Saga", {"action": "MenuFilm", "famille": "sagaListe", "numIdSaga": saga[0][3]})]
        categories += [("Acteurs", {"action": "affActeurs", "u2p": numId, "typM": typMedia}),\
                ("Similaires", {"action": "suggest", "u2p": numId, "typ": "Similaires", "typM": typMedia}), ("Recommandations", {"action": "suggest", "u2p": numId, "typ": "Recommendations", "typM": typMedia})]
        """

        #liste lastview
        if __addon__.getSetting("bookonline") != "false":
            listeView = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=movie" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            listeView = [int(x) for x in listeView]
        else:
            listeView = list(widget.extractIdInVu(t="movies"))
        if int(numId) in listeView:
            categories.append(("Retirer Last/View", {"action": "supView", "u2p": numId, "typM": "movies"}))


        #liste favs
        if __addon__.getSetting("bookonline") != "false":
            listeM = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=movies" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            listeM = [int(x) for x in listeM]
        else:
            listeM = list(widget.extractFavs(t="movies"))
        if int(numId) in listeM:
            categories.append(("Retirer fav's-HK", {"action": "fav", "mode": "sup", "u2p": numId, "typM": "movies"}))
        else:
            categories.append(("Ajouter fav's-HK", {"action": "fav", "mode": "ajout", "u2p": numId, "typM": "movies"}))

        #fenetre information
        categories.append(("Fenêtre Information", {"action": "feninfo", "u2p": numId, "typM": "movies", "title": title}))

        for cat in categories:
            if "Saga" in cat[0] and cat[1]["action"] == "MenuFilm":
                lFinale = [saga[0][0], saga[0][2], year, genre, backdrop, popu, numId, saga[0][1]]
            else:
                lFinale = [title, overview, year, genre, backdrop, popu, numId, poster]
            media = Media("menu", *lFinale)
            media.typeMedia = typMedia

            addDirectoryMenu(cat[0], isFolder=True, parameters=cat[1], media=media)
        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)
    return

def addDirectoryMenu(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=name)
    updateInfoTagVideo(li,media,False,False,False,False,False)
    if "Saison" in name:
        commands = []
        commands.append(('[COLOR yellow]Gestion Vus/Non-Vus[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=vuNonVu&saison=%d&u2p=%s&refresh=1)' %(media.saison, media.numId)))
        li.addContextMenuItems(commands)
        isWidget = xbmc.getInfoLabel('Container.PluginName')
        if "U2P" not in isWidget:
            li.setProperty('widgetEpisodes', 'true')
            li.setProperty('vus', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=vuNonVu&saison=%d&u2p=%s&refresh=1)' %(media.saison, media.numId))

    li.setArt({'icon': media.backdrop,
                "thumb": media.poster,
                'poster':media.poster,
                'fanart': media.backdrop
                })

    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)


def getEpisodesSaison(numId):
    try:
        if __addon__.getSetting("bookonline") != "false":
            vus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
        else:
            vus =  widget.getVu("tvshow")
    except:
        vus = []
    vus = [("Saison %s" %x.split("-")[1].zfill(2), x.split("-")[2])for x in vus if x.split("-")[0] == str(numId)]
    sql = "SELECT saison, episode FROM tvshowEpisodes WHERE numId={}".format(numId)
    liste = extractMedias(sql=sql)
    notice(liste)
    dictSaisons = {}
    for saison in list(set([x[0] for x in liste])):
        nbTotal = len([x for x in liste if x[0] == saison])
        nbVus = len([x for x in vus if x[0] == saison])
        if nbVus == 0:
            c = "red"
        elif nbVus == nbTotal:
            c = "green"
        else:
            c = "orange"
        dictSaisons[saison] = (c, nbVus, nbTotal)
    return dictSaisons


def detailsTV(params):
    #notice(params)
    #typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    #if not typMedia:
    #    xbmc.executebuiltin("Dialog.Close(busydialog)")
    #    xbmc.sleep(500)
    #    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    #typMedia = params["typM"]
    typMedia = "tvshow"
    numId = params["u2p"]
    u2p = params["u2p"]
    if u2p and numId != "divers":
        if "saison" in params.keys():
            numSaison = params["saison"].zfill(2)
            saisons = ["Saison %s" %numSaison]
        else:
            sql = "SELECT DISTINCT saison FROM tvshowEpisodes WHERE numId={}".format(numId)
            saisons = extractMedias(sql=sql, unique=1)
        dictSaisonsVU = getEpisodesSaison(u2p)
        sql = "SELECT title, overview, year, genre, backdrop, popu, numId, poster, runtime FROM tvshow WHERE numId={}".format(numId)
        liste = extractMedias(sql=sql)
        if liste:
            title, overview, year, genre, backdrop, popu, numId, poster, runtime = liste[0]
        else:
            return False
        try: int(runtime)
        except: runtime = 0
        overview = "%s\nsynopsis: %s \nAnnée: %s\nGenre: %s\nNote: %.2f\nDurée: %d mns" %(title, overview[:150] + "...", year, genre, popu, runtime)
        xbmcplugin.setPluginCategory(__handle__, "Menu")
        xbmcplugin.setContent(__handle__, 'episodes')
        choixsaisons = [("%s [COLOR %s](%d/%d)[/COLOR]" %(x, dictSaisonsVU[x][0], dictSaisonsVU[x][1], dictSaisonsVU[x][2]), {"action": "visuEpisodes", "u2p": numId, "saison": x}) for x in saisons]
        categories = [("[COLOR red]Bande Annonce[/COLOR]", {"action": "ba", "u2p": numId, "typM": typMedia})] + choixsaisons + \
            [("Acteurs", {"action": "affActeurs", "u2p": numId, "typM": typMedia}),\
            ("Similaires", {"action": "suggest", "u2p": numId, "typ": "Similaires","typM": typMedia}), \
            ("Recommandations", {"action": "suggest", "u2p": numId, "typ": "Recommendations", "typM": typMedia})]

        #liste lastview
        if __addon__.getSetting("bookonline") != "false":
            listeView = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=tv" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            listeView = [int(x) for x in listeView]
        else:
            listeView = list(widget.extractIdInVu(t="tvshow"))
        if int(numId) in listeView:
            categories.append(("Retirer Last/View", {"action": "supView", "u2p": numId, "typM": typMedia}))

        #liste favs
        if __addon__.getSetting("bookonline") != "false":
            listeM = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=tvshow" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            listeM = [int(x) for x in listeM]
        else:
            listeM = list(widget.extractFavs(t="tvshow"))
        if int(numId) in listeM:
            categories.append(("Retirer fav's-HK", {"action": "fav", "mode": "sup", "u2p": numId, "typM": "tvshow"}))
        else:
            categories.append(("Ajouter fav's-HK", {"action": "fav", "mode": "ajout", "u2p": numId, "typM": "tvshow"}))
        mdb = TMDB(__keyTMDB__)
        dictSaisons = dict(mdb.serieNumIdSaison(u2p).items())
        notice(dictSaisons)

        for cat in categories:
            lFinale = [title, overview, year, genre, backdrop, popu, numId, poster]
            if "saison" in cat[1].keys():
                numSaison = int(cat[1]["saison"].split(" ")[1])
                try:
                    tab = dictSaisons[numSaison]
                    lFinale = [title, tab[2], year, genre, backdrop, popu, numId, tab[1]]
                    #lFinale = [tab[0], tab[2], year, genre, backdrop, popu, numId, tab[1]]
                except Exception as e:
                    notice(str(e))

            media = Media("menu", *lFinale)
            if "saison" in cat[1].keys():
                media.saison = numSaison
            media.typeMedia = typMedia

            addDirectoryMenu(cat[0], isFolder=True, parameters=cat[1], media=media)
        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def suiteSerie():
    try:
        if __addon__.getSetting("bookonline") != "false":
            listeVus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
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
    for numId, episodeVu in dictSerie.items():
        sql = "SELECT episode, link FROM tvshowEpisodes WHERE numId={}".format(numId)
        episodes = extractMedias(sql=sql)
        episodes = sorted([(int(x[0].split("E")[0][1:] + x[0].split("E")[1].zfill(4)), x[1], x[0]) for x in episodes])
        for (episode, lien, numEpisode) in episodes:
            if episode > episodeVu:
                serie = [numId, "", "", lien]
                sql = "SELECT Title, overview, year, backdrop, popu FROM tvshow WHERE numId={}".format(numId)
                serie += extractMedias(sql=sql)[0]
                serie += [int(numEpisode.split("E")[0][1:]), int(numEpisode.split("E")[1]), 0]
                listeSerie.append(serie)
                notice(serie)
                break
    xbmcplugin.setPluginCategory(__handle__, "Episodes")
    xbmcplugin.setContent(__handle__, 'episodes')
    for l in listeSerie[::-1]:
        media = Media("episode", *l)
        media.typeMedia = "episode"
        media.numId = int(l[0])
        addDirectoryEpisodes("%s ([COLOR white]S%sE%s[/COLOR])" %(media.title, str(media.saison).zfill(2), str(media.episode).zfill(2)), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)


def normalizeNum(num):
    s, e = num.split("E")
    e = "%s%s" %("0" * (4 - len(e)), e)
    return s + "E" + e

def affEpisodes2(params):
    numId = params["u2p"]
    saison = params["saison"]
    typM = "episode"
    xbmcplugin.setPluginCategory(__handle__, "Episodes")
    xbmcplugin.setContent(__handle__, 'episodes')
    sql = "SELECT * FROM tvshowEpisodes WHERE numId={} AND saison='{}'".format(numId, saison)
    liste = extractMedias(sql=sql)
    mdb = TMDB(__keyTMDB__)
    tabEpisodes = mdb.saison(numId, saison.replace("Saison ", ""))
    try:
        if __addon__.getSetting("bookonline") != "false":
            vus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
        else:
            vus =  widget.getVu("tvshow")
    except:
        vus = []
    liste = [(x[0], x[1], normalizeNum(x[2]), x[3]) for x in liste]
    for l in sorted(liste, key=lambda x: x[-2]):
        ep = "%d-%d-%d" %(int(l[0]), int(l[2].split("E")[0].replace("S", "")), int(l[2].split("E")[1]))
        if ep in vus:
            isVu = 1
        else:
            isVu = 0
        try:
            lFinale = list(l) + list([episode for episode in tabEpisodes if int(l[2].split("E")[1]) == episode[-1]][0])
        except:
            lFinale = list(l) + ["Episode", "Pas de synopsis ....", "", "", "", int(saison.replace("Saison ", "")) , int(l[2].split("E")[1])]
        lFinale.append(isVu)
        media = Media("episode", *lFinale)
        media.typeMedia = typM
        #notice(media.vu)
        media.numId = int(numId)
        addDirectoryEpisodes("E%d - %s" %(int(l[2].split("E")[1]), media.title ), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

'''
def affEpisodes(numId, saison):
    typM = "episode"
    xbmcplugin.setPluginCategory(__handle__, "Episodes")
    xbmcplugin.setContent(__handle__, 'episodes')
    sql = "SELECT * FROM tvshowEpisodes WHERE numId={} AND saison='{}'".format(numId, saison)
    liste = extractMedias(sql=sql)
    mdb = TMDB(__keyTMDB__)
    tabEpisodes = mdb.saison(numId, saison.replace("Saison ", ""))
    for l in liste:
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
'''

def addDirectoryEpisodes(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=("%s" %(name)))
    #, "dbid": media.numId + 500000
    #notice(media.episode)
    updateInfoTagVideo(li,media,False,True,False,False,True)
    li.setArt({'icon': media.backdrop,
              "fanart": media.backdrop})
    li.setProperty('IsPlayable', 'true')
    commands = []
    commands.append(('[COLOR yellow]Gestion Vus/Non-Vus[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=vuNonVu&saison=%d&u2p=%s&refresh=1)' %(media.saison, media.numId)))
    li.addContextMenuItems(commands, replaceItems=False)
    isWidget = xbmc.getInfoLabel('Container.PluginName')
    if "U2P" not in isWidget:
        li.setProperty('widgetEpisodes', 'true')
        li.setProperty('vus', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=vuNonVu&saison=%d&u2p=%s&refresh=1)' %(media.saison, media.numId))

    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)


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
    tabLinkIn = [(x.split("#")[0].split("@")[0], x.split("#")[0].split("@")[1]) for x in paramstring]
    #dictResos = cr.extractReso(tabLinkIn[:100])
    dictResos = {}
    for i in range(0, len(tabLinkIn), 100):
        dictResos.update(cr.extractReso(tabLinkIn[i: i + 100]))

    dictResos = {x.split("#")[0].split("@")[1]: dictResos[x.split("#")[0].split("@")[1]] if dictResos[x.split("#")[0].split("@")[1]] else x.split("#")[1] for x in paramstring}
    paramstring = orderLiens(dictResos, paramstring)
    tabNomLien = ["[COLOR %s]#%d[/COLOR]| %s - %.2fGo" %(colorLiens(dictResos[x.split("#")[0].split("@")[1]][0]), i + 1, dictResos[x.split("#")[0].split("@")[1]][0], (int(dictResos[x.split("#")[0].split("@")[1]][1]) / 1000000000.0)) for i, x in enumerate(paramstring)]
    tabRelease = [dictResos[x.split("#")[0].split("@")[1]][2] for i, x in enumerate(paramstring)]
    tabLiens = [(x, paramstring[i], tabRelease[i]) for i, x in enumerate(tabNomLien)]
    #web_pdb.set_trace()
    if "poiss" in params.keys():
        uptobox.affLiens(numId, "movie", tabLiens)
    else:
        affLiens(numId, "movie", tabLiens)


def affLiens(numId, typM, liste):
    xbmcplugin.setPluginCategory(__handle__, "Liens")
    xbmcplugin.setContent(__handle__, 'files')
    try:
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                            FROM movie as m WHERE m.numId={}".format(numId)
        movie = extractMedias(sql=sql)
    except:
        movie = []
    if not movie:
        sql = "SELECT title, overview, year, poster, numId, genres, popu, backdrop, runtime, id FROM filmsPub WHERE numId={}".format(numId)
        movie = createbdhk.extractMedias(sql=sql)
    for l in liste:
        l = list(l)
        l += movie[0]
        media = Media("lien", *l)
        media.typeMedia = typM
        if typM == "movie":
            addDirectoryFilms("%s" %(l[0]), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True, cacheToDisc=True)

def orderLiens(dictResos, paramstring):
    tabLinks = []
    tabLinks2 = []
    taille = 5000000001
    filtre = 0
    if __addon__.getSetting("filtliens") != "false":
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

def getParams(paramstring, u2p=0, saisonIn=1):
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
        paramstring = orderLiens(dictResos, paramstring)
        #notice(paramstring)
        try:
            tabNomLien += ["#%d (%s - %.2fGo)" %(i + 1, dictResos[x.split("#")[0].split("@")[1]][0], (int(dictResos[x.split("#")[0].split("@")[1]][1]) / 1000000000.0)) for i, x in enumerate(paramstring)]
        except:
            tabNomLien += ["#%d (ind)" %(i + 1) for i, x in enumerate(paramstring)]
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
                    result['url'] = paramstring[selected].split("#")[0]
                    reso = dictResos[paramstring[selected].split("#")[0].split("@")[1]][0]
            else:
                result['url'] = paramstring[selected].split("#")[0]
                reso = dictResos[paramstring[selected].split("#")[0].split("@")[1]][0]
        else:
            return

    if typMedia != "movie":
        if u2p:
            gestionBD("update", u2p, title, saisonIn, reso, pos)
        else:
            if title:
                gestionBD("update", idDB, title, saison, reso, pos)

    # debridage
    ApikeyAlldeb = getkeyAlldebrid()
    ApikeyRealdeb = getkeyRealdebrid()
    ApikeyUpto = getkeyUpto()
    validKey = False
    if ApikeyAlldeb:
        erreurs = ["AUTH_MISSING_AGENT", "AUTH_BAD_AGENT", "AUTH_MISSING_APIKEY", "AUTH_BAD_APIKEY"]
        urlDedrid, status = cr.resolveLink(result['url'].split("@")[0], result['url'].split("@")[1], keyAllD=ApikeyAlldeb)
        if status in erreurs:
            validKey = False
            showInfoNotification("Key Alldebrid Out!")
            #addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
            #addon.setSetting(id="keyalldebrid", value="")
        else:
            result['url'] = urlDedrid.strip()
            validKey = True

    if ApikeyRealdeb and not validKey:
        urlDedrid, status = cr.resolveLink(result['url'].split("@")[0], result['url'].split("@")[1], keyRD=ApikeyRealdeb)
        if status == "err":
            showInfoNotification("Key Realdebrid Out!")
            #addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
            #addon.setSetting(id="keyrealdebrid", value="")
        else:
            result['url'] = urlDedrid.strip()
            validKey = True

    if ApikeyUpto and not validKey:
        urlDedrid, status = cr.resolveLink(result['url'].split("@")[0], result['url'].split("@")[1], key=ApikeyUpto)
        result['url'] = urlDedrid.strip()
        if status == 16:
            showInfoNotification("Key Uptobox Out!")
            #addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
            #addon.setSetting(id="keyupto", value="")

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

def delcompte(params):
    link = params["lien"]
    ApikeyUpto = getkeyUpto()
    up = uptobox.Uptobox(ApikeyUpto)
    up.deleteFile(link)
    showInfoNotification("Delete Ok: %s" %link)


def addCompteUpto(params):
    modeUp = __addon__.getSetting("modeadd")
    link = params["lien"]
    ApikeyUpto = getkeyUpto()
    cr = cryptage.Crypt()
    links = link.split("*")
    if len(links) > 1:
        choix = [x.split("#")[1] for x in links]
        dialog = xbmcgui.Dialog()
        d = dialog.select("Que veux tu ajouter?", choix)
        if d != -1:
            link = links[d]
        else:
            return
    else:
        link = links[0]
    link = link.split("#")[0]
    if modeUp == "alias":
        filecode, status = cr.resolveLink(link.split("@")[0], link.split("@")[1], key=ApikeyUpto, addCompte=1)
    else:
        filecode, status = cr.resolveLink(link.split("@")[0], link.split("@")[1], key=ApikeyUpto, addCompte=2)
    showInfoNotification("Upload Ok: %s" %filecode)

'''
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
'''

def loadSimReco2(params):
    numId = params["u2p"]
    recherche =  params["typ"]
    typM = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typM:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typM = xbmc.getInfoLabel('ListItem.DBTYPE')
    if typM == "":
        typM = params["typM"]
    #notice("typ demande " + recherche + " typM" +typM)
    dictTyp = {"tvshow": "tv", "movie": "movie", "episode": "tv"}
    mdb = TMDB(__keyTMDB__)
    if recherche == "Similaires":
        liste = mdb.suggReco(numId, dictTyp[typM], "similar")
    elif recherche == "Recommendations":
        liste = mdb.suggReco(numId, dictTyp[typM], "recommendations")

    if __addon__.getSetting("actifnewpaste")  != "false":
        if typM == "movie":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                FROM filmsPub as m WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
        else:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m\
                 WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
        movies = createbdhk.extractMedias(sql=sql)
    elif __addon__.getSetting("actifhk") != "false":
        if typM == "movie":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                            WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
        else:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id  FROM tvshow as m \
                            WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
        movies = extractMedias(sql=sql)

    affMovies(typM, movies[:-1])

def extractFanart(numId):
    cnx = sqlite3.connect(__repAddon__ + "medias.bd")
    cur = cnx.cursor()
    sql = "SELECT logo, clearart, banner FROM movieFanart WHERE numId={}".format(numId)
    cur.execute(sql)
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    if liste:
        logo, clearart, banner = liste[0]
    else:
        logo, clearart, banner = "", "", ""
    return logo, clearart, banner

def extractMedias(limit=0, offset=1, sql="", unique=0):
    cnx = sqlite3.connect(__repAddon__ + "medias.bd")
    cur = cnx.cursor()
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
    cur.close()
    cnx.close()
    return requete

def affAlldeb():
    choix = [("Magnets", {"action":"magnets", "offset": 0}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Afficher les liens magnets"),
             ("History", {"action":"listeAll", "offset": 0, "typeL": "history"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Afficher les liens recents"),
             ("Sauvegarde", {"action":"listeAll", "offset": 0, "typeL": "links"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Afficher les liens sauvés"),]
    xbmcplugin.setPluginCategory(__handle__, "Menu Alldebrid")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)


def affUpto():
    choix = [("Recherche", {"action":"rechercheUpto", "offset": 0}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "Recherche dans le compte Uptobox\n   --- ATTENTION ---\n c'est sur le nom du fichier!!!"),
            ("News", {"action":"newUpto", "offset": 0}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Afficher les derniéres nouveautés du compte Uptobox"),
            ("Racine", {"action": "loadUpto", "rep": "//", "offset": 0, "typM": "movie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Media a la racine du compte"),
            ("Mon Historique", {"action": "histoupto"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Mon historique.png', "Suivi series, films Uptobox"),]
    xbmcplugin.setPluginCategory(__handle__, "Menu Uptobox")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")

    liste = widget.extractRepUpto()
    if liste:
        for (nom, rep, typMedia) in liste:
            if typMedia == "movie":
                choix.append((nom, {"action": "loadUpto", "rep": rep, "offset": 0, "typM": typMedia}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', typMedia))
            else:
                choix.append((nom, {"action": "loadUptoSerie", "rep": rep, "offset": 0, "typM": typMedia}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', typMedia))

    liste = widget.extractRepUptoPublic()
    if liste:
        for (nom, numHash, folder, typMedia) in liste:
            choix.append((nom, {"action": "loadUptoP", "hash": numHash, "folder": folder, "offset": 0, "typM": typMedia}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', typMedia))

    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def affTmdb():
    liste = widget.extractListTMDB()
    if liste:
        xbmcplugin.setPluginCategory(__handle__, "Menu TMDB")
        addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
        choix = []
        for (nom, typMedia) in liste:
            if typMedia == "movie":
                choix.append((nom, {"action":"MenuFilm", "famille": 'tmdb', "nom": nom}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', typMedia))
            else:
                choix.append((nom, {"action":"MenuSerie", "famille": 'tmdb', "nom": nom}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', typMedia))
        isFolder = True
        for ch in sorted(choix):
            name, parameters, picture, texte = ch
            li = xbmcgui.ListItem(label=name)
            updateMinimalInfoTagVideo(li,name,texte)
            li.setArt({'thumb': picture,
                      'icon': addon.getAddonInfo('icon'),
                      'icon': addon.getAddonInfo('icon'),
                      'fanart': addon.getAddonInfo('fanart')})
            url = sys.argv[0] + '?' + urlencode(parameters)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)


def affPastebin():
    liste = widget.extractListPaste()
    if liste:
        xbmcplugin.setPluginCategory(__handle__, "Menu Liste Pastebin")
        addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
        choix = []
        for (nom, typMedia) in liste:
            if typMedia == "film":
                choix.append((nom, {"action":"MenuFilm", "famille": 'paste', "nom": nom}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', typMedia))
            else:
                choix.append((nom, {"action":"MenuSerie", "famille": 'paste', "nom": nom, "t": typMedia}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', typMedia))
        isFolder = True
        for ch in sorted(choix):
            name, parameters, picture, texte = ch
            li = xbmcgui.ListItem(label=name)
            updateMinimalInfoTagVideo(li,name,texte)
            li.setArt({'thumb': picture,
                      'icon': addon.getAddonInfo('icon'),
                      'icon': addon.getAddonInfo('icon'),
                      'fanart': addon.getAddonInfo('fanart')})
            url = sys.argv[0] + '?' + urlencode(parameters)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def affTrakt():
    xbmcplugin.setPluginCategory(__handle__, "Menu Trakt")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choix = [("Listes", {"action":"MenuTrakt", "liste": "liste"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Listes personnelles"),
    ("Listes Liked", {"action":"MenuTrakt", "liste": "liked"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Listes que tu as aimées et likées"),
    ("Watchlist Film", {"action":"MenuTrakt", "cat": "wmovie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Tes envies de films a voir"),
    ("Watchlist Serie", {"action":"MenuTrakt", "cat": "wshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Tes envies de series a voir"),
    ("Recommendations Film", {"action":"MenuTrakt", "cat": "rmovie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Films pour toi"),
    ("Recommendations Serie", {"action":"MenuTrakt", "cat": "rshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Series pour toi"),
    ]

    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)


def ventilationHK():
    xbmcplugin.setPluginCategory(__handle__, "Menu")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choix = [
    ("Setting", {"action":"setting"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/setting.png', "Reglages U2P"),
    ("Setting Profils", {"action":"affProfils"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/profil.png', "Choix Profils"),
    #("Il est frais mon poisson ....", {"action": "affNewsUpto", "offset": "0"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Dernieres news brut....."),
    ]
    # bd hk
    if __addon__.getSetting("actifhk") != "false":
        choix += [("Films, Docu, concerts....", {"action":"MenuFilm"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/film1.png', "Bibliothéque de films, concerts, spectacles et documentaires"),
        ("Divers....", {"action":"MenuDivers"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Sports, Show TV, FANKAI, etc..."),
        ("Series & Animes", {"action":"MenuSerie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/series1.png', "Bibliothéque séries , animation & animes japonais"),
        ("Audio Book", {"action":"MenuAudio"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/book.png', "Bibliothéque livres audio"),
        ("Ma Recherche", {"action":"affSearch"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "type de recherche dispo"),]

    # cretion bd avec les pastes pastebin
    #if __addon__.getSetting("actiflocal") != "false":
    #    choix += [("Pastes Pastebin", {"action":"pastepastebin"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/pastebin.png', "DATABASE via num paste"),]

    # creation avec repertoires crypté
    if __addon__.getSetting("actifnewpaste") != "false":
        choix += [("Médiathéque hk²", {"action":"menuRepCrypte"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/upto.png', "DATABASE new systéme"),]

    # trakt
    if __addon__.getSetting("traktperso") != "false":
        userPass = [x[1] for x in widget.usersBookmark() if x[0] == __addon__.getSetting("profiltrakt")]
        if ( __addon__.getSetting("bookonline") != "false" and userPass and __addon__.getSetting("bookonline_name") == userPass[0]) or __addon__.getSetting("bookonline") == "false":
            choix.append(("Mon Trakt", {"action":"affTraktPerso"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/trakt.png', "ce qui est lié au compte Trakt perso"))

    # mon contenu uptobox
    if __addon__.getSetting("actifupto") != "false":
        choix.append(("Mon Uptobox", {"action":"affUpto"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/upto.png', "accés à ton compte upto et publique"))

    # liste tmdb
    if __addon__.getSetting("actiftmdb") != "false":
        choix.append(("Mon Movie-DB", {"action":"affTmdb"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/tmdb.png', "listes reconstituées avec TMDB"))

    # liste pastebin d'apres un num de paste depuis hk
    if __addon__.getSetting("actifpastebin") != "false":
        choix.append(("Mon Pastebin", {"action":"affPastebin"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/pastebin.png', "listes reconstituées avec le(s) paste(s)"))

    # mon alldeb
    if __addon__.getSetting("actifalldeb") != "false":
        choix.append(("Mon Alldebrid", {"action":"affAlldeb"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/alldebrid.png', "Accés liens du compte"))

    choix.append(("Mes Bandes Annonces", {"action":"affbaext"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Accés repo special Bande Annonce"))

    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def traktHKventilation():
    trk = TraktHK()
    user = __addon__.getSetting("usertrakt")
    if __addon__.getSetting("actifnewpaste")  != "false":
        sqlMovie = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, (SELECT GROUP_CONCAT(l.link, '*') FROM filmsPubLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                FROM filmsPub as m WHERE m.numId IN ({})"
        sqlTvshow = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genres, m.popu, m.backdrop, m.runtime, m.id FROM seriesPub as m\
                 WHERE m.numId IN ({})"
        fxExtract = createbdhk.extractMedias
    elif __addon__.getSetting("actifhk") != "false":
        sqlMovie = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                            FROM movie as m WHERE m.numId IN ({})"
        sqlTvshow = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                            FROM tvshow as m WHERE m.numId IN ({})"
        fxExtract = extractMedias
    movies = None
    if "cat" in __params__.keys():
        cat = __params__["cat"]
        #===========================================================================================================================================
        if cat == "wmovie":
            tabNumId = trk.getUserWatchlist(user, typM="movies")
            tabNumId = [x for x in tabNumId if x]
            movies = fxExtract(sql=sqlMovie.format(",".join([str(x) for x in tabNumId])))
            typM = "movie"
        #===========================================================================================================================================
        elif cat == "wshow":
            typM = "tvshow"
            tabNumId = trk.getUserWatchlist(user, typM="shows")
            tabNumId = [x for x in tabNumId if x]
            movies = fxExtract(sql=sqlTvshow.format(",".join([str(x) for x in tabNumId])))
        #===========================================================================================================================================
        elif cat == "rmovie":
            tabNumId = trk.recommendations(user, typM="movies")
            tabNumId = [x for x in tabNumId if x]
            movies = fxExtract(sql=sqlMovie.format(",".join([str(x) for x in tabNumId])))
            typM = "movie"
        #===========================================================================================================================================
        elif cat == "rshow":
            typM = "tvshow"
            tabNumId = trk.recommendations(user, typM="shows")
            tabNumId = [x for x in tabNumId if x]
            movies = fxExtract(sql=sqlTvshow.format(",".join([str(x) for x in tabNumId])))

    elif "numliste" in __params__.keys():
        numliste = __params__["numliste"]
        nb =  int(__params__["nb"])
        listeTR = trk.getListId([numliste, nb])
        listeMovies = [liste["movie"]["ids"]["tmdb"] for liste in listeTR if liste["type"] == "movie"]
        listeMovies = [x for x in listeMovies if x]
        listeShows = [liste["show"]["ids"]["tmdb"] for liste in listeTR if liste["type"] == "show"]
        listeShows = [x for x in listeShows if x]
        if listeMovies and listeShows:
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('Listes', 'Cette liste a 2 types de contenu, lequel afficher?', nolabel="Films", yeslabel="Series")
            if not ret:
                typM = "movie"
                movies = fxExtract(sql=sqlMovie.format(",".join([str(x) for x in listeMovies])))
            else:
                typM = "tvshow"
                movies = fxExtract(sql=sqlTvshow.format(",".join([str(x) for x in listeShows])))
        elif listeMovies:
            typM = "movie"
            movies = fxExtract(sql=sqlMovie.format(",".join([str(x) for x in listeMovies])))
        elif listeShows:
            typM = "tvshow"
            movies = fxExtract(sql=sqlTvshow.format(",".join([str(x) for x in listeShows])))

    elif "liste" in __params__.keys():
        if __params__["liste"] == "liste":
            listes = trk.extractListsIdUser(user)
        if __params__["liste"] == "liked":
            listes = trk.getUserListsLikes(user)
        choix = [(k, {"action":"MenuTrakt", "numliste":v[0], "nb": v[1]}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', k) for k, v in list(listes.values())[0].items()]
        addCategorieMedia(choix)

    if movies:
        affMovies(typM, movies)



def diversHK():
    if "groupe" in __params__.keys():
        #title, overview, year, poster, link, numId
        sql = "SELECT title, groupe||' ('||repo||')', '', '', 'divers', '', '', link, '', '' FROM divers WHERE repo='{}' AND groupe='{}' ORDER BY id DESC".format(__params__["repo"].replace("'", "''"), __params__["groupe"].replace("'", "''"))
        movies = extractMedias(sql=sql)
        #notice(movies)
        affMovies("movie", movies)

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
            sql = "SELECT DISTINCT groupe FROM divers WHERE repo='{}' ORDER BY id DESC".format(__params__["repo"].replace("'", "''"))
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuDivers", "repo":__params__["repo"], "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
    else:
        sql = "SELECT DISTINCT repo FROM divers"
        listeRep = extractMedias(sql=sql, unique=1)
        choix = [(x, {"action":"MenuDivers", "repo":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in sorted(listeRep)]
        addCategorieMedia(choix)


def mediasHK(params={}):
    notice("params: " + str(params))
    if params:
        __params__["famille"] = params["famille"]
        __params__["u2p"] = params["u2p"]
        __params__["numIdSaga"] = params["u2p"]

    typM = "movie"
    try:
        offset = int(__params__["offset"])
    except:
        offset = 0
    try:
        limit = int(__params__["limit"])
    except:
        limit = int(getNbMedias())
    orderDefault = getOrderDefault()

    year = datetime.today().year
    lastYear = year - 1

    if "famille" in __params__.keys():
        movies = []
        #====================================================================================================================================================================================
        if __params__["famille"] in ["tmdb"]:
            nom = __params__["nom"]
            listeId = widget.recupTMDB(nom, "movie")
            listeId = listeId[offset:]
            tabMovies = []
            for n in listeId:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
                    if len(tabMovies) == limit:
                        break
            __params__["offset"] = offset
            movies = tabMovies[:]
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["paste"]:
            nom = __params__["nom"]
            listePaste = widget.recupPaste(nom, "film")
            listeId = []
            for paste in listePaste:
                sql = "SELECT numId FROM paste WHERE numPaste='{}' ORDER BY id asc".format(paste)
                listeId += [x[0] for x in extractMedias(sql=sql)]
            listeId = listeId[offset:]
            tabMovies = []
            for n in listeId:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
                    if len(tabMovies) == limit:
                        break
            __params__["offset"] = offset
            movies = tabMovies[:]
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["Last View", "Mon historique"]:
            if __addon__.getSetting("bookonline") != "false":
                liste = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=movie" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            else:
                liste = widget.bdHK(extract=1)
            tabMovies = []
            for n in liste:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
            movies = tabMovies[:]
            #sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
            #        WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            #movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] in ["Fav'S HK", "Mes favoris HK"]:
            if __addon__.getSetting("bookonline") != "false":
                notice("http://%s/requete.php?name=%s&type=favs&media=movies" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
                liste = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=movies" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            else:
                liste = widget.extractFavs("movies")
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            __params__["favs"] = __addon__.getSetting("bookonline_name")
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["Last In", "Derniers Ajouts"]:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id FROM movie as m"\
            + " ORDER BY m.id DESC" + " LIMIT {} OFFSET {}".format(limit, offset)
            __params__["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["#Years/Last In", "Nouveautés par année"]:
            #sql = "SELECT numId FROM movieFamille WHERE famille IN ('#Documentaires', '#Concerts', '#Spectacles')"
            sql = "SELECT numId FROM movieFamille WHERE famille IN (SELECT o.nom FROM movieTypeFamille as o WHERE o.typFamille='out')"
            tabNumId = extractMedias(sql=sql, unique=1)
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId NOT IN ({})  AND m.year!='' AND genre NOT LIKE '%%Documentaire%%' AND genre NOT LIKE '%%Animation%%' ORDER BY ".format(",".join([str(x) for x in tabNumId])) + " year DESC, id DESC"\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
            __params__["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["Nouveautés %d-%d" %(lastYear, year)]:
            #sql = "SELECT numId FROM movieFamille WHERE famille IN ('#Documentaires', '#Concerts', '#Spectacles')"
            sql = "SELECT numId FROM movieFamille WHERE famille IN (SELECT o.nom FROM movieTypeFamille as o WHERE o.typFamille='out')"
            tabNumId = extractMedias(sql=sql, unique=1)
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId NOT IN ({})  AND m.year!=''  AND m.year>={} AND genre NOT LIKE '%%Documentaire%%' AND genre NOT LIKE '%%Animation%%' ORDER BY ".format(",".join([str(x) for x in tabNumId]), lastYear) + " id DESC"\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
            __params__["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["#Notations", "Les mieux notés"]:
            #sql = "SELECT numId FROM movieFamille WHERE famille IN ('#Documentaires', '#Concerts', '#Spectacles')"
            sql = "SELECT numId FROM movieFamille WHERE famille IN (SELECT o.nom FROM movieTypeFamille as o WHERE o.typFamille='out')"
            tabNumId = extractMedias(sql=sql, unique=1)
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId NOT IN ({})  AND m.year!='' AND genre NOT LIKE '%%Documentaire%%' AND genre NOT LIKE '%%Animation%%' AND m.popu>7 AND m.popu<9 AND m.votes>500 ORDER BY ".format(",".join([str(x) for x in tabNumId])) + " m.popu DESC"\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
            __params__["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "cast":
            mdb = TMDB(__keyTMDB__)
            liste = mdb.person(__params__["u2p"])
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Liste Aléatoire":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id  FROM movie as m ORDER BY RANDOM() LIMIT {}".format(getNbMedias())
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Alpha(s)":
            if "alpha" in __params__.keys():
                alpha =  __params__["alpha"]
            else:
                dialog = xbmcgui.Dialog()
                alpha = dialog.input("ex: ram => tous les titres qui commencent par 'ram' \n(astuce le _ remplace tous caractéres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")

            if len(alpha) > 0:
                __params__["alpha"] = alpha
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.title LIKE {} ORDER BY title COLLATE NOCASE ASC".format("'" + str(alpha) + "%'") + " LIMIT {} OFFSET {}".format(limit, offset)
                movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Multi-Tri":
            #sql = "SELECT numId FROM movieFamille WHERE famille IN ('#Documentaires', '#Concerts', '#Spectacles')"
            sql = "SELECT numId FROM movieFamille WHERE famille IN (SELECT o.nom FROM movieTypeFamille as o WHERE o.typFamille='out')"
            tabNumId = extractMedias(sql=sql, unique=1)
            dictTri = {"Année puis Date entrée": "year DESC, id DESC", "Date entrée": "id DESC", "Année puis Ordre Alpha": "year DESC, title COLLATE NOCASE ASC", "Ordre Alpha A-Z": "title COLLATE NOCASE ASC",\
             "Ordre Alpha Z-A": "title COLLATE NOCASE DESC"}
            if "tri" in __params__.keys():
                tri = int(__params__["tri"])
            else:
                dialog = xbmcgui.Dialog()
                tri = dialog.select("Selectionner le tri", list(dictTri.keys()), 0, 0)
            if tri != -1:
                __params__["tri"] = str(tri)
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId NOT IN ({})  AND m.year!='' AND genre NOT LIKE '%%Documentaire%%' ORDER BY ".format(",".join([str(x) for x in tabNumId])) + dictTri[list(dictTri.keys())[tri]]\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
                movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["Search", "Recherche"]:
            dialog = xbmcgui.Dialog()
            d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
            if len(d) > 2:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["Groupes Contrib", "Listes des contributeurs"]:
            sql = "SELECT DISTINCT groupeParent FROM movieGroupe"
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuFilm", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Spécial Widget":
            sql = "SELECT DISTINCT groupeParent FROM movieTrakt"
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuFilm", "trakt": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Mes Widgets":
            #notice(widget.extractListe())
            listeRep = list(widget.extractListe())
            choix = [(x, {"action":"MenuFilm", "widget": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Listes lecture":
            listeRep = list(widget.getListesV("movie"))
            choix = [(x, {"action":"MenuFilm", "listeV": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Listes Trakt":
            listeRep = list(widget.getListesT("movie"))
            listeRep = list(set([x[3] for x in listeRep]))
            choix = [(x, {"action":"MenuFilm", "listeT": x, "typM": "movie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Sagas":
            sql = "SELECT numId, title, overview, poster, poster FROM saga ORDER BY title"
            movies = extractMedias(sql=sql)
            typM = "saga"
        #====================================================================================================================================================================================
        elif __params__["famille"] == "sagaListe":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM movie as m WHERE m.numId IN (SELECT f.numId FROM sagaTitle as f WHERE f.numIdSaga={})".format(__params__["numIdSaga"])
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Année(s)":
            if "an" in __params__.keys():
                an = [int(x) for x in __params__["an"].split(":")]
            else:
                dialog = xbmcgui.Dialog()
                d = dialog.input("Entrer Année => 2010 / Groupe d'années => 2010:2014", type=xbmcgui.INPUT_ALPHANUM)
                if d:
                    an = d.split(":")
            __params__["an"] = ":".join([str(x) for x in an])
            if len(an) == 1:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM movie as m WHERE m.year={}".format(an[0]) + " ORDER BY m.year DESC, m.Title ASC" + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM movie as m WHERE m.year>={} and m.year<={}".format(an[0], an[1]) + " ORDER BY m.year DESC, m.Title ASC" + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Genre(s)":
            mdb = TMDB(__keyTMDB__)
            tabGenre = mdb.getGenre()
            if "genre" in __params__.keys():
                genres = [int(x) for x in __params__["genre"].split("*")]
            else:
                dialog = xbmcgui.Dialog()
                genres = dialog.multiselect("Selectionner le/les genre(s)", tabGenre, preselect=[])
            if genres:
                __params__["genre"] = "*".join([str(x) for x in genres])
                genresOk = " or ".join(["m.genre LIKE '%%%s%%'" %tabGenre[x] for x in genres])
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE " + genresOk + " ORDER BY m.id DESC" + " LIMIT {} OFFSET {}".format(limit, offset)
                movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "genres":
            rechGenre = __params__["typgenre"]
            if '#' in rechGenre:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM movie as m WHERE m.numId IN (SELECT f.numId FROM movieFamille as f WHERE f.famille='{}')".format(rechGenre)\
                    + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                            FROM movie as m WHERE m.genre LIKE '%%{}%%' ORDER BY m.id DESC".format(rechGenre) + " LIMIT {} OFFSET {}".format( limit, offset)
            movies = extractMedias(sql=sql)
        #==================================================================================================================================================================================
        elif __params__["famille"] == "Favoris":
            pass
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["Derniers Ajouts Films", "Les plus populaires TMDB/trakt", "#Film Last/In", "#Best TMDB-TRAKT"]:
            dictCf ={"Derniers Ajouts Films": "#Films Last/In", "Les plus populaires TMDB/trakt": "#Best TMDB-TRAKT", "#Films Last/In": "#Films Last/In", "#Best TMDB-TRAKT": "#Best TMDB-TRAKT"}
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM movie as m WHERE m.numId IN (SELECT f.numId FROM movieFamille as f WHERE f.famille='{}')".format(dictCf[__params__["famille"]])\
                    + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset


        else:
            #ORDER BY m.title COLLATE NOCASE ASC
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                    FROM movie as m WHERE m.numId IN (SELECT f.numId FROM movieFamille as f WHERE f.famille='{}')".format(__params__["famille"])\
                    + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset
            #sorted(movies, key=lambda x: x[-1], reverse=True)
        affMovies(typM, movies, params=__params__)

    if "groupe" in __params__.keys():
        sql = "SELECT  groupeFille FROM movieGroupe WHERE groupeParent='{}'".format(__params__["groupe"].replace("'", "''"))
        listeRep = extractMedias(sql=sql, unique=1)
        if len(listeRep) == 1 or not listeRep:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                            WHERE m.numId IN (SELECT d.numId FROM movieGroupeDetail as d WHERE d.groupe='{}')".format(__params__["groupe"].replace("'", "''"))\
                            + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset
            affMovies(typM, movies, params=__params__)
        else:
            choix = [(x, {"action":"MenuFilm", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)

    elif "listeT" in __params__.keys():
        if "listeTfille" in __params__.keys():
            liste = list(widget.getListesT("movie"))
            liste = [(x[0], x[1], "movie") for x in liste if x[3] == __params__["listeT"] and x[4] == __params__["listeTfille"]][0]
            trk = TraktHK()
            tabNumId = trk.extractList(*liste)
            tabNumId = [x for x in tabNumId if x]
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))
            movies = extractMedias(sql=sql)
            affMovies(typM, movies)
        else:
            listeRep = list(widget.getListesT("movie"))
            listeRep = list(set([x[4] for x in listeRep if x[3] == __params__["listeT"]]))
            choix = [(x, {"action":"MenuFilm", "listeT": __params__["listeT"], "listeTfille": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)


    elif "trakt" in __params__.keys():
        sql = "SELECT  groupeFille FROM movieTrakt WHERE groupeParent='{}'".format(__params__["trakt"].replace("'", "''"))
        listeRep = extractMedias(sql=sql, unique=1)
        if len(listeRep) == 1 or not listeRep:
            if listeRep:
                gr = listeRep[0].replace("'", "''")
            else:
                gr = __params__["trakt"].replace("'", "''")

            tabMovies = []
            sql = "SELECT d.numId FROM movieTraktDetail as d WHERE d.groupe='{}' ORDER BY d.id ASC".format(gr)
            listeNumId = extractMedias(sql=sql, unique=1)
            for n in listeNumId:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
            __params__["offset"] = offset
            affMovies(typM, tabMovies, params=__params__)
            '''
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId), m.backdrop, m.runtime, m.id  FROM movie as m \
                            WHERE m.numId IN (SELECT d.numId FROM movieTraktDetail as d WHERE d.groupe='{}' ORDER BY d.id ASC)".format(__params__["trakt"].replace("'", "''"))\
                            + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset
            affMovies(typM, movies, params=__params__)
            '''

        else:
            choix = [(x, {"action":"MenuFilm", "trakt": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)

    elif "widget" in __params__.keys():
        sql = widget.getListe(__params__["widget"])
        movies = extractMedias(sql=sql)
        affMovies(typM, movies)

    elif "listeV" in __params__.keys():
        tabNumId = widget.getListesVdetail(__params__["listeV"], "movie")
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
        __params__["offset"] = offset
        movies = extractMedias(sql=sql)
        affMovies(typM, movies)

    elif "typfamille" in __params__.keys():
        sql = "SELECT nom FROM movieTypeFamille WHERE typFamille='{}'".format(__params__["typfamille"])
        listeRepData = extractMedias(sql=sql, unique=1)
        choix = [(x, {"action":"MenuFilm", "famille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in listeRepData]
        addCategorieMedia(choix)

    else:
        listeRep = ["Derniers Ajouts", "Derniers Ajouts Films", "Nouveautés par année", "Nouveautés %d-%d" %(lastYear, year), "Les mieux notés", "Les plus populaires TMDB/trakt", "Mon historique", "Mes favoris HK",\
            "Listes des contributeurs", "Sagas", "Liste Aléatoire", "Spécial Widget", "Mes Widgets", "Listes lecture", "Listes Trakt"]
        sql = "SELECT DISTINCT typFamille FROM movieTypeFamille"
        listeRepData = [x for x in extractMedias(sql=sql, unique=1) if x not in ["filtre", "genre", "out"]]
        choix = [(x, {"action":"MenuFilm", "famille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in listeRep]
        choix += [(x, {"action":"MenuFilm", "typfamille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in listeRepData]
        choix.append(("Filtres", {"action":"filtres", "typM": "movie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Filtres.png', "Filtres"))
        choix.append(("Genres", {"action":"genres", "typM": "movie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Genres"))
        addCategorieMedia(choix)



def seriesHK():
    typM = "tvshow"
    try:
        offset = int(__params__["offset"])
    except:
        offset = 0
    try:
        limit = int(__params__["limit"])
    except:
        limit = int(getNbMedias())

    orderDefault = getOrderDefault()

    xbmcgui.Window(10000).setProperty('nomFenetre', '')

    if "famille" in __params__.keys():
        movies = []
        #====================================================================================================================================================================================
        if __params__["famille"] in ["tmdb"]:
            nom = __params__["nom"]
            listeId = widget.recupTMDB(nom, "tv")
            listeId = listeId[offset:]
            tabMovies = []
            for n in listeId:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
                    if len(tabMovies) == limit:
                        break
            __params__["offset"] = offset
            movies = tabMovies[:]
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["paste"]:
            nom = __params__["nom"]
            t = __params__["t"]
            listePaste = widget.recupPaste(nom, t)
            listeId = []
            for paste in listePaste:
                sql = "SELECT numId FROM paste WHERE numPaste='{}' ORDER BY id asc".format(paste)
                listeId += [x[0] for x in extractMedias(sql=sql)]
            listeId = listeId[offset:]
            tabMovies = []
            for n in listeId:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
                    if len(tabMovies) == limit:
                        break
            __params__["offset"] = offset
            movies = tabMovies[:]
        #===============================================================================================================================================================================
        elif __params__["famille"] in ["Last View", "Mon historique"]:
            if __addon__.getSetting("bookonline") != "false":
                liste = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=tv" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            else:
                liste = widget.bdHK(extract=1, typM="tvshow")
            tabMovies = []
            for n in liste:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
            movies = tabMovies[:]
            #sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m \
            #        WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            #movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] in ["Fav'S HK", "Mes favoris HK"]:
            if __addon__.getSetting("bookonline") != "false":
                liste = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=tvshow" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name")))
            else:
                liste = widget.extractFavs("tvshow")
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m \
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            __params__["favs"] = __addon__.getSetting("bookonline_name")
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Mes Widgets":
            #notice(widget.extractListe("serie"))
            listeRep = list(widget.extractListe("serie"))
            choix = [(x, {"action":"MenuSerie", "widget": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Listes lecture":
            listeRep = list(widget.getListesV("tvshow"))
            choix = [(x, {"action":"MenuSerie", "listeV": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #===============================================================================================================================================================================
        elif __params__["famille"] in ["Last In", "Derniers Ajouts"]:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m ORDER BY m.id DESC"\
            + " LIMIT {} OFFSET {}".format(limit, offset)
            __params__["offset"] = offset
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] in ["#Years/Last In", "Nouveautés par année"]:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE m.genre NOT LIKE '%%Documentaire%%' AND m.genre NOT LIKE '%%Animation%%' AND m.genre NOT LIKE '%%Kids%%' ORDER BY " +  " year DESC, id DESC"\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
            __params__["offset"] = offset
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] == "Liste Aléatoire":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m ORDER BY RANDOM() LIMIT 200 "
            movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "cast":
            mdb = TMDB(__keyTMDB__)
            liste = mdb.person(__params__["u2p"], typM="tvshow")
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m\
                    WHERE m.numId IN ({})".format(",".join([str(x) for x in liste]))
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] == "Alpha(s)":
            if "alpha" in __params__.keys():
                alpha =  __params__["alpha"]
            else:
                dialog = xbmcgui.Dialog()
                alpha = dialog.input("ex: ram => tous les titres qui commencent par 'ram' \n(astuce le _ remplace tous caractéres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
            if len(alpha) > 0:
                __params__["alpha"] = alpha
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE m.title LIKE {} ORDER BY title COLLATE NOCASE ASC".format("'" + str(alpha) + "%'")\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
                movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"]  in ["Search", "Recherche"]:
            dialog = xbmcgui.Dialog()
            d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
            if len(d) > 2:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
                movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] == "Multi-Tri":
            dialog = xbmcgui.Dialog()
            dictTri = {"Année puis Date entrée": "year DESC, id DESC", "Date entrée": "id DESC", "Année puis Ordre Alpha": "year DESC, title COLLATE NOCASE ASC", "Ordre Alpha A-Z": "title COLLATE NOCASE ASC",\
             "Ordre Alpha Z-A": "title COLLATE NOCASE DESC"}
            if "tri" in __params__.keys():
                tri = int(__params__["tri"])
            else:
                dialog = xbmcgui.Dialog()
                tri = dialog.select("Selectionner le tri", list(dictTri.keys()), 0, 0)
            if tri != -1:
                __params__["tri"] = str(tri)
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE m.genre NOT LIKE '%%Documentaire%%' ORDER BY " + dictTri[list(dictTri.keys())[tri]]\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
                movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] == "Année(s)":
            if "an" in __params__.keys():
                an = [int(x) for x in __params__["an"].split(":")]
            else:
                dialog = xbmcgui.Dialog()
                d = dialog.input("Entrer Année => 2010 / Groupe d'années => 2010:2014", type=xbmcgui.INPUT_ALPHANUM)
                if d:
                    an = d.split(":")
            __params__["an"] = ":".join([str(x) for x in an])
            if len(an) == 1:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                    FROM tvshow as m WHERE m.year={}".format(an[0]) + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                    FROM tvshow as m WHERE m.year>={} and m.year<={}".format(an[0], an[1]) + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] == "Genre(s)":
            mdb = TMDB(__keyTMDB__)
            tabGenre = mdb.getGenre(typM="tv")
            if "genre" in __params__.keys():
                genres = [int(x) for x in __params__["genre"].split("*")]
            else:
                dialog = xbmcgui.Dialog()
                genres = dialog.multiselect("Selectionner le/les genre(s)", tabGenre, preselect=[])
            if genres:
                __params__["genre"] = "*".join([str(x) for x in genres])
                genresOk = " or ".join(["m.genre LIKE '%%%s%%'" %tabGenre[x] for x in genres])
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE " + genresOk + " LIMIT {} OFFSET {}".format(limit, offset)
                movies = extractMedias(sql=sql)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "genres":
            rechGenre = __params__["typgenre"]
            if '#' in rechGenre:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                    FROM tvshow as m WHERE m.numId IN (SELECT f.numId FROM tvshowFamille as f WHERE f.famille='{}')".format(rechGenre)\
                    + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            else:
                sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                            FROM tvshow as m WHERE m.genre LIKE '%%{}%%' ORDER BY m.id DESC".format(rechGenre) + " LIMIT {} OFFSET {}".format( limit, offset)
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] == "#Documentaires":
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE m.genre like '%%Documentaire%%'" \
                        + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            __params__["offset"] = offset
            movies = extractMedias(sql=sql)
        #===============================================================================================================================================================================
        elif __params__["famille"] in ["Groupes Contrib", "Listes des contributeurs"]:
            sql = "SELECT DISTINCT groupeParent FROM tvshowGroupe"
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuSerie", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Listes Trakt":
            listeRep = list(widget.getListesT("show"))
            listeRep = list(set([x[3] for x in listeRep]))
            choix = [(x, {"action":"MenuSerie", "listeT": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
        #====================================================================================================================================================================================
        elif __params__["famille"] == "Spécial Widget":
            sql = "SELECT DISTINCT groupeParent FROM tvshowTrakt"
            listeRep = extractMedias(sql=sql, unique=1)
            choix = [(x, {"action":"MenuSerie", "trakt": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)

        elif __params__["famille"] in ["Derniers Ajouts Series", "Les plus populaires TMDB/trakt", "#Series", "#Best TMDB-TRAKT"]:
            dictCf ={"Derniers Ajouts Series": "#Series", "Les plus populaires TMDB/trakt": "#Best TMDB-TRAKT", "#Series": "#Series", "#Best TMDB-TRAKT": "#Best TMDB-TRAKT"}
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                    FROM tvshow as m WHERE m.numId IN (SELECT f.numId FROM tvshowFamille as f WHERE f.famille='{}')".format(dictCf[__params__["famille"]])\
                    + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset

        else:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                    FROM tvshow as m WHERE m.numId IN (SELECT f.numId FROM tvshowFamille as f WHERE f.famille='{}')".format(__params__["famille"])\
            + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset
        affMovies(typM, movies, params=__params__)
    #===============================================================================================================================================================================
    if "groupe" in __params__.keys():
        sql = "SELECT  groupeFille FROM tvshowGroupe WHERE groupeParent='{}'".format(__params__["groupe"].replace("'", "''"))
        listeRep = extractMedias(sql=sql, unique=1)
        if len(listeRep) == 1 or not listeRep:
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m \
                            WHERE m.numId IN (SELECT d.numId FROM tvshowGroupeDetail as d WHERE d.groupe='{}')".format(__params__["groupe"].replace("'", "''"))\
                            + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset
            affMovies(typM, movies, params=__params__)
        else:
            choix = [(x, {"action":"MenuSerie", "groupe": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
    #===============================================================================================================================================================================
    elif "listeT" in __params__.keys():
        if "listeTfille" in __params__.keys():
            liste = list(widget.getListesT("show"))
            liste = [(x[0], x[1], "show") for x in liste if x[3] == __params__["listeT"] and x[4] == __params__["listeTfille"]][0]
            trk = TraktHK()
            tabNumId = trk.extractList(*liste)
            tabNumId = [x for x in tabNumId if x]
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))
            movies = extractMedias(sql=sql)
            affMovies(typM, movies)
        else:
            listeRep = list(widget.getListesT("show"))
            listeRep = list(set([x[4] for x in listeRep if x[3] == __params__["listeT"]]))
            choix = [(x, {"action":"MenuSerie", "listeT": __params__["listeT"], "listeTfille": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
    #===============================================================================================================================================================================
    elif "listeV" in __params__.keys():
        tabNumId = widget.getListesVdetail(__params__["listeV"], "tvshow")
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                        FROM tvshow as m WHERE m.numId IN ({})".format(",".join([str(x) for x in tabNumId]))\
                        + " LIMIT {} OFFSET {}".format(limit, offset)
        __params__["offset"] = offset
        movies = extractMedias(sql=sql)
        affMovies(typM, movies)
    #===============================================================================================================================================================================
    elif "trakt" in __params__.keys():
        sql = "SELECT  groupeFille FROM tvshowTrakt WHERE groupeParent='{}'".format(__params__["trakt"].replace("'", "''"))
        listeRep = extractMedias(sql=sql, unique=1)
        if len(listeRep) == 1 or not listeRep:
            if listeRep:
                gr = listeRep[0].replace("'", "''")
            else:
                gr = __params__["trakt"].replace("'", "''")
            tabMovies = []
            sql = "SELECT d.numId FROM tvshowTraktDetail as d WHERE d.groupe='{}' ORDER BY d.id ASC".format(gr)
            listeNumId = extractMedias(sql=sql, unique=1)
            for n in listeNumId:
                if n:
                    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id  FROM tvshow as m \
                                WHERE m.numId={}".format(n)
                    movies = extractMedias(sql=sql)
                    if movies:
                        tabMovies.append(movies[0])
            __params__["offset"] = offset
            affMovies(typM, tabMovies, params=__params__)
            '''
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.id  FROM tvshow as m \
                            WHERE m.numId IN (SELECT d.numId FROM tvshowTraktDetail as d WHERE d.groupe='{}')".format(__params__["trakt"].replace("'", "''"))\
                            + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset
            affMovies(typM, movies, params=__params__)
            '''
        else:
            choix = [(x, {"action":"MenuSerie", "trakt": x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s' %getImageWidget(x), x) for x in sorted(listeRep)]
            addCategorieMedia(choix)
    #===============================================================================================================================================================================
    elif "widget" in __params__.keys():
        sql = widget.getListe(__params__["widget"], "serie")
        movies = extractMedias(sql=sql)
        affMovies(typM, movies)
    #===============================================================================================================================================================================
    elif "typfamille" in __params__.keys():
        sql = "SELECT nom FROM tvshowTypeFamille WHERE typFamille='{}'".format(__params__["typfamille"])
        listeRepData = extractMedias(sql=sql, unique=1)
        choix = [(x, {"action":"MenuSerie", "famille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in listeRepData]
        addCategorieMedia(choix)
    #===============================================================================================================================================================================
    elif "network" in __params__.keys():
        if "namenetwork" in __params__.keys():
            sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                    FROM tvshow as m WHERE m.numId IN (SELECT f.numId FROM tvshowNetworkDetail as f WHERE f.network='{}')".format(__params__["namenetwork"])\
                    + orderDefault + " LIMIT {} OFFSET {}".format(limit, offset)
            movies = extractMedias(sql=sql)
            __params__["offset"] = offset
            #__params__["content"] = "images"
            affMovies(typM, movies, params=__params__)
        else:
            sql = "SELECT network, poster FROM tvshowNetwork"
            listeRepData = extractMedias(sql=sql)
            choix = [(x[0], {"action":"MenuSerie", "network":"1", "namenetwork": x[0]}, "http://image.tmdb.org/t/p/w500%s" %x[1], x[0]) for x in listeRepData]
            addCategorieMedia(choix)
    #===============================================================================================================================================================================
    else:
        #sql = "SELECT DISTINCT famille FROM tvshowFamille"
        #listeRep = extractMedias(sql=sql, unique=1)
        sql = "SELECT DISTINCT typFamille FROM tvshowTypeFamille"
        listeRepData = [x for x in extractMedias(sql=sql, unique=1) if x not in ["filtre", "genre", "out"]]
        listeRep = []
        for cat in ["Derniers Ajouts", "Derniers Ajouts Series", "Nouveautés par année", "Les plus populaires TMDB/trakt", "Mon historique", "Mes favoris HK", "Liste Aléatoire",\
               "Listes lecture", "Listes Trakt", "Listes des contributeurs", "Spécial Widget", "Mes Widgets"]:
            listeRep.append(cat)
        choix = [("On continue....", {"action":"suiteSerie"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Liste des episodes des series en cours....")]
        choix += [(x, {"action":"MenuSerie", "famille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in listeRep]
        choix += [(x, {"action":"MenuSerie", "typfamille":x}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s.png' %x, x) for x in listeRepData]
        choix += [("Diffuseurs", {"action":"MenuSerie", "network":"1"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Diffuseur")]
        choix.append(("Filtres", {"action":"filtres", "typM": "tvshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/Filtres.png', "Filtres"))
        choix.append(("Genres", {"action":"genres", "typM": "tvshow"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', "Genres"))
        addCategorieMedia(choix)

def getImageWidget(x):
    if "Netflix" in x:
        im = "netflix.jpg"
    elif "Prime" in x:
        im = "primevideo.jpg"
    elif "CANAL" in x:
        im = "canalplus.jpg"
    elif "HBO" in x:
        im = "hbomax.jpg"
    elif "Disney" in x:
        im = "disneyplus.jpg"
    elif "Apple" in x:
        im = "appletv.jpg"
    elif "ARTE" in x:
        im = "ARTE.jpg"
    elif "SALTO" in x:
        im = "salto.jpg"
    else:
        im = "groupe.png"
    return im

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

    xbmcplugin.setPluginCategory(__handle__, nomF)
    if content:
        xbmcplugin.setContent(__handle__, content)
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    isFolder = True

    for ch in choix:
        name, parameters, picture, texte = ch
        if texte in dictChoix.keys():
            texte = dictChoix[texte]
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        if "http" not in picture and not os.path.isfile(xbmcvfs.translatePath(picture)):
            picture = 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png'
        li.setArt({'thumb': picture,
                  #'icon':  addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True, cacheToDisc=True)

def filtres(params):
    typM = params["typM"]
    dictChoix = {"Derniers Ajours": "Liste des derniers entrés dans pastebin (nouveautée ou pas)", "Last View": "La liste de médias commencés ou la reprise est possible", "Liste Aléatoire": "Liste de médias sortis au hazard, quand tu ne sais pas quoi regarder",\
         "Search": "ben recherche ..... (astuce le _ remplace n'importe quel caractére ex search => r_m donnera tous les titres qui contiennent ram, rom , rum etc... Interressant pour la recherche simultanées de 'e é è ê'",\
          "Groupes Contrib": "Les groupes classés des conributeurs",\
          "Année(s)": "Recherche par années ex 2010 ou groupe d'années 2010:2013 => tous les medias 2010 2011 2012 2013", "Genre(s)": "vos genres préféres avec le multi choix ex choix sience-fiction et fantatisque => la liste gardera les 2 genres", \
          "Alpha(s)": "liste suivant dont le titre commence pas la lettre choisie ou le debut du mot ex ram donnera tous les titres commencant par ram (astuce le _ remplace n'importe quel caractére"}
    filtres = ["Année(s)" , "Recherche", "Genre(s)", "Alpha(s)", "Multi-Tri"]
    xbmcplugin.setPluginCategory(__handle__, "Choix Filtres")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    isFolder = True
    if typM == "movie":
        sql = "SELECT nom FROM movieTypeFamille WHERE typFamille='filtre'"
        liste = extractMedias(sql=sql)
        liste = sorted([x[0] for x in liste])
        filtres += liste
        choix = [(x, {"action":"MenuFilm", "famille":x, "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in filtres]
    else:
        choix = [(x, {"action":"MenuSerie", "famille":x, "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in filtres]
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        if texte in dictChoix.keys():
            texte = dictChoix[texte]
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def affSearch():
    xbmcplugin.setPluginCategory(__handle__, "Recherches...")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    isFolder = True

    if __addon__.getSetting("actifnewpaste") != "false":
        choix = [("Recherche Films", {"action":"mediasHKFilms", "famille": "Search", "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ("Recherche Series", {"action":"mediasHKSeries", "famille": "Search", "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ("Recherche Globale", {"action": "affGlobalHK2"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ("Recherche Acteurs", {"action": "affSearchCast"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ]

    else:
        choix = [("Recherche Films", {"action":"MenuFilm", "famille": "Search", "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ("Recherche Series", {"action":"MenuSerie", "famille": "Search", "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ("Recherche Globale", {"action":"affGlobal"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ("Recherche Acteurs", {"action":"affSearchCast"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "ben recherche ....."),
            ("Recherche Uptobox", {"action":"rechercheUpto", "offset": 0}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/search.png', "Recherche compte uptobox"),
            ]

    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def affGlobal():
    dictTyp = {"movie": "Film", "tvshow": "Serie"}
    dialog = xbmcgui.Dialog()
    d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
    if len(d) > 2:
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id \
                FROM tvshow as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
        tvshows = extractMedias(sql=sql)
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE normalizeTitle(m.title) LIKE normalizeTitle({}) ORDER BY title COLLATE NOCASE ASC".format("'%" + str(d).replace("'", "''") + "%'")
        movies = extractMedias(sql=sql)

        xbmcplugin.setContent(__handle__, 'movies')
        for typM, medias in [("movie", movies), ("tvshow", tvshows)]:

            try:
                dictLogos, dictArt, dictLogosTMDB = logos(typM)
            except:
                dictLogos, dictArt, dictLogosTMDB = {}, {}, {}
            i = 0
            for i, media in enumerate(medias):
                media = Media(typM, *media[:-1])
                if typM == "movie":
                    urlFanart = "http://assets.fanart.tv/fanart/movie/"
                else:
                    urlFanart = "http://assets.fanart.tv/fanart/tv/"
                if int(media.numId) in dictLogos.keys():
                        media.clearlogo = urlFanart + dictLogos[int(media.numId)]
                else:
                    if int(media.numId) in dictLogosTMDB.keys():
                        media.clearlogo = "http://image.tmdb.org/t/p/w300"  + dictLogosTMDB[int(media.numId)]
                    else:
                        media.clearlogo = ""
                if int(media.numId) in dictArt.keys():
                    media.clearart = urlFanart + dictArt[int(media.numId)]
                else:
                    media.clearart = ""
                media.title = "%s (%s)" %(media.title, dictTyp[typM])
                if typM == "movie":
                    ok = addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": "detailM", "lien": media.link, "u2p": media.numId}, media=media)
                else:
                    ok = addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": "detailT", "lien": media.link, "u2p": media.numId}, media=media)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        #xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS, labelMask="Page Suivante")
        if i == (int(getNbMedias()) -1):
            addDirNext(params)

        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True, cacheToDisc=True)

def genres(params):
    typM = params["typM"]
    xbmcplugin.setPluginCategory(__handle__, "Choix Genres")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    isFolder = True
    if typM == "movie":
        mdb = TMDB(__keyTMDB__)
        tabGenre = mdb.getGenre()
        sql = "SELECT nom FROM movieTypeFamille WHERE typFamille='genre'"
        liste = extractMedias(sql=sql)
        tabGenre += sorted([x[0] for x in liste])
        choix = [(x, {"action":"MenuFilm", "famille": "genres", "typgenre": x, "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in tabGenre]
    else:
        mdb = TMDB(__keyTMDB__)
        tabGenre = mdb.getGenre(typM="tv")
        sql = "SELECT nom FROM tvshowTypeFamille WHERE typFamille='genre'"
        liste = extractMedias(sql=sql)
        tabGenre += sorted([x[0] for x in liste])
        choix = [(x, {"action":"MenuSerie", "famille": "genres", "typgenre": x, "offset": 0, "limit": int(getNbMedias())}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/groupe.png', x) for x in tabGenre]

    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def affSearchCast(params={}):
    if "nom" in params.keys():
        d = params["nom"].replace("recherche", "")
    else:
        dialog = xbmcgui.Dialog()
        d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
    if len(d) > 2:
        xbmcplugin.setPluginCategory(__handle__, "Acteurs")
        xbmcplugin.setContent(__handle__, 'files')
        mdb = TMDB(__keyTMDB__)
        liste = mdb.searchPerson(d)
        notice(liste)
        for l in liste:
            media = Media("cast", *l)
            media.typeMedia = "movie"
            if __addon__.getSetting("actifnewpaste")  != "false":
                addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action":"mediasHKFilms", "famille": "cast", "u2p": media.numId}, media=media)
            else:
                addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action":"MenuFilm", "famille": "cast", "u2p": media.numId}, media=media)
        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def affCast2(params):
    numId = params["u2p"]
    typM = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typM:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typM = xbmc.getInfoLabel('ListItem.DBTYPE')
    if typM == "":
        typM = params["typM"]
    xbmcplugin.setPluginCategory(__handle__, "Acteurs / Réalisateur")
    xbmcplugin.setContent(__handle__, 'files')
    mdb = TMDB(__keyTMDB__)
    if typM == "movie":
        liste = mdb.castFilm(numId)
        if __addon__.getSetting("actifnewpaste")  != "false":
            menu = "mediasHKFilms"
        elif __addon__.getSetting("actifhk") != "false":
            menu = "MenuFilm"
    else:
        liste = mdb.castSerie(numId)
        if __addon__.getSetting("actifnewpaste")  != "false":
            menu = "mediasHKSeries"
        elif __addon__.getSetting("actifhk") != "false":
            menu = "MenuSerie"
    for l in liste:
        media = Media("cast", *l)
        media.typeMedia = typM
        addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": menu, "famille": "cast", "u2p": media.numId}, media=media)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def addDirNext(params):
    isFolder = True
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    #notice("id addon " + str(addon.getAddonInfo("id")))
    li = xbmcgui.ListItem(label="[COLOR red]Page Suivante[/COLOR]")

    updateEmptyInfoTag(li)
    li.setArt({
              'thumb': 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/next.png',
              'icon': addon.getAddonInfo('icon'),
              'fanart': addon.getAddonInfo('fanart'),
              })
    #commands = []
    try:
        params["offset"] = str(int(params["offset"]) + int(getNbMedias()))
    except: pass
    url = sys.argv[0] + '?' + urlencode(params)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def audioHKOld():
    movies = extractMedias(sql=sql)
    affMovies("audiobook", movies)

def audioHK():
    typM = "audioBook"
    xbmcplugin.setPluginCategory(__handle__, "Livres Audio")
    xbmcplugin.setContent(__handle__, 'movies')
    sql = "SELECT auteur, titre, numId, description, poster, link, '' FROM audioBook ORDER BY id DESC"#auteur ASC, titre ASC "
    movies = extractMedias(sql=sql)
    for movie in movies:
        media = Media("audiobook", *movie)
        media.typeMedia = typM
        addDirectoryEbook("%s" %(media.title), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "typMedia": media.typeMedia}, media=media)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def addDirectoryEbook(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=("%s" %(name)))
    #Suppression du If qui faisait la meme chose...
    updateInfoTagVideo(li,media,False,False,False,False,False)
    li.setArt({'icon': media.backdrop, 'thumb': media.poster,})
    li.setProperty('IsPlayable', 'true')

    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def logos(typM):
    if typM == "movie":
        #clearlogo  clearart fanart
        sql = "SELECT numId, logo, clearart FROM movieFanart"
        logos = extractMedias(sql=sql)
        dictLogos = {x[0]: x[1] for x in logos if x[1]}
        dictArt = {x[0]: x[2] for x in logos if x[2]}
        #clearlogo tmdb
        sql = "SELECT numId, logo FROM movieTMDBlogo"
        logos = extractMedias(sql=sql)
        dictLogosTMDB = {x[0]: x[1] for x in logos}
    else:
        sql = "SELECT numId, logo, clearart FROM tvshowFanart"
        logos = extractMedias(sql=sql)
        dictLogos = {x[0]: x[1] for x in logos if x[1]}
        dictArt = {x[0]: x[2] for x in logos if x[2]}
        #clearlogo tmdb
        sql = "SELECT numId, logo FROM tvshowTMDBlogo"
        logos = extractMedias(sql=sql)
        dictLogosTMDB = {x[0]: x[1] for x in logos}
    return dictLogos, dictArt, dictLogosTMDB

def affMovies(typM, medias, params=""):

    if params and "favs" in params.keys():
        nom = widget.getProfil(params["favs"])
        xbmcplugin.setPluginCategory(__handle__, "Favs: %s" %nom)
    else:
        xbmcplugin.setPluginCategory(__handle__, typM)
    try:
        if medias[0][4] == "divers":
            xbmcplugin.setContent(__handle__, 'files')
        elif typM == "movie":
            xbmcplugin.setContent(__handle__, 'movies')
        else:
            xbmcplugin.setContent(__handle__, 'tvshows')
    except:
        xbmcplugin.setContent(__handle__, 'movies')
    if __addon__.getSetting("actifhk") != "false":
        dictLogos, dictArt, dictLogosTMDB = logos(typM)
    else:
        dictLogos, dictArt, dictLogosTMDB = {}, {}, {}
    i = 0
    for i, media in enumerate(medias):
        try:
            media = Media(typM, *media[:-1])
        except:
            media = Media(typM, *media)
        if typM == "saga":
            addDirectoryFilms(media.title, isFolder=True, parameters={"action":"MenuFilm", "famille": "sagaListe", "numIdSaga": media.numId}, media=media)
        else:

            if media.numId == "divers":
                media.numId = 0
                addDirectoryFilms("%s (%s)" %(media.title, media.year), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId}, media=media)
            else:
                if typM == "movie":
                    urlFanart = "http://assets.fanart.tv/fanart/movie/"
                else:
                    urlFanart = "http://assets.fanart.tv/fanart/tv/"
                if int(media.numId) in dictLogos.keys():
                        media.clearlogo = urlFanart + dictLogos[int(media.numId)]
                else:
                    if int(media.numId) in dictLogosTMDB.keys():
                        media.clearlogo = "http://image.tmdb.org/t/p/w300"  + dictLogosTMDB[int(media.numId)]
                    else:
                        media.clearlogo = ""
                if int(media.numId) in dictArt.keys():
                    media.clearart = urlFanart + dictArt[int(media.numId)]
                else:
                    media.clearart = ""
                if typM == "movie":
                    ok = addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": "detailM", "lien": media.link, "u2p": media.numId}, media=media)
                    '''
                    if __addon__.getSetting("newfen") == "false":
                        ok = addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": "detailM", "lien": media.link, "u2p": media.numId}, media=media)
                    else:
                        ok = addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": "visuFenmovie", "lien": media.link, "u2p": media.numId, 'title': media.title}, media=media)
                    '''
                elif typM == "audiobook":
                    ok = addDirectoryFilms(media.title, isFolder=True, parameters={"action": "play", "lien": media.link, "u2p": media.numId}, media=media)
                else:
                    if __addon__.getSetting("actifnewpaste") != "false":
                        ok = addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": "affSaisonUptofoldercrypt", "u2p": media.numId}, media=media)
                    else:
                        ok = addDirectoryFilms("%s" %(media.title), isFolder=True, parameters={"action": "detailT", "lien": media.link, "u2p": media.numId}, media=media)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    #xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS, labelMask="Page Suivante")
    if i >= (int(getNbMedias())) - 1:
        addDirNext(params)

    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True, cacheToDisc=True)


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
    li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def fenMovie(params):
    #xbmcplugin.setPluginCategory(__handle__, "Choix Pbi2kodi")
    #xbmcplugin.setContent(__handle__, 'files')
    title = params["title"]
    u2p = params["u2p"]
    try:
        links = params["lien"]
    except :
        links = ""

    #dialog = xbmcgui.Dialog()
    #ret = dialog.contextmenu(['Détails Informations HK', 'Lire', "Ajouter Fav's HK", "Retirer LastView"])
    #notice(ret)
    #if ret == 0:
    window = FenFilmDetail(title=title, numId=u2p, links=links)
    # Show the created window.
    window.doModal()
    del window
    #elif ret == 1:
    #    affLiens2({"u2p": u2p, "lien": links})

    #xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True, cacheToDisc=False)



def menuPbi():
    xbmcplugin.setPluginCategory(__handle__, "Choix U2Pplay")
    xbmcplugin.setContent(__handle__, 'files')
    listeChoix = [("01. Médiathéques", {"action":"movies"}, "pastebin.png", "Mediathéque Pastebin"),
                  ("02. Import DataBase", {"action":"bd"}, "strm.png", "Import DATEBASE"),

                  #("03. Création Listes", {"action":"createL"}, "debrid.png", "Création de liste Widget"),
                  #("04. Suppréssion Listes", {"action":"supL"}, "debrid.png", "Suppréssion de liste Widget"),
                  #("05. Création Listes lecture", {"action":"createLV"}, "debrid.png", "Création de liste lecture perso ou favoris"),
                  #("06. Suppréssion Listes lecture", {"action":"suppLV"}, "debrid.png", "Suppréssion de liste lecture perso ou favoris"),
                  #("07. Création Listes Trakt", {"action":"createLT"}, "debrid.png", "Importation et Création liste trakt"),
                  #("08. Suppréssion Listes/Groupe Trakt", {"action":"suppLT"}, "debrid.png", "Suppréssion liste/groupe trakt"),
                  #("09. Création Listes Paste(s)", {"action":"createLP"}, "liste.png", "Création liste avec index paste(s)"),
                  #("10. Suppréssion Listes Paste(s)", {"action":"suppLP"}, "liste.png", "Suppréssion liste avec index paste(s)"),
                  #("11. Création Listes TMDB", {"action":"createLTMDB"}, "liste.png", "Création liste avec numéro TMDB"),
                  #("12. Suppréssion Listes TMDB", {"action":"suppLTMDB"}, "liste.png", "Suppréssion liste TMDB"),
                  #("13. Création Accés Repertoire Uptobox", {"action":"createRUPTO"}, "liste.png", "Création Accés repertoire Uptobox"),
                  #("14. Création Accés Repertoire Publique Uptobox", {"action":"createRUPTOP"}, "liste.png", "Création Accés repertoire Publique Uptobox"),

                  ]

    # mon iptv
    if __addon__.getSetting("iptv") != "false" and vIPTV:
        listeChoix.append(("03. IPTV", {"action":"iptvLoad"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png', "iptv"))

    #strms
    if __addon__.getSetting("actifStrm") != "false" and vIPTV:
        listeChoix.append(("04. Import STRMS", {"action":"strms"}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Création strms via listes perso"))

    listeChoix.append(("20. Import Config", {"action":"impHK"}, "debrid.png", "Importation d'un config prefaite via rentry"))
    for choix in listeChoix:
        addDirectoryItemLocal(choix[0], isFolder=True, parameters=choix[1], picture=choix[2], texte=choix[3])

    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def addDirectoryItemLocal(name, isFolder=True, parameters={}, picture="", texte="" ):
    ''' Add a list item to the XBMC UI.'''
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    li = xbmcgui.ListItem(label=name)

    updateMinimalInfoTagVideo(li,name,texte)

    #Overlay ne dispose de method sur le getVideoInfoTag ...
    #li.setInfo('video', {"title": name, 'plot': texte, 'mediatype': 'video', "overlay": 6})

    #'playcount':0, "status": "Continuing"
    li.setArt({'thumb': 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/%s' %picture,
              'icon': addon.getAddonInfo('icon'),
              #'icon': addon.getAddonInfo('icon'),
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
    selectedApi = dialogApi.select("Choix Debrideurs", choixApi)
    if selectedApi != -1:
        key = addon.getSetting(dictApi[choixApi[selectedApi]][0])
        d = dialogApi.input(dictApi[choixApi[selectedApi]][1], type=xbmcgui.INPUT_ALPHANUM, defaultt=key)
        addon.setSetting(id=dictApi[choixApi[selectedApi]][0], value=d)

def makeStrmsOld(clear=0):

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

def makeStrms(clear=0):
    strmC = Strm(BDMEDIANew)
    strmC.makeStrms()
    showInfoNotification("strms créés!")
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}')

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
    try:
        url = video['url']
        title = video['title']
        li = xbmcgui.ListItem(title, path=url)
        if "episode" in video.keys():
            updateMinimalInfoTagVideo(li,title,None, video['episode'],video['season'])
        else:
            updateMinimalInfoTagVideo(li,title)
    except Exception as e:
        notice("Service.py - createListItemFromVideo::createListItemFromVideo " + str(e))
    return li

def getIDfile(f):
    try:
        cnx = sqlite3.connect(__database__)
        cur = cnx.cursor()
        sql = "SELECT idFile FROM files WHERE strFilename=? AND dateAdded IS NOT NULL"
        cur.execute(sql, (f,))
        return cur.fetchone()[0]
    except Exception as e:
        notice("get infos file " + str(e))



def prepareUpNext(title, numId, saison, episode):
    #notice(episode)
    if __addon__.getSetting("actifnewpaste")  != "false":
        link = uptobox.getLinkUpNext(numId, saison, int(episode) + 1)
    elif __addon__.getSetting("actifhk") != "false":
        sql = "SELECT link FROM tvshowEpisodes \
                WHERE numId={} AND saison='Saison {}' AND episode=='S{}E{}'".format(numId, str(saison).zfill(2), str(saison).zfill(2), str(int(episode) + 1).zfill(2))
        link = extractMedias(sql=sql, unique=1)
    #notice(link)
    next_info = {}
    if link:
        try:
            mdb = TMDB(__keyTMDB__)
            tabEpisodes = mdb.saison(numId, saison)
            #['Épisode 1', 'Maud Bachelet semble vivre une vie parfaite ', '2022-01-10', '/jkV6JVxXIiDujhEyFreyEo5IxUe.jpg', 0.0, 1, 1]
            if [x for x in tabEpisodes if x[-1] > int(episode)]:
                next_info["current_episode"] = [dict([
                    ("episodeid", x[-1]),
                    ("tvshowid", 0),
                    ("title", x[0]),
                    ("art", {
                        'thumb': "http://image.tmdb.org/t/p/w500%s" %x[3],
                        'tvshow.clearart': "",
                        'tvshow.clearlogo': "",
                        'tvshow.fanart': "",
                        'tvshow.landscape': "http://image.tmdb.org/t/p/w500%s" %x[3],
                        'tvshow.poster': '',
                    }),
                    ("season", x[-2]),
                    ("episode", x[-1]),
                    ("showtitle", title),
                    ("plot", x[1]),
                    ("rating", x[-3]), ("firstaired", x[2])]) for x in tabEpisodes if x[-1] == int(episode)][0]
                next_info["next_episode"] = [dict([
                    ("episodeid", x[-1]),
                    ("tvshowid", 0),
                    ("title", x[0]),
                    ("art", {
                        'thumb': "http://image.tmdb.org/t/p/w500%s" %x[3],
                        'tvshow.clearart': "",
                        'tvshow.clearlogo': "",
                        'tvshow.fanart': "",
                        'tvshow.landscape': "http://image.tmdb.org/t/p/w500%s" %x[3],
                        'tvshow.poster': '',
                    }),
                    ("season", x[-2]),
                    ("episode", x[-1]),
                    ("showtitle", title),
                    ("plot", x[1]),
                    ("rating", x[-3]), ("firstaired", x[2])]) for x in tabEpisodes if x[-1] == int(episode) + 1][0]
                #plugin://plugin.video.sendtokodiU2P/?action=playHK&lien=7UM9cgSAc%40yqh47Hp6a6kW%23&u2p=154454

                param = {"u2p": numId, 'action': "playHKEpisode", 'lien': link[0],  "title": title, 'episode': int(episode) + 1, "saison": saison, "typMedia": "episode"}
                urls = link[0].split("#")
                url = sys.argv[0] + '?' + urlencode(param)
                next_info["play_url"] = url
                #next_info["notification_time"] = 70
            #notice(next_info)
            if next_info["next_episode"]:
                notice(upnext_signal("plugin.video.sendtokodiU2P", next_info))
        except: pass

def playEpisode(params):
    if xbmc.Player().isPlaying():
        tt = 0
        for x in range(3):
            tt = xbmc.Player().getTotalTime()
            if tt:
                break
            time.sleep(0.1)
        t = xbmc.Player().getTime()
        if __addon__.getSetting("bookonline") != "false":
            numEpisode = int(params["episode"]) - 1
            widget.pushSite("http://%s/requete.php?name=%s&type=posserie&numid=%s&pos=%.3f&tt=%.3f&saison=%s&episode=%s"\
                 %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], t, tt, params["saison"], str(numEpisode)))
        else:
            widget.bdHK(numId=params["u2p"], pos=t, tt=tt, typM="episode", saison=int(params["saison"]), episode=int(params["episode"]) - 1)
    cr = cryptage.Crypt()
    paramstring = params["lien"].split("*")
    if len(paramstring) > 1:
        dictResos = cr.extractReso([(x.split("#")[0].split("@")[0], x.split("#")[0].split("@")[1]) for x in paramstring])
        dictResos = {x.split("#")[0].split("@")[1]: dictResos[x.split("#")[0].split("@")[1]] if dictResos[x.split("#")[0].split("@")[1]] else x.split("#")[1] for x in paramstring}
        histoReso = gestionBD("getHK", params["u2p"], params["saison"])
        pos = [k for k, v in dictResos.items() if histoReso[0] == v[0]]
        notice(pos)
        if pos:
            link = [x for x in paramstring if pos[0] in x]
            if link:
               # params["lien"] = "*".join(link)
                params["lien"] = link[0]
    param = {"u2p": params["u2p"], 'action': "playHK", 'lien': params["lien"], 'episode': params["episode"], "saison": params["saison"], "typMedia": "episode"}
    playMediaHK(param)

def mepInfos(numId):
    sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m WHERE m.numId={}".format(numId)
    movies = extractMedias(sql=sql)
    media = Media("movie", *movies[0])

    logo, clearart, banner = extractFanart(numId)
    urlFanart = "http://assets.fanart.tv/fanart/movie/"

    li = xbmcgui.ListItem(label=media.title)
    updateInfoTagVideo(li,media,True,False,True,False,False)
    #liz.setPath("plugin://%s/play/%s" % (ADDON.getAddonInfo("id"),urllib.quote(url, safe='')) )
    li.setArt({'icon': media.backdrop,
            'thumb': media.poster,
            'poster': media.poster,
            'clearlogo': urlFanart,
            'fanart': media.backdrop})
    return li

def testCertification(numId, typMedia):
    if __addon__.getSetting("bookonline") != "false":
        try:
            passwd = __addon__.getSetting("bookonline_name")
            certificationUser = widget.getCertification(passwd)
            if certificationUser[0] > 18:
                return False
            certificationCorrect = widget.recupCertif(numId, typMedia)
            if not certificationCorrect:
                if __addon__.getSetting("actifnewpaste")  != "false":
                    if typMedia == "movie":
                        sql = "SELECT certif FROM filmsPub WHERE numId={}".format(numId)
                    else:
                        sql = "SELECT certif FROM seriesPub WHERE numId={}".format(numId)
                    certificationMedia = createbdhk.extractMedias(sql=sql, unique=1)
                elif __addon__.getSetting("actifhk") != "false":
                    if typMedia == "movie":
                        sql = "SELECT certification FROM movieCertification WHERE numId={}".format(numId)
                    else:
                        sql = "SELECT certification FROM tvshowCertification WHERE numId={}".format(numId)
                    certificationMedia = extractMedias(sql=sql, unique=1)
            else:
                certificationMedia = [certificationCorrect]
            if certificationMedia and  isinstance(certificationMedia[0], int):

                if certificationMedia[0] > certificationUser[0]:
                    showInfoNotification("tu es trop jeune .....")
                    return True
            else:
                if certificationUser[1] == 0:
                    if typMedia == "movie":
                        if __addon__.getSetting("actifnewpaste")  != "false":
                            sql2 = "SELECT numId FROM filmsRepos WHERE famille='concert'"
                            concerts = createbdhk.extractMedias(sql=sql2)
                            concerts = [x[0] for x in concerts]
                            if int(numId) in concerts:
                                return False
                        elif __addon__.getSetting("actifhk") != "false":
                            sql2 = "SELECT numId FROM movieFamille WHERE famille='#Concerts'"
                            concerts = extractMedias(sql=sql2)
                            concerts = [x[0] for x in concerts]
                            if int(numId) in concerts:
                                return False
                        if certificationUser[0] > 11:
                            if __addon__.getSetting("actifnewpaste")  != "false":
                                sql2 = "SELECT numId FROM filmsRepos WHERE famille='concert' or famille='spectacle' or famille='docu'"
                                autres = createbdhk.extractMedias(sql=sql2)
                                autres = [x[0] for x in autres]
                                if int(numId) in autres:
                                    return False
                            elif __addon__.getSetting("actifhk") != "false":
                                sql2 = "SELECT numId FROM movieFamille WHERE famille='#Sports' or famille='#Spectacles'"
                                autres = extractMedias(sql=sql2)
                                autres = [x[0] for x in autres]
                                if int(numId) in autres:
                                    return False
                    showInfoNotification("tu es trop jeune .....")
                    return True

            return False
        except:
            return False

def nettHistoDB(bd):
    cnx2 = sqlite3.connect(bd)
    cur2 = cnx2.cursor()
    try:
        cur2.execute("SELECT (SELECT f.strFilename FROM files as f WHERE b.idFile=f.idFile) FROM bookmark as b")
    except: pass
    try:
        [cur2.execute("DELETE FROM files WHERE strFilename=?", (x[0],)) for x in cur2.fetchall() if "playMediaUptobox&" not in x[0]]
    except: pass
    cnx2.commit()
    cur2.close()
    cnx2.close()


def playMediaHK(params):

    typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    if not typMedia:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.sleep(500)
        typMedia = xbmc.getInfoLabel('ListItem.DBTYPE')
    notice(typMedia)
    numId = params["u2p"]
    try:
        typMedia = params["typMedia"]
    except: pass

    #======================================== certification ========================================
    if testCertification(numId, typMedia):
        return
    #======================================  fin certif ============================================
    if typMedia not in ["movie", "audioBook"]:
        if "saison" in params.keys():
            try:
                title = params['title']
            except:
                title = ""
            numEpisode = params['episode']
            saison = params["saison"]
            li = xbmcgui.ListItem()
            media = MediaSp(**{"title": title, "episode": numEpisode, "season": saison})
            updateInfoTagVideo2(li, media)
            #xbmcgui.ListItem().setInfo('video', {"title": title, "episode": numEpisode, "season": saison})
        else:
            title = xbmc.getInfoLabel('ListItem.TVShowTitle')
            saison = xbmc.getInfoLabel('ListItem.Season')
            numEpisode = xbmc.getInfoLabel('ListItem.Episode')
            if not numEpisode and 'episode' in params.keys():
                numEpisode = params['episode']
        #prepareUpNext(title, numId, saison, numEpisode)
    else:
        saison = 1

    result = getParams(params['lien'], u2p=numId, saisonIn=saison)
    #notice(result)
    if result and "url" in result.keys():
        if typMedia not in ["movie", "audioBook"]:
            result["episode"] = numEpisode
            result["season"] = saison
        else:
            result["episode"] = ""
            result["season"] = ""
        url = str(result['url'])
        showInfoNotification("playing title " + result['title'])
        try:
            result['title'] = xbmc.getInfoLabel('ListItem.TITLE')
            listIt = createListItemFromVideo(result)
            if "skin" in params.keys():
                li = mepInfos(params["u2p"])
                xbmc.Player().play(url, li)
            else:
                xbmcplugin.setResolvedUrl(__handle__, True, listitem=listIt)
        except Exception as e:
            notice("playMediaHK - Erreur Play " + str(e))
        threading.Thread(target=gestionThumbnails).start()
        count = 0
        time.sleep(2)
        while not xbmc.Player().isPlaying():
            count = count + 1
            if count >= 20:
                return
            else:
                time.sleep(1)
        trk = actifTrakt()
        if numId != "divers" and str(numId) != "0":
            if typMedia == "movie":
                if __addon__.getSetting("bookonline") != "false":
                    #notice("http://%s/requete.php?name=%s&type=getpos&numid=%s&media=%s" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], typMedia))
                    recupPos = widget.responseSite("http://%s/requete.php?name=%s&type=getpos&numid=%s&media=%s" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], typMedia))
                    if recupPos:
                        seek = float(recupPos[0])
                    else:
                        seek = 0
                else:
                    seek = widget.bdHK(sauve=0, numId=int(numId))
            elif typMedia == "audioBook":
                seek = 0
            else:
                if __addon__.getSetting("bookonline") != "false":
                    recupPos = widget.responseSite("http://%s/requete.php?name=%s&type=getpos&numid=%s&media=%s&saison=%s&episode=%s" \
                        %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], typMedia, saison, numEpisode))
                    if recupPos:
                        seek = float(recupPos[0])
                    else:
                        seek = 0
                else:
                    seek = widget.bdHK(sauve=0, numId=int(numId), typM=typMedia, saison=saison, episode=numEpisode)
        else:
            seek = 0
        if seek > 0:
            dialog = xbmcgui.Dialog()
            resume = dialog.yesno('Play Video', 'Resume last position?')
            #notice(seek)
            if resume:
                notice(xbmc.getInfoLabel('Player.Title'))
                xbmc.Player().seekTime(int(seek))
            else:
                notice("delete")
        okUpNext = True
        tt = xbmc.Player().getTotalTime()
        #web_pdb.set_trace()
        notice("typeMedia " + typMedia)

        # scrobble
        try:
            if trk and numId != "divers" and str(numId) != "0":
                pos = 0.0
                if typMedia == "movie":
                    trk.scrobble(title="", year=0, numId=numId, pos=pos, typM="movie", mode="start")
                else:
                    trk.scrobble(title="", year=0, numId=numId, pos=pos, season=saison, number=numEpisode, typM="show", mode="start")
        except: pass
        t = 0
        while xbmc.Player().isPlaying():
            t = xbmc.Player().getTime()
            #notice(t)
            if tt == 0:
                tt = xbmc.Player().getTotalTime()
            time.sleep(1)
            if t > 10 and okUpNext and typMedia not in ["movie", "audioBook"]:
                try:
                    prepareUpNext(title, numId, saison, numEpisode)
                    okUpNext = False
                except: pass
        if t > 180 and numId != "divers" and str(numId) != "0":
            if typMedia == "movie":
                if __addon__.getSetting("bookonline") != "false":
                    widget.pushSite("http://%s/requete.php?name=%s&type=posmovie&numid=%s&pos=%.3f&tt=%.3f" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], t, tt))
                else:
                    widget.bdHK(numId=numId, pos=t, tt=tt, typM=typMedia)
            elif typMedia == "episode":
                if __addon__.getSetting("bookonline") != "false":
                    requete = "http://%s/requete.php?name=%s&type=posserie&numid=%s&pos=%d&tt=%d&saison=%s&episode=%s"\
                         %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], t, tt, saison, numEpisode)
                    widget.pushSite(requete)
                    if tt and (float(t) / float(tt) * 100.0) > 90.0:
                        #push on "on continue"
                        widget.gestOC(params["u2p"], "ajout")
                        scraperUPTO.extractEpisodesOnContinue()
                        #
                        p = {"name": __addon__.getSetting("bookonline_name"), "type": "vuepisodes", "numid": params["u2p"], "saison": saison, "episodes": numEpisode,"vu": "1"}
                        requete = "http://%s/requete.php" %__addon__.getSetting("bookonline_site") + '?' + urlencode(p)
                        widget.pushSite(requete)
                else:
                    widget.bdHK(numId=numId, pos=t, tt=tt, typM=typMedia, saison=saison, episode=numEpisode)

        #fin scrooble
        try:
            if trk and numId != "divers" and str(numId) != "0" and t :
                try:
                    pos = t / tt * 100.0
                except:
                    pos = 10.0
                if typMedia == "movie":
                    trk.scrobble(title="", year=0, numId=numId, pos=pos, typM="movie", mode="stop")
                else:
                    trk.scrobble(title="", year=0, numId=numId, pos=pos, season=saison, number=numEpisode, typM="show", mode="stop")
        except: pass

        nettHistoDB(__database__)

        if os.path.isfile(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/rskin.txt')) and __addon__.getSetting("rskin"):
            time.sleep(5)
            xbmc.executebuiltin('ReloadSkin')
            time.sleep(0.05)
            os.remove(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/rskin.txt'))

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
    #notice("idFile " + str(idfile))
    #notice(xbmc.getInfoLabel('ListItem.Episode'))
    #notice(xbmc.getInfoLabel('ListItem.TvShowDBID'))
    #notice(xbmc.getInfoLabel('ListItem.PercentPlayed'))
    #notice(xbmc.getInfoLabel('ListItem.EndTimeResume'))
    #notice("fin listem")

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
            notice("playMedia - Erreur Play " + str(e))
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
            #notice(infoTag.getDbId())
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

"""
def mepAutoStart():
    if not os.path.isfile(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/maj.txt")):
        repStart = xbmcvfs.translatePath("special://home/addons/service.autoexec/")
        repFileStart = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/maj/")
        try:
            os.mkdir(repStart)
        except: pass
        for f in os.listdir(repFileStart):
            if not os.path.isfile(xbmcvfs.translatePath("special://home/addons/service.autoexec/%s" %f)):
                xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/maj/%s" %f), xbmcvfs.translatePath("special://home/addons/service.autoexec/%s" %f))
        open(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/maj.txt"), "w")
"""
def mepAutoStart2():
    repStart = xbmcvfs.translatePath("special://home/addons/service.majhk/")
    repFileStart = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/majhk/")
    try:
        os.mkdir(repStart)
    except: pass
    for f in os.listdir(repFileStart):
        xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/majhk/%s" %f), xbmcvfs.translatePath("special://home/addons/service.majhk/%s" %f))
    for f in [x for x in os.listdir(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P")) if x[-4:] == ".pyc"]:
        xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/%s" %f), xbmcvfs.translatePath("special://home/addons/service.majhk/%s" %f))
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "service.majhk", "enabled": true }}')
    showInfoNotification("Mise place service Maj !!")


def mepAutoStart():
    repStart = xbmcvfs.translatePath("special://home/addons/service.autoexec/")
    repFileStart = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/maj/")
    try:
        os.mkdir(repStart)
    except: pass
    for f in os.listdir(repFileStart):
        xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/maj/%s" %f), xbmcvfs.translatePath("special://home/addons/service.autoexec/%s" %f))
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "service.autoexec", "enabled": true }}')
    showInfoNotification("Mise place Maj au Restat Kodi !!")


def patchNextUp():
    xbmcvfs.delete(xbmcvfs.translatePath("special://home/addons/service.upnext/resources/lib/monitor.py"))
    xbmcvfs.delete(xbmcvfs.translatePath("special://home/addons/service.upnext/resources/lib/player.py"))
    xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/nextup/monitor.py"), xbmcvfs.translatePath("special://home/addons/service.upnext/resources/lib/monitor.py"))
    xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/nextup/player.py"), xbmcvfs.translatePath("special://home/addons/service.upnext/resources/lib/player.py"))
    showInfoNotification("Patch ok, redemarrez KODI !!!!")

def majDatabase():
    importDatabase(debug=0, maj=1)

def createFav():
    if not os.path.isfile(os.path.normpath(os.path.join(__repAddon__, "fav.txt"))):
        favBD = '''\n<favourite name="Import DataBase" thumb="special://home/addons/plugin.video.sendtokodiU2P/resources/png/database.png">PlayMedia(&quot;plugin://plugin.video.sendtokodiU2P/?action=bdauto&quot;)</favourite>'''
        favMovies = '''<favourite name="Mediatheque HK" thumb="special://home/addons/plugin.video.sendtokodiU2P/resources/png/movies.png">ActivateWindow(10025,&quot;plugin://plugin.video.sendtokodiU2P/?action=movies&quot;,return)</favourite>'''
        try:
            with io.open(xbmcvfs.translatePath("special://home/userdata/favourites.xml"), "r", encoding="utf-8") as f:
                txFavs = f.read()
            pos = txFavs.find("<favourites>")
            pos += len("<favourites>")
            txDeb = txFavs[:pos]
            txFin = txFavs[pos:]

            if favBD not in txFavs:
                    txDeb += "%s\n" %favBD
            if os.path.isfile(os.path.normpath(os.path.join(__repAddon__, "medias.bd"))) and favMovies not in txFavs:
                    txDeb += favMovies
            with io.open(xbmcvfs.translatePath("special://home/userdata/favourites.xml"), "w", encoding="utf-8") as f:
                f.write(txDeb + txFin)
            open(os.path.normpath(os.path.join(__repAddon__, "fav.txt")), "w")
        except:
            pass
            #txFavs = ""
            #txDeb = "<favourites>"
            #txFin = "\n</favourites>"

def testHKdb():
    cnx = sqlite3.connect(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/medias.bd"))
    cur = cnx.cursor()
    cur.execute("PRAGMA integrity_check")
    result = cur.fetchone()[0]
    cur.close()
    cnx.close()
    return result

def importDatabase(typImport="full", debug=1, maj=0):
    repAddon = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/")
    fDOWN = 0
    tps = time.time()
    a = time.time()
    if typImport == "epg":
        numRecup = __addon__.getSetting("epg")
    elif typImport == "ba":
        numRecup = __addon__.getSetting("numba")
        fDOWN = 1
    else:
        if not __addon__.getSetting("numhk"):
            dialog = xbmcgui.Dialog()
            d = dialog.input("Num DB HK ex:zmdeo", type=xbmcgui.INPUT_ALPHANUM)
            if d:
                __addon__.setSetting("numhk", d)
            else:
                return
        if maj:
            numRecup = __addon__.getSetting("numhk")
        else:
            dictDB = {"HK-autonome": __addon__.getSetting("numhk"), "HK-autonome-forced": __addon__.getSetting("numhk"),
                "skin": __addon__.getSetting("skinhk"), "Epg": __addon__.getSetting("epg")}
            choixDB = sorted(list(dictDB.keys()))

            dialogApi = xbmcgui.Dialog()
            if typImport == "autonome":
                choixDB = [x for x in choixDB if "HK" in x]
            selectedDB = dialogApi.select("Choix DATABASE", choixDB)

            if selectedDB != -1:
                # debridage
                numRecup = dictDB[choixDB[selectedDB]]
                if debug:
                    showInfoNotification("Verif Update")
                if "forced" in choixDB[selectedDB]:
                    fDOWN = 1
            else:
                return

    ApikeyAlldeb, ApikeyRealdeb, ApikeyUpto = getkeyAlldebrid(), getkeyRealdebrid(), getkeyUpto()
    cr = cryptage.Crypt()
    repStrm, _ = cheminOs()
    tx = False
    if numRecup:
        if ApikeyUpto and not tx:
            tx = cr.updateBD(repAddon, key=ApikeyUpto, typkey="upto", numRentry=numRecup, forceDownload=fDOWN)
        if ApikeyAlldeb and not tx:
            tx = cr.updateBD(repAddon, key=ApikeyAlldeb, typkey="alldeb", numRentry=numRecup, forceDownload=fDOWN)
        if ApikeyRealdeb and not tx:
            tx = cr.updateBD(repAddon, key=ApikeyRealdeb, typkey="realdeb", numRentry=numRecup, forceDownload=fDOWN)
    else:
        if ApikeyUpto and not tx:
            tx = cr.updateBD(repAddon, key=ApikeyUpto, typkey="upto", forceDownload=fDOWN)
        if ApikeyAlldeb and not tx:
            tx = cr.updateBD(repAddon, key=ApikeyAlldeb, typkey="alldeb", forceDownload=fDOWN)
        if ApikeyRealdeb and not tx:
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
            try:
                zipObject.extract("MyVideos119-U2P.db", repAddon)
                dbIn = True
            except:
                dbIn = False
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
                    zipObject.extract("epg.bd", xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/'))
                except: pass
                try:
                    zipObject.extract("ba.db", xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/'))
                except: pass
                try:
                    # extract db HK
                    bdOk = False
                    for nbImport in range(3):
                        zipObject.extract("medias.bd", xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/resources/'))
                        time.sleep(0.2)
                        shutil.move(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/medias.bd"), xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/medias.bd"))
                        time.sleep(0.1)
                        if debug:
                            bdOk = True
                            break
                        else:
                            if testHKdb() == "ok":
                                #notice("nombre import: " + str(nbImport + 1))
                                bdOk = True
                                break
                        time.sleep(2)
                    if not bdOk:
                        showInfoNotification('Erreur database corrupt, faite un "Import manuel"')


                except: pass
                for i, f in enumerate(listOfFileNames):
                    nbGroupe = int((i / float(nbFiles)) * 100.0)
                    pDialogBD2.update(nbGroupe, 'U2Pplay', message="verif STRMS")
                    if f in ["fileSources.txt", "sources.xml", "fichierDB.txt"] or f[-4:] in [".xml", ".xsp", ".zip"]:
                        zipObject.extract(f, repAddon)


        pDialogBD2.close()

        if dbIn:
            a = time.time()
            showInfoNotification("Mise en place new database !!!")
            notice("extraction %0.2f" %(time.time() - a))
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
        else:
            xbmcvfs.delete(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/MyVideos119-U2P.zip"))

    else:
        if debug:
            showInfoNotification("Pas d'update")
    if debug:
        showInfoNotification("Durée Update : %d s" %(time.time() - tps))
        gestionThumbnails()

        createFav()
        time.sleep(0.5)
        #xbmc.executebuiltin('ReloadSkin')
    return

def delDATABASE():
    xbmcvfs.copy(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/MyVideos119-U2P.db"), xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/MyVideos119.db"))
    shutil.move(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/MyVideos119.db"), __database__)
    showInfoNotification("DATAbase effacée , redemarrez KODI !!!!")

def supWidg():
    liste = list(widget.extractListe("all"))
    if liste:
        dialog = xbmcgui.Dialog()
        sups = dialog.multiselect("Liste(s) à supprimer", liste, preselect=[])
        if sups:
            listeSup = [liste[x] for x in sups]
            #notice(listeSup)
            widget.supListe(listeSup)
            showInfoNotification("Liste(s) choisie(s) éffacée(s)")


def reloadSkin():
    time.sleep(0.5)
    xbmc.executebuiltin('ReloadSkin')
    return

def actifProfil(params, menu=1):
    passwd = params["passwd"]
    __addon__.setSetting(id="bookonline_name", value=passwd)
    #xbmc.executebuiltin("plugin://plugin.video.sendtokodiU2P/?action=movies',return)")

    if menu:
        ventilationHK()
    else:
        notice("reload skin")
        reloadSkin()

def gestionVuSaison(params):
    if "newhk" in params.keys():
        liste = uptobox.getEpisodesSerie(params["u2p"], params["saison"])
    else:
        sql = "SELECT DISTINCT episode FROM tvshowEpisodes WHERE numId={} and saison='Saison {}'".format(params["u2p"], params["saison"].zfill(2))
        liste = extractMedias(sql=sql, unique=1)
        liste = [(x, int(x.split("E")[1])) for x in liste]
        liste = [x[0] for x in sorted(liste, key=lambda y: y[1])]
    dialog = xbmcgui.Dialog()
    choix = ["Aucun", "Tous", "Tous sauf"] + liste
    selected = dialog.multiselect("Mettre en Vus", choix, preselect=[])
    if selected:
        if 0 in selected:
            listeVu = []
            listeNonVu = liste[:]
        elif 1 in selected:
            listeVu = liste[:]
            listeNonVu = []
        elif 2 in selected:
            listeVu = [x for x in liste if x not in [liste[y - 3] for y in selected if y > 2]]
            listeNonVu = [liste[y - 3] for y in selected if y > 2]
        else:
            listeNonVu = [x for x in liste if x not in [liste[y - 3] for y in selected if y > 2]]
            listeVu = [liste[y - 3] for y in selected if y > 2]
        #trakt
        trk = actifTrakt()
        if trk:
            trk.gestionWatchedHistory(numId=[int(params["u2p"])], season=int(params["saison"]), number=[int(x.split("E")[1]) for x in listeVu], typM="show", mode="add")
            trk.gestionWatchedHistory(numId=[int(params["u2p"])], season=int(params["saison"]), number=[int(x.split("E")[1]) for x in listeNonVu], typM="show", mode="remove")

        if __addon__.getSetting("bookonline") != "false":
            episodes = "*".join([str(int(x.split("E")[1])) for x in listeVu])
            if episodes:
                #notice("http://%s/requete.php?name=%s&type=vuepisodes&numid=%s&saison=%s&episodes=%s&vu=1"\
                #     %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], params["saison"], episodes))
                widget.pushSite("http://%s/requete.php?name=%s&type=vuepisodes&numid=%s&saison=%s&episodes=%s&vu=1"\
                     %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], params["saison"], episodes))
            time.sleep(0.1)
            episodes = "*".join([str(int(x.split("E")[1])) for x in listeNonVu])
            if episodes:
                #notice("http://%s/requete.php?name=%s&type=vuepisodes&numid=%s&saison=%s&episodes=%s&vu=0"\
                #     %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], params["saison"], episodes))
                widget.pushSite("http://%s/requete.php?name=%s&type=vuepisodes&numid=%s&saison=%s&episodes=%s&vu=0"\
                     %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["u2p"], params["saison"], episodes))
        else:
            for l in listeVu:
                episode = int(l.split("E")[1])
                widget.setVu(params["u2p"], int(params["saison"]), episode, 1, typM="tv")

            for l in listeNonVu:
                episode = int(l.split("E")[1])
                widget.setVu(params["u2p"], int(params["saison"]), episode, 0, typM="tv")
        if params["refresh"] == "1":
            xbmc.executebuiltin("Container.Refresh")

def createListeV():
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Listes', 'Quel type de liste ?', nolabel="Films", yeslabel="Series")
    if not ret:
        media = "movie"
    else:
        media = "tvshow"
    d = dialog.input("Nom de la liste", type=xbmcgui.INPUT_ALPHANUM)
    if d:
        widget.createListeV(d, media)
        showInfoNotification("Création liste lecture: %s ok!!" %d)

def createListeT():
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Listes', 'Quel type de liste ?', nolabel="Films", yeslabel="Series")
    if not ret:
        media = "movie"
    else:
        media = "show"
    trk = TraktHK()
    trk.importListes(media)


def createWidg():
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS listes(
      `id`    INTEGER PRIMARY KEY,
      title TEXT,
      sql TEXT,
      type TEXT,
      UNIQUE (title))
        """)
    cnx.commit()

    dialogTuto = xbmcgui.Dialog()
    dialogTuto.textviewer('Tuto', '''1ere fenêtre
tu choisis une liste soit "SERIES ", soit "FILMs"

2eme fenetre
tu choisis le contenu filtré ou pas
filtré => c'est sans les documentaires , les concerts, les spectacles et les animations

3eme fenêtre
FILTRES
cela sert a filtrer la bibliothéque en fonction de critéres
1) Genre(s)
ca te permet de choisir ta liste en fonction du genre
Par exemple tu veux les films horreur, tu selectionnes dans la liste "Horreur"
Tu peux aussi faire du multi-genres exemple: Horreur-Fantastique, même procédure mais tu selectionnes "horreur" et "Fantastique"
Tu valides par "OK

2) Année(s)
tu choisis ta liste avec le critére de la date du médias
Exemple tu veux tous les média de 2021
tu inscris simplement: 2021
si tu veux une liste par plage d'années
Exemple tu veux les medias des années de 2010 à 2019 (une decade)
tu inscris: 2010:2019
et tu valides par "OK"

3) Popularité
c'est un critére de notation, il s'emploie, pour un maximum d'efficacité, avec le critére "Votes" que l'on verra aprés
tu veux tous les medias donc la note est inférieur à 9
tu inscris: <9
tu veux par plage de notation
Exemple tu veux les medias qui ont une note supérieur à 4 et inférieur à 9.5
tu inscris: 4:9.5
On met un . a la place de la ,

4) Votes
c'est le nombre de votant pour obtenir la note "Popularité" vu juste avant
c'est un tandem avec "Popularité"
on va prendre un exemple
Un média peut connu qui recoit 2 votes , 1 à 9.5 et 1 à 10 (c'est plus frequent qu on ne le pense)
Il aura une note de 9.75 qui sera tres tres surfaite....
Pour eviter ce probléme , on indique un nombre de votants minimum
si on a mis en "Popularité" 4:9.5, on ajoute un nombre de votant minimum example de 500, et la on filtre bien les médias peu regardés donc peu notés
2 exemples
    #je veux les films notés entre 3 et 9.5 mais aussi les anciens films (tmdb n'existait pas, donc pas forcément été beaucoup noté)
        Popularité => 3:9.5
        Votes => 200
        200 me permet de filtrer les nanard....
    #je veux les gros blockbusters, bien notés
        Popularité => 6:9.5
        Votes => 10000
        la tu as les top....

5) Langue
tu choisis ta liste en fonction de la langue d'origine
exemple , les medias japonais, tu choisis "ja", Francais "fr" etc..
Dans "u2pplay-tutos" tu as tout le détail des langues => "lang_Liste.pdf"

Voila pour l'explication des Filtres , tu peux les mettre tous ou une partie c'est à ta convenance, tu peux créér et effacer des listes autant de fois que possible.
Entraines-toi , c'est un outil trés interressant et tu verras une fois compris, c'est trés trés simple
et c'est un belge qui te le dit ....

4éme Fenêtre
ORDRE DE TRI
4 choix
Alpha = par ordre alphabétique de A à Z
Date Added = par ordre d'arrivée ou de modification dans la mediathéque , c'est le dernier entré ou modifié qui sera en 1er
Popularity = par ordre de notation du plus grand vers le plus petit
Year = Par ordre d'année du média du plus récent au plus vieux

on peut mettre plusieurs tris, la priorité et l'ordre insertion des tris
en 1 tu choisis year
en 2 popularity
ordre se fera => tous les medias de 2022 classé par ordre de note ensuite 2021 classé par ordre de note etc ...


5éme fenêtre
Nombre Médias
le nombre de médias que va comporter ta liste
Il faut qu'il soit toujours inférieur à la pagination (500 par default)

ps: si ya des fautes, ca tombe bien ce n'est pas un concours d'orthographe...''')

    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Listes', 'Quel type de liste ?', nolabel="Films", yeslabel="Series")
    if not ret:
        media = "film"
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, (SELECT l.link FROM movieLink as l WHERE l.numId=m.numId) , m.backdrop, m.runtime, m.id \
                        FROM movie as m "
        tx1 = 'Films uniquement? (sans animation, documentaire, concert et spectacle)'
        genreMedia = "movie"
    else:
        media = "serie"
        genreMedia = "tv"
        tx1 = 'Series uniquement? (sans animation, documentaire)'
        sql = "SELECT m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id FROM tvshow as m "

    dictFiltre = {}
    tabOrder = []
    dictOrder = {"Alpha": "Title ASC", "Date Added": "id DESC", "Popularity": "popu DESC", "Year": "year DESC", "Date Release": "dateRelease DESC", "Votes": "votes DESC"}

    dialog = xbmcgui.Dialog()
    tc = dialog.yesno('Contenu', tx1)
    if tc:
        if media == "film":
            typContenu = widget.contenuFilm()
        else:
            typContenu = widget.contenuSerie()
    else:
        typContenu = ""
    notice(typContenu)
    ajoutGenre = 1
    while ajoutGenre:
        dialog = xbmcgui.Dialog()
        choix = ["Genre(s)", "Année(s)", "Popularité", "Votes", "Langue"]#, "Resos", "Acteur", "Réalisateur", "Langue"]
        selected = dialog.select("Filtres", choix)
        if selected != -1:
            filtre = choix[selected]
            if "Genre" in filtre:
                dictFiltre[filtre] = widget.genre(__keyTMDB__, genreMedia)
            elif "Ann" in filtre:
                dictFiltre[filtre] = widget.year()
            elif "Popu" in filtre:
                dictFiltre[filtre] = widget.popu()
            elif "Votes" in filtre:
                dictFiltre[filtre] = widget.votes()
            elif "Langue" in filtre:
                if genreMedia == "movie":
                    sqlang = "SELECT DISTINCT lang FROM filmsPub"
                else:
                    sqlang = "SELECT DISTINCT lang FROM seriesPub"
                liste = createbdhk.extractMedias(sql=sqlang, unique=1)
                dictFiltre[filtre] = widget.langue(sorted(liste))
            dialog = xbmcgui.Dialog()
            ajout = dialog.yesno('Filtres', 'Ajout Filtre supplémentaire ?')
            if not ajout:
                while 1:
                    ajoutGenre = 0
                    choix = list(dictOrder.keys())
                    dialog = xbmcgui.Dialog()
                    selected = dialog.select("Choix ordre de tri (par defaut desc sauf Alpha)", choix)
                    if selected != -1:
                        if choix[selected] not in tabOrder:
                            tabOrder.append(choix[selected])
                        dialog = xbmcgui.Dialog()
                        ajout = dialog.yesno('Filtres', 'Ajout ordre supplémentaire ?')
                        if not ajout:
                            #if tabOrder[0] == "Alpha":
                            #    sens = "ASC"
                            #else:
                            #    sens = "DESC"
                            tri = " ORDER BY {}".format(",".join([dictOrder[x] for x in tabOrder]))
                            dialog = xbmcgui.Dialog()
                            d = dialog.numeric(0, 'Nombre Médias')
                            if int(d) == 0:
                                d = "40000"
                            elif int(d) < 25:
                                d = "25"
                            limit = " LIMIT %s" %d
                            sqladd = "WHERE " + typContenu
                            sqladd += " AND ".join([v for k, v in dictFiltre.items()])
                            sqladd += tri
                            sqladd += limit
                            sql +=  sqladd
                            notice(sql)
                            d = dialog.input("Nom de la liste", type=xbmcgui.INPUT_ALPHANUM)
                            if d:
                                if __addon__.getSetting("bookonline") != "false":
                                    site = __addon__.getSetting("bookonline_site")
                                    name = __addon__.getSetting("bookonline_name")
                                    url = "http://{}/requete.php?type=insertlp&name={}&title={}&media={}&sql={}".format(site, name, d, media, quote(sql))
                                    widget.pushSite(url)

                                cur.execute("REPLACE INTO listes (title, sql, type) VALUES (?, ?, ?)", (d, sql, media, ))
                                cnx.commit()
                                showInfoNotification("Création liste: %s ok!!" %d)
                            break


                    else:
                        break
        else:
            break
    cur.close()
    cnx.close()

def createRUPTO():
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Repertoire', 'Quel type de Repertoire?', nolabel="Films", yeslabel="Series")
    if not ret:
        genreMedia = "movie"
    else:
        genreMedia = "tvshow"
    dialog = xbmcgui.Dialog()
    nomRep = dialog.input("Nom du repertoire Upto (ex: //FilmNews)", type=xbmcgui.INPUT_ALPHANUM)
    if nomRep:
        nomListe = dialog.input("Nom Affichage HK ", type=xbmcgui.INPUT_ALPHANUM)
        if nomListe:
            widget.createRepUpto(nomListe, nomRep, genreMedia)

def createRUPTOP():
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Repertoire', 'Quel type de Repertoire?', nolabel="Films", yeslabel="Series")
    if not ret:
        genreMedia = "movie"
    else:
        genreMedia = "tvshow"
    dialog = xbmcgui.Dialog()
    hashRep = dialog.input("HASH repertoire", type=xbmcgui.INPUT_ALPHANUM)
    if hashRep:
        numRep = dialog.numeric(0, 'Numéro Repertoire')
        if numRep:
            nomListe = dialog.input("Nom Affichage HK ", type=xbmcgui.INPUT_ALPHANUM)
            if nomListe:
                widget.createRepUptoPublic(nomListe, hashRep, numRep, genreMedia)


def createLTMDB():
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Listes', 'Quel type de liste ?', nolabel="Films", yeslabel="Series")
    if not ret:
        genreMedia = "movie"
    else:
        genreMedia = "tv"
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Listes', 'Quel type de liste TMDB?', nolabel="Keyword", yeslabel="List")
    if not ret:
        typList = "Keyword"
    else:
        typList = "liste"
    nomListe = dialog.input("Nom de la liste", type=xbmcgui.INPUT_ALPHANUM)
    if nomListe:
            if typList == "Keyword":
                dialog = xbmcgui.Dialog()
                liste = sorted(list(medias.keywords.keys()))
                selected = dialog.select("Choix Keywords", liste)
                if selected != -1:
                    d = medias.keywords[liste[selected]]
                else:
                    d = ""
            else:
                d = dialog.numeric(0, 'Numéro Liste')
            if d:
                mdb = TMDB(__keyTMDB__)
                if typList == "Keyword":
                    listId = [(nomListe, genreMedia, x) for x in  mdb.listKeywords(d, typM=genreMedia)]
                else:
                    listId = [(nomListe, genreMedia, x) for x in  mdb.getList(d)]
                widget.createListTMDB(listId)
                showInfoNotification("Liste TMDB %s créé" %nomListe)



def createListeLP():
    dialog = xbmcgui.Dialog()
    choix = ["anime", "film", "serie"]
    selected = dialog.select("Choix type Repo", choix)
    if selected != -1:
        typRepo = choix[selected]
        dialog = xbmcgui.Dialog()
        d = dialog.input("Nom de la liste", type=xbmcgui.INPUT_ALPHANUM)
        if d:
            sql = "SELECT DISTINCT(numPaste) FROM paste WHERE type='{}'".format(typRepo)
            liste = sorted([x[0] for x in extractMedias(sql=sql)], key=lambda s: s.lower())
            listeRepo = []
            pos = 1
            while 1:
                dialog = xbmcgui.Dialog()
                selected = dialog.select("Choix Num Paste", liste)
                if selected != -1:
                    num = liste[selected]
                    listeRepo.append((d, num, pos, typRepo))
                    pos += 1
                    liste.pop(selected)
                    dialog = xbmcgui.Dialog()
                    ajout = dialog.yesno('Pastes', 'Ajouter un paste?')
                    if not ajout:
                        break
                else:
                    break
    if listeRepo:
        widget.insertPaste(listeRepo)
        showInfoNotification("Repo Pastes %s créé" %d)


def choixSkin():
    try:
        repListes = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/skin/")
        dictRep = {"Config made in %s" %x: [x] for x in os.listdir(repListes)}
        dialogApi = xbmcgui.Dialog()
        choixRep = list(dictRep.keys())
        selectedApi = dialogApi.select("Choix Contrib", choixRep)

        if selectedApi != -1:
            xbmcvfs.delete(xbmcvfs.translatePath("special://home/userdata/addon_data/script.skinshortcuts/"))
            contrib = dictRep[choixRep[selectedApi]][0]
            repConfig = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/skin/%s/" %contrib)
            repDesti = xbmcvfs.translatePath("special://home/userdata/addon_data/")
            filesConfig = os.listdir(repConfig)
            dialog = xbmcgui.Dialog()
            repos = dialog.select("Selectionner la config à installer", [x[:-4].replace("_", " ") for x in filesConfig], 0)
            if repos != -1:
                with zipfile.ZipFile(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/skin/%s/%s" %(contrib, filesConfig[repos])), 'r') as zipObject:
                    zipObject.extractall(repDesti)

            xbmc.sleep(500)
            xbmc.executebuiltin('ReloadSkin')
    except:
        showInfoNotification("Import skin à faire en 1er => import Database => skin ")

def supView(params):
    if __addon__.getSetting("bookonline") != "false":
        widget.pushSite("http://%s/requete.php?name=%s&type=supview&media=%s&numid=%s" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["typM"], params["u2p"]))
    else:
        widget.supView(params["u2p"], params["typM"])
    showInfoNotification("Retrait Last/View ok!!")

def choixProfil(menu=0):
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
    cur = cnx.cursor()

    sql = "SELECT nom, pass FROM users"
    cur.execute(sql)
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    if not menu:
        xbmcplugin.setPluginCategory(__handle__, "Choix Users")
        xbmcplugin.setContent(__handle__, 'files')
        for choix in liste:

            addDirectoryItemLocal(choix[0], isFolder=True, parameters={"action":"actifP", "passwd": choix[1]}, picture="pastebin.png", texte="Profil à activer, mettre en favori pour un accés direct")

        xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)
    else:
        dialog = xbmcgui.Dialog()
        profil = dialog.select("Selectionner le profil à activer", [x[0] for x in liste])
        if profil != -1:
            actifProfil({"passwd": liste[profil][1]}, menu=0)

def suppProfil():
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      pass TEXT,
      UNIQUE (pass))
        """)
    cnx.commit()
    sql = "SELECT nom, pass FROM users"
    cur.execute(sql)
    liste = cur.fetchall()
    dialogApi = xbmcgui.Dialog()
    selected = dialogApi.select("Profil à supprimer", [x[0] for x in liste])
    if selected != -1:
        sql = "DELETE FROM users WHERE nom=? AND pass=?"
        cur.execute(sql, (liste[selected]))
        cnx.commit()
        sql = "DELETE FROM certification WHERE pass=?"
        cur.execute(sql, (liste[selected][1],))
        cnx.commit()
    cur.close()
    cnx.close()

def insertBookmarkHK(nom, passwd, certification, sans, debug=1):
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      pass TEXT,
      UNIQUE (pass))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS certification(
          pass TEXT,
          certification INTEGER,
          sans INTEGER,
          UNIQUE (pass))
            """)
    cnx.commit()
    try:
        sql = "REPLACE INTO users (nom, pass) VALUES (?, ?)"
        cur.execute(sql, (nom, passwd, ))
        cnx.commit()

        sql = "REPLACE INTO certification (pass, certification, sans) VALUES (?, ?, ?)"
        cur.execute(sql, (passwd, certification, sans))
        cnx.commit()

        """
        params = {
            'action': 'actifP',
            'passwd': passwd
        }

        cmd = {
            'jsonrpc': '2.0',
            'method': 'Favourites.AddFavourite',
            'params': {
                'title': nom,
                "thumbnail": xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/resources/png/profil.png"),
                "type":"window",
                "window":"videos",
                "windowparameter": __url__ + '?' + urlencode(params)
            },
            'id': '1'
        }
        xbmc.executeJSONRPC(json.dumps(cmd))
        """
        if debug:
            showInfoNotification("User: %s créé!!" %nom)
    except Exception as e:
        #showInfoNotification(str(e))
        showInfoNotification("ECHEC création User!!")
    cur.close()
    cnx.close()

def importConfigHK():

    tabProfil = []
    dictCertification = {"Familial":1, "10 ans": 12, "12 ans": 14, "16 ans": 17, "18 ans": 25, "10": 12, "12": 14, "16": 17, "18": 25, "familial":1}
    dictSans = {"oui": 1, "non": 0, "Oui": 1, "Non": 0}
    if __addon__.getSetting("rentry"):
        d = __addon__.getSetting("rentry")
        numTable, pos, paste = int(d[0]), int(d[1:3]), d[3:]
        url = "https://rentry.co/%s/raw" %paste
        dictImport = ast.literal_eval(requests.get(url).content.decode())
        for nom, login, certification, autre in dictImport["bookmark"]:
            #tabProfil.append("%s -- %s -- %s -- %s" %(nom, login, certification, autre))
            insertBookmarkHK(nom, login, dictCertification[certification], dictSans[autre], debug=0)
        try:
            if dictImport["keyUpto"]:
                keyUpto = widget.decryptKey(dictImport["keyUpto"], pos, numTable)
                #showInfoNotification(keyUpto)
                status, validite = testUptobox(keyUpto)
                #tabProfil.append("Key Uptobox %s -- %s" % (status, validite))
                __addon__.setSetting(id="keyupto", value=keyUpto)
        except: pass
        try:
            if dictImport["keyAlldeb"]:
                keyAlldeb = widget.decryptKey(dictImport["keyAlldeb"], pos, numTable)
                #showInfoNotification(keyAlldeb)
                status, validite = testAlldebrid(keyAlldeb)
                #tabProfil.append("Key Alldebrid %s -- %s" % (status, validite))
                __addon__.setSetting(id="keyalldebrid", value=keyAlldeb)
        except: pass
        try:
            if dictImport["keyRealdeb"]:
                keyRealdeb = widget.decryptKey(dictImport["keyRealdeb"], pos, numTable)
                tabProfil.append("Key Realdebrid %s" % keyRealdeb)
                __addon__.setSetting(id="keyrealdebrid", value=keyRealdeb)
        except: pass
        try:
            if dictImport["keyTMDB"]:
                keyTMDB = widget.decryptKey(dictImport["TMDB"], pos, numTable)
                tabProfil.append("Key TMDB %s" % keyTMDB)
                __addon__.setSetting(id="keyrealdebrid", value=keyTMDB)
        except: pass
        try:
            if dictImport["client_id"]:
                client_id = widget.decryptKey(dictImport["client_id"], pos, numTable)
                tabProfil.append("Key Trakt Id %s" % client_id)
                __addon__.setSetting(id="clientid", value=client_id)
        except: pass
        try:
            if dictImport["client_secret"]:
                client_secret = widget.decryptKey(dictImport["client_secret"], pos, numTable)
                tabProfil.append("Key Trakt secret %s" % client_secret)
                __addon__.setSetting(id="clientsecret", value=client_secret)
        except: pass

        try:
            if dictImport["iptv"]:
                for fournisseur, macs in dictImport["iptv"].items():
                    fournisseur, nom = fournisseur.split("=")
                    nbCompte = 0
                    for mac in macs:
                        nbCompte += iptv.importCompte(fournisseur.strip(), mac, nom.strip())
                    tabProfil.append("fournisseur %s\nNombre de comptes importés: %d" %(fournisseur, nbCompte))
        except: pass

        try:
            if dictImport["client_secret"]:
                client_secret = widget.decryptKey(dictImport["client_secret"], pos, numTable)
                tabProfil.append("Key Trakt secret %s" % client_secret)
                __addon__.setSetting(id="clientsecret", value=client_secret)
        except: pass
        dialog = xbmcgui.Dialog()
        dialog.textviewer('Config', "\n".join(tabProfil))

def createPass():
    tab = "0123456789AZERTYUIOPMLKJHGFDSQWXVCBN?!azertyuiopmlkjhgfdsqwxcvbn"
    nb = random.randint(10, 20)
    tx = ""
    for i in range(nb):
        tx += tab[random.randint(0, (len(tab) - 1))]
    return tx

def ajoutProfil(initP=0):
    dialog = xbmcgui.Dialog()
    d = dialog.input("Mettre votre pseudo:", type=xbmcgui.INPUT_ALPHANUM)
    if d:
        nom = d
        dialog = xbmcgui.Dialog()
        d = dialog.input("Mettre ton pass (accés à ton bookmark,\nmettre un pass complexe!!!)", createPass(), type=xbmcgui.INPUT_ALPHANUM)
        if d:
            passwd = d
            dictCertification = {"Familial":1, "10 ans": 12, "12 ans": 14, "16 ans": 17, "18 ans": 25}
            choix = list(dictCertification.keys())
            selected = dialog.select("Certification", choix)
            if selected != -1:
                certification = dictCertification[choix[selected]]
                dialog = xbmcgui.Dialog()
                tc = dialog.yesno('Certification', "Autoriser la lecture des titres sans certification ?")
                notice("sans: " + str(tc))
                if tc:
                    sans = 1
                else:
                    sans = 0
                insertBookmarkHK(nom, passwd, certification, sans)
                if initP:
                    dialog = xbmcgui.Dialog()
                    tc = dialog.yesno('Profil', "Veux-tu activer Bookmark en ligne ? (favoris etc...)")

                    if tc:
                        __addon__.setSetting(id="bookonline", value="true")
                        actifProfil({"passwd": passwd}, menu=0)
                    else:
                        __addon__.setSetting(id="bookonline", value="false")

def affProfils():
    liste = widget.usersBookmark()
    xbmcplugin.setPluginCategory(__handle__, "Profils")
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    choix = [(x[0], {"action":"actifP", "passwd": x[1]}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/profil.png', "Click pour activer") for x in liste ]
    isFolder = True
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        updateMinimalInfoTagVideo(li,name,texte)
        li.setArt({'thumb': picture,
                  'icon': addon.getAddonInfo('icon'),
                  'icon': addon.getAddonInfo('icon'),
                  'fanart': addon.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)

def actifTrakt():
    trk = None
    if __addon__.getSetting("traktperso") != "false":
        if __addon__.getSetting("bookonline") != "false":
            userPass = [x[1] for x in widget.usersBookmark() if x[0] == __addon__.getSetting("profiltrakt")]
            if userPass and __addon__.getSetting("bookonline_name") == userPass[0]:
                    trk = TraktHK()
        else:
            trk = TraktHK()
    return trk

def gestionoc(params):
    if params["mode"] == "ajout":
        widget.gestOC(params["u2p"], "ajout")
    else:
        widget.gestOC(params["u2p"], "supp")
    return

def gestionFavHK(params):
    trk = actifTrakt()
    if params["mode"] == "ajout":
        typAjout = "add"
        if __addon__.getSetting("bookonline") != "false":
            widget.pushSite("http://%s/requete.php?name=%s&type=infavs&media=%s&numid=%s" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["typM"], params["u2p"]))
        else:
            widget.ajoutFavs(params["u2p"], params["typM"])
    else:
        typAjout = "remove"
        if __addon__.getSetting("bookonline") != "false":
            widget.pushSite("http://%s/requete.php?name=%s&type=supfavs&media=%s&numid=%s" %(__addon__.getSetting("bookonline_site"), __addon__.getSetting("bookonline_name"), params["typM"], params["u2p"]))
        else:
            widget.supFavs(params["u2p"], params["typM"])
    if trk:
        if params["typM"] == "movies":
            trk.gestionWatchlist(numId=[int(params["u2p"])], typM="movie", mode=typAjout)
        else:
            trk.gestionWatchlist(numId=[int(params["u2p"])], typM="show", mode=typAjout)
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

def testUptobox(key):
    url = 'https://%s/api/user/me?token=' %__addon__.getSetting("extupto") + key
    headers = {'Accept': 'application/json'}
    try:
        data = requests.get(url, headers=headers).json()
        status = data["message"]
        validite = data["data"]["premium_expire"]
    except:
        status = "out"
        validite = ""
    return status, validite

def testAlldebrid(key):
    url = 'https://api.alldebrid.com/v4/user?agent=myAppName&apikey=' + key
    #try:
    data = requests.get(url).json()
    notice(data)
    status = data["status"]
    validate = data["data"]["user"]["premiumUntil"]
    if int(validate) > 0:
        validate = datetime.fromtimestamp(validate)
    else:
        validate = "Validation expirée"
    #except:
    #    status = "out"
    #    validate = False
    return status, validate

def assistant():
    # key debrideurs
    a = 0
    while a < 5:
        ApikeyAlldeb, ApikeyRealdeb, ApikeyUpto = getkeyAlldebrid(), getkeyRealdebrid(), getkeyUpto()
        if not ApikeyUpto and not ApikeyRealdeb and not ApikeyAlldeb:
            dialog = xbmcgui.Dialog()
            resume = dialog.yesno('Config', 'As-tu un numéro de config?')
            if resume:
                dialog = xbmcgui.Dialog()
                d = dialog.input("Num config", type=xbmcgui.INPUT_ALPHANUM)
                if d:
                    __addon__.setSetting("rentry", d)
                    importConfigHK()
            else:
                configKeysApi()
        else:
            keyOk = False
            if ApikeyAlldeb:
                ok, validite = testAlldebrid(ApikeyAlldeb)
                if ok == "success":
                    keyOk = True
                    showInfoNotification("Key Alldebrid Ok! expire: %s" %validite)
                else:
                    showInfoNotification("Key Alldebrid out!")
                    __addon__.setSetting(id="keyalldebrid", value="")
            if ApikeyUpto:
                ok, validite = testUptobox(ApikeyUpto)
                if ok == "Success":
                    keyOk = True
                    showInfoNotification("Key Upto ok! expire: %s" %validite)
                else:
                    showInfoNotification("Key Upto out!")
                    __addon__.setSetting(id="keyupto", value="")
            if ApikeyRealdeb:
                keyOk = True
            if keyOk:
                break
        a += 1

    if keyOk:
        if not __addon__.getSetting("numhk"):
            dialog = xbmcgui.Dialog()
            d = dialog.input("Num DB HK ex:zmdeo", type=xbmcgui.INPUT_ALPHANUM)
            if d:
                __addon__.setSetting("numhk", d)
            else:
                return False
        importDatabase("autonome")
        return True
    else:
        return False

def vuMovieTrakt(params):
    numId = int(params["u2p"])
    trk = actifTrakt()
    trk.gestionWatchedHistory(numId=[numId], typM="movie", mode="add")

def correctCertif(params):
    widget.correctCertif(params["u2p"], params["typM"])

def newUptoPublic(params):
    folder = __addon__.getSetting("poissFolder")
    hsh = __addon__.getSetting("poissHash")
    sql = "SELECT DISTINCT typM FROM repos WHERE repo='poissonnerie' ORDER BY typM"
    try:
        tabFiles = uptobox.extractMedias(sql=sql, unique=1)
    except:
        tabFiles = []
    xbmcplugin.setPluginCategory(__handle__, "Choix U2Pplay")
    xbmcplugin.setContent(__handle__, 'files')
    listeChoix = [(x, {"action":"AffCatPoiss", "offset":"0", "typM": x}, "liste.png", "Catégories %s de ma poissonerie !!"%x) for x in tabFiles]
    listeChoix.append(("Update ou création", {"action":"insertrepo", "repo":"poissonnerie", "folder": folder, "hash": hsh}, "liste.png", "Création ou update de ma poissonnerie!!"))
    listeChoix.append(("Recherche", {"action":"recherepo", "repo":"poissonnerie"}, "liste.png", "Recherche dans ma poissonnerie!!"))
    listeChoix.append(("Vider la poissonnerie", {"action":"reinitPoissonnerie"}, "liste.png", "Vider la poissonnerie!!"))
    for choix in listeChoix:
        addDirectoryItemLocal(choix[0], isFolder=True, parameters=choix[1], picture=choix[2], texte=choix[3])

    xbmcplugin.endOfDirectory(handle=__handle__, succeeded=True)


def recherRepo(params):
    dialog = xbmcgui.Dialog()
    d = dialog.input("Recherche (mini 3 lettres)", type=xbmcgui.INPUT_ALPHANUM, defaultt="")
    if len(d) > 2:
        sql = "SELECT DISTINCT nom, lien FROM repos WHERE repo='poissonnerie' AND (normalizeTitle(title) LIKE normalizeTitle({}) OR normalizeTitle(nom) LIKE normalizeTitle({}) )  ORDER BY id ASC"\
            .format("'%" + str(d).replace("'", "''") + "%'", "'%" + str(d).replace("'", "''") + "%'")
        tab = uptobox.extractMedias(sql=sql)
        medias = uptobox.ventilationType(tab)
        uptobox.affUptoboxNews("movie", [x[1:]  for x in medias])

def newUptoPublic2(params):
    limit = __addon__.getSetting("nbupto")
    offset = int(params["offset"])
    typM = params["typM"]
    if typM == "film":
        sql = "SELECT DISTINCT numId FROM repos WHERE repo='poissonnerie' AND typM='{}' ORDER BY id ASC LIMIT {} OFFSET {}".format(typM, limit, offset)
        tab = uptobox.extractMedias(sql=sql, unique=1)
        tabFiles = [(x, "*".join(uptobox.extractMedias(sql="SELECT lien FROM repos WHERE repo='poissonnerie' AND typM='{}' AND numId={}".format(typM, x), unique=1))) for x in tab]
        medias = uptobox.getFilmsUptoNews(tabFiles)
        uptobox.affUptoboxNews("movie", [x[1:]  for x in medias], params, cr=1)
    elif typM == "divers":
        sql = "SELECT DISTINCT nom FROM repos WHERE repo='poissonnerie' AND typM='{}' ORDER BY id ASC LIMIT {} OFFSET {}".format(typM, limit, offset)
        tab = uptobox.extractMedias(sql=sql, unique=1)
        tabFiles = [(x, "*".join(uptobox.extractMedias(sql="SELECT lien FROM repos WHERE repo='poissonnerie' AND typM='{}' AND nom='{}'".format(typM, x.replace("'", "''")), unique=1))) for x in tab]
        medias = [(0, x[0], "", 0, "", 0, "", "", x[1], "", 0, 0) for x in tabFiles]
        uptobox.affUptoboxNews("movie", [x[1:]  for x in medias], params, cr=1)
    elif typM == "serie":
        sql = "SELECT DISTINCT numId FROM repos WHERE repo='poissonnerie' AND typM='{}' ORDER BY id ASC LIMIT {} OFFSET {}".format(typM, limit, offset)
        tab = uptobox.extractMedias(sql=sql, unique=1)
        medias = uptobox.getSeriesUptoNews(tab)
        uptobox.affUptoboxNewsSerie("movie", [x[1:]  for x in medias], params,)

def affSaisonUptoPoiss(params):
    numId = params["u2p"]
    sql = "SELECT DISTINCT saison FROM repos WHERE repo='poissonnerie' AND numId={} and typM='serie' ORDER BY saison".format(numId)
    tabFiles = uptobox.extractMedias(sql=sql, unique=1)
    params["tabsaison"] = "*".join([str(x) for x in tabFiles])
    uptobox.loadSaisonsUpto(params)

def visuEpisodesUptoPoiss(params):
    numId = params["u2p"]
    saison = params["saison"]
    sql = "SELECT DISTINCT episode FROM repos WHERE repo='poissonnerie' AND typM='serie' AND saison={} AND numId={} ORDER BY episode".format(saison, numId)
    tab = uptobox.extractMedias(sql=sql, unique=1)
    tabFiles = [(x, "*".join(uptobox.extractMedias(sql="SELECT lien FROM repos WHERE repo='poissonnerie' AND typM='serie' AND numId={} AND saison={} AND episode={} "\
                .format(numId, saison, x), unique=1))) for x in tab]
    if "release" in params.keys():
        uptobox.affEpisodesUptoPoiss(numId, saison, tabFiles, params["release"])
    else:
        uptobox.affEpisodesUptoPoissRelease(numId, saison, tabFiles)

def majHkcron():
    threading.Thread(name="maj", target=scraperUPTO.majHkNewStart).start()



def intmajbann15():
    #init addon
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    #Change valeur
    addon.setSetting(id="intmaj", value="15")
    addon.setSetting(id="delaimaj", value="0")
    #recup valeur intmaj
    intmaj = addon.getSetting("intmaj")
    #recup delaimaj
    delaimaj = addon.getSetting("delaimaj")
    # si vide
    if intmaj:
        dialog = xbmcgui.Dialog()
        d = dialog.input("Intervalle des Maj en minutes: [0|5|15|30|45|60|120|240]", type=xbmcgui.INPUT_ALPHANUM)
        if d:
            intmaj = d
            addon.setSetting(id="intmaj", value=d.strip())
        else:
            return
    # si delaimaj vide
    if delaimaj:
        dialog = xbmcgui.Dialog()
        d = dialog.input("Délai de la 1ère Maj en minutes: Au démarrage de Kodi", type=xbmcgui.INPUT_ALPHANUM)
        if d:
            delaimaj = d
            addon.setSetting(id="delaimaj", value=d.strip())
        else:
            return
    #notice(intmaj)
    #notice(delaimaj)
    showInfoNotification(intmaj + " " + delaimaj)

def rskin2():
    #init addon
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    #Change valeur
    addon.setSetting(id="rskin", value="true")

def rskin3():
    #init addon
    addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    #Change valeur
    addon.setSetting(id="rskin", value="false")


def router(paramstring):
    params = dict(parse_qsl(paramstring))

    dictActions = {
         # player
        'play': (playMedia, params), 'playHK': (playMediaHK, params), 'playHKEpisode': (playEpisode, params),
        # u2p local
        'os': (selectOS, ""), 'apiConf': (configKeysApi, ""), 'clearStrms': (makeStrms, 1), 'ePaste': (editPaste, ""), 'groupe': (creaGroupe, ""),
        # config kodi
        'thmn': (editNbThumbnails, ""), 'resos': (editResos, ''), 'rlk': (reloadSkin, ""),
        # database
        'bd': (importDatabase, ""), 'bdauto': (importDatabase, "autonome"), 'maj': (majDatabase, ""), 'delDta': (delDATABASE, ""), 'patch': (patchNextUp, ""), 'bdepg': (importDatabase, "epg"),
        # listes
        'choixrepo': (choixRepo, ""), 'choixliste': (choixliste, ""), 'createL': (createWidg, ""),  'supL': (supWidg, ""), 'createLV': (createListeV, ""), 'createLT': (createListeT, ""),
        'suppLV': (widget.suppListeTV, ""), 'suppLT': (widget.suppListeT, ""), "affTraktPerso": (affTrakt, ""), "createLP": (createListeLP, ""), "affPastebin": (affPastebin, ""),
         'suppLP': (widget.suppListeLP, ""), "createLTMDB": (createLTMDB, ""), "affTmdb": (affTmdb, ""), "suppLTMDB": (widget.suppLTMDB, ""), "createRUPTO": (createRUPTO, ""),
         "createRUPTOP": (createRUPTOP, ""), "suppLUPTO": (widget.suppLUPTO, ""),
        # HK
        'MenuFilm': (mediasHK, ""), 'MenuDivers': (diversHK, ""), 'MenuSerie': (seriesHK, ""), 'detailM': (detailsMedia, params), 'detailT': (detailsTV, params),
        "afficheLiens": (affLiens2, params), "suggest": (loadSimReco2, params), "affActeurs": (affCast2, params), "ba": (getBa, params), "visuEpisodes": (affEpisodes2, params),
        "filtres": (filtres, params), 'movies': (ventilationHK, ""), 'supView': (supView, params), 'fav': (gestionFavHK, params), 'vuNonVu': (gestionVuSaison, params),
        "visuFenmovie": (fenMovie, params), "genres": (genres, params), "impHK": (importConfigHK, ""), "gestionMedia": (gestionMedia, params), 'MenuTrakt': (traktHKventilation, ""),
        "suiteSerie": (suiteSerie, ""), "vuMovieTrakt": (vuMovieTrakt, params), "affSearch": (affSearch, ""), "affGlobal": (affGlobal, ""), "affSearchCast": (affSearchCast, ""),
        "correctCertif": (correctCertif, params), "affUpto": (affUpto, ""), "loadUpto": (uptobox.loadUpto, params), "loadUptoP": (uptobox.loadUptoP, params), "newUpto": (uptobox.newUpto, params),
        "playMediaUptobox": (uptobox.playMediaUptobox, params), "rechercheUpto": (uptobox.searchUpto, params), "loadUptoSerie": (uptobox.loadSeriesUpto, params), "affSaisonUpto": (uptobox.loadSaisonsUpto, params),
        "visuEpisodesUpto": (uptobox.affEpisodesUpto, params), "affAlldeb": (affAlldeb, ""), "magnets": (uptobox.magnets, params), "histoupto": (uptobox.getHistoUpto, __database__),
        "listeAll": (uptobox.listeAllded, params), "affNewsUpto": (newUptoPublic, params), "addcompte": (addCompteUpto, params), "AffCatPoiss": (newUptoPublic2, params), "affSaisonUptoPoiss": (affSaisonUptoPoiss, params),
        "visuEpisodesUptoPoiss": (visuEpisodesUptoPoiss, params), "delcompte": (delcompte, params), "affdetailfilmpoiss": (uptobox.detailFilmPoiss, params), "cryptFolder": (scraperUPTO.cryptFolder, ""),
        "affSaisonUptofoldercrypt": (uptobox.loadSaisonsUptoFolderCrypt, params), "visuEpisodesFolderCrypt": (uptobox.affEpisodesFolderCrypt, params), "affGlobalHK2": (createbdhk.affGlobal, ""), "feninfo": (fenInfo, params),
        #strm
        'strms': (makeStrms, ""), "strmSelectWidget" : (configureSTRM,""),
        #profils
        'ajoutP': (ajoutProfil, ""), 'choixP': (choixProfil, ""), 'suppP': (suppProfil, ""), 'actifP': (actifProfil, params), 'actifPm': (choixProfil, 1), "affProfils":( affProfils, ""),
        "assistant": (assistant, ""),
        #audiobook
        'MenuAudio':(audioHK, ""),
        #skin
        'choixskin': (choixSkin, ""),
        # repo
        "insertrepo": (scraperUPTO.createRepo, params), "recherepo": (recherRepo, params), "gestionMajRepSerie": (scraperUPTO.updateSeriesRepCR, ""), "gestionMajRep": (uptobox.majRepsFilms, ""),
        "folderPubDetails": (createbdhk.detailsmenuRepCrypte, params), "folderPub": (uptobox.loadFoldersPub, params),"affFoldercryptDivers": (uptobox.loadFolderCryptDivers, params),
        "reinitPoissonnerie": (scraperUPTO.reinitPoissonnerie, ''),
        #pastebin
        "pastepastebin": (createbdhk.menu, ""), "repopastebin": (createbdhk.createRepo, ""), "affRepoPaste": (createbdhk.affRepo, params), "affSaisonPastebin": (createbdhk.affSaisonPastebin, params),
        "visuEpisodesPastebin": (createbdhk.visuEpisodesPastebin, params), "folderPastebin": (scraperUPTO.ajoutFoldercr, params), "menuPastebin": (createbdhk.menuPastebin, ""),
        "menuRepCrypte": (createbdhk.menuRepCrypte, ""),
        #newHK
        "mediasHKFilms": (createbdhk.mediasHKFilms, params), "majHkNew": (scraperUPTO.majHkNew, ''), "genresHK": (createbdhk.genresHK, params), "mediasHKSeries": (createbdhk.mediasHKSeries, params),
        "suiteSerieHK": (createbdhk.suiteSerie, params), "suiteSerieHK2": (createbdhk.suiteSerie2, ""), "resetBDhkNew": (scraperUPTO.resetBDhkNew, ""), "lockRepHK": (uptobox.lockRep, params),
        "tmdbSerie": (createbdhk.tmdbSerie, params), "majhkneww": (scraperUPTO.majHkNew, ''), "findf": (createbdhk.rechercheFilm, params), "findss": (createbdhk.rechercheSerie, params),
        "findc": (affSearchCast, params),  "mepautostart": (mepAutoStart, ""), "affbaext": (createbdhk.affbaext, ""), "affbacat": (createbdhk.affbacat, params), "playMediabaext": (uptobox.playMediabaext, params),
        "affbacattmdb": (createbdhk.affbacattmdb, params), "updateba": (importDatabase, "ba"), "rskin2": (rskin2, ''), "rskin3": (rskin3, ''), "intmajbann15": (intmajbann15, ''), "majhkcron": (majHkcron, ''),  "mepautostart2": (mepAutoStart2, ""),
        }
    if vIPTV:
        dictActionsIPTV = { "iptvLoad": (iptv.menu, ""), "affChaine": (iptv.affChaines, params), "playMediaIptv": (iptv.playMedia, params), "ajoutIPTV": (iptv.ajoutIPTV, ""), "loadF": (iptv.load, params),
                    "activemac": (iptv.activeMac, params), "gestfourn": (iptv.gestfourn, params), "lock": (iptv.lock, params), "affepgChann": (iptv.affepgChann, params), "mapepg": (iptv.mapEpg, params),
                    "gestFuseau": (iptv.gestFuseau, params), "getVod": (iptv.getVodSeries, params), "affVod": (iptv.affVod, params), "gestfournVod": (iptv.gestfournVod, params), "affEpisodes": (iptv.affEpisodes, params),
                    "retireriptv": (iptv.retireriptv, ""), "delDB": (iptv.removeDB, ""), "IPTVbank":(iptv.IPTVbank, ""), "addFavIptv": (iptv.addFavIptv, params), "IPTVfav": (iptv.IPTVfav, ""),
                    "iptvsupfav": (iptv.supfavIptv, params), "iptvdepfav": (iptv.iptvdepfav, params), "iptvreplay": (iptv.replay, params),  "loadFX": (iptv.loadX, ""), "affChainex": (iptv.affChainesx, params),
                    "fepgx": (iptv.forceMajEpgX, "")}
        dictActions.update(dictActionsIPTV)
    notice(len(dictActions))
    if params:
        fn = params['action']
        if fn in dictActions.keys():
            argv = dictActions[fn][1]
            if argv:
                dictActions[fn][0](argv)
            else:
                dictActions[fn][0]()
        elif fn == 'setting':
            xbmcaddon.Addon().openSettings()
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
         menuPbi()




if __name__ == '__main__':

    nameExploit = sys.platform
    __addon__ = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    #notice(nameExploit)
    # Get the plugin url in plugin:// notation.
    __url__ = sys.argv[0]
    # Get the plugin handle as an integer number.
    __handle__ = int(sys.argv[1])
    #  database video kodi
    bdKodis = ["MyVideos119.db", "MyVideos121.db"]
    for bdKodi in bdKodis:
        if os.path.isfile(xbmcvfs.translatePath("special://home/userdata/Database/%s" %bdKodi)):
            __database__ = xbmcvfs.translatePath("special://home/userdata/Database/%s" %bdKodi)
            #break

    #Deprecated xbmc.translatePath. Moved to xbmcvfs.translatePath
    __repAddon__ = xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/")
    __repAddonData__ = xbmcvfs.translatePath("special://home/userdata/addon_data/plugin.video.sendtokodiU2P")
    __keyTMDB__ = getkeyTMDB()
    __params__ = dict(parse_qsl(sys.argv[2][1:]))

    #
    # assistant
    if __addon__.getSetting("actifhk") != "false":
        if not os.path.exists(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P')):
            os.makedirs(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P'))
        plusProfil = False
        if not os.path.isfile(xbmcvfs.translatePath("special://home/addons/plugin.video.sendtokodiU2P/medias.bd")):
            widget.initBookmark()
            if assistant():
                plusProfil = True
            else:
                sys.exit()
        if plusProfil:
            liste = widget.usersBookmark()
            if not liste:
                ajoutProfil(initP=1)

            xbmcgui.Dialog().ok("Configuration" , "Config Ok !!\nUn petit merci aux contributeurs est toujours le bienvenu\nBon film....")
    if not os.path.isfile(__repAddon__ + "service.txt"):
        with open(__repAddon__ + "service.txt", "w") as f:
            mepAutoStart2()
    createFav()
    #notice(pyVersion)
    #notice(pyVersionM)
    #xbmc.executebuiltin("InstallFromZip")
    #notice(sys.version_info)
    #notice(__url__)
    #notice(__handle__)
    router(sys.argv[2][1:])

    #Setting most video properties through ListItem.setInfo() is deprecated and might be removed in future Kodi versions. Please use the respective setter in InfoTagVideo.