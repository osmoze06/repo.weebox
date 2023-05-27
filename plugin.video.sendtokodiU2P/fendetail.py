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
from pastebin import Pastebin
from medias import Media, TMDB
import zipfile
import threading
import datetime
from upNext import upnext_signal
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

pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor
if pyVersionM == 8:
    import pasteCrypt3 as cryptage
else:
    import pasteCrypt2 as cryptage
import random

class FenFilmDetail(pyxbmct.AddonDialogWindow):

    def __init__(self, title='', numId="", links=""):
        """Class constructor"""
        # Call the base class' constructor.
        super(FenFilmDetail, self).__init__(title)
        # Set width, height and the grid parameters
        self.numId = numId
        self.links = links
        self.setGeometry(1180, 660, 50, 30)
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
        movies = self.extractMedias(sql=sql)
        media = Media("movie", *movies[0])

        
        #backdrop
        image = pyxbmct.Image(media.backdrop, colorDiffuse='0x22FFFFFF')
        self.placeControl(image, 0, 0, rowspan=50, columnspan=30)
        logo, clearart, banner = self.extractFanart(self.numId)
        urlFanart = "http://assets.fanart.tv/fanart/movie/"

        #clearlogo ou title
        if logo:
            imageLogo = pyxbmct.Image(urlFanart + logo)
            self.placeControl(imageLogo, 0, 0, rowspan=8, columnspan=7)
        else:
            label = pyxbmct.Label(media.title, font="font14", textColor="0xFF00FF00")
            self.placeControl(label, 2, 0, columnspan=15)

        #poster
        #if clearart:
        #    imageClearart = pyxbmct.Image(urlFanart + clearart)
        #    self.placeControl(imageClearart, 35, 25, rowspan=12, columnspan=5)
        #else:
        poster = pyxbmct.Image(media.poster) 
        self.placeControl(poster, 0, 25, rowspan=23, columnspan=5)

        #menu
        #labelMenu = pyxbmct.Label('MENU', textColor=self.colorMenu)
        #self.placeControl(labelMenu, 31, 0, columnspan=10)
        self.menu = pyxbmct.List('font12', _itemHeight=30)
        self.placeControl(self.menu, 29, 0, rowspan=18, columnspan=25)
        #, "Acteurs & Réalisateur"
        self.menu.addItems(["[COLOR blue]Bande Annonce[/COLOR]", "[COLOR green]Lire[/COLOR]", "Suggestions", "Similaires"])
        self.connect(self.menu, lambda: self.listFunction(self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()))
        
        #overview
        #labelSynop = pyxbmct.Label('SYNOPSIS', textColor=colorMenu)
        #self.placeControl(labelSynop, 14, 0, columnspan=10)
        self.synop = pyxbmct.TextBox('font12', textColor='0xFFFFFFFF')
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
        self.placeControl(self.radiobutton, ligneNot + 1, 20, columnspan=5)
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

        # sagas
        self.sagaOk = False
        sql = "SELECT s.title, s.poster, s.numId FROM saga AS s WHERE s.numId=(SELECT t.numIdSaga FROM sagaTitle AS t WHERE t.numId={})".format(self.numId)
        saga = extractMedias(sql=sql)
        #notice(saga)
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

    def affSaga(self, numId):
        showInfoNotification(numId)
        mediasHK({"famille": "sagaListe", "u2p": numId})
        self.close()
        

    def setCasting2(self):
        mdb = TMDB(__keyTMDB__)
        liste = mdb.castFilm(self.numId)
        nbListe = len(liste)
        label = pyxbmct.Label("CASTING", textColor=self.colorMenu)
        self.placeControl(label, 45, 0, columnspan=4)
        posy = 3
        cast1, cast2 = None, None
        self.tabCast = [cast1, cast2]
        self.tabCast2 = [cast1, cast2]
        for i, casting1 in enumerate(liste[:2]):
            self.tabCast2[i] = casting1
            if self.tabCast2[i][2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + self.tabCast2[i][2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(self.tabCast2[i][0], self.tabCast2[i][1])
            self.tabCast[i] = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(self.tabCast[i], 42, posy, rowspan=9, columnspan=2) 
            self.connect(self.tabCast[i], lambda: self.affCastingFilmo(str(self.tabCast2[i][3])))
            posy += 2
                

    def setCasting(self):
        # cast
        posy = 3
        posx = 10
        pos = 0
        posh = 40
        mdb = TMDB(__keyTMDB__)
        liste = mdb.castFilm(self.numId)
        nbListe = len(liste)
        label = pyxbmct.Label("CASTING", textColor=self.colorMenu)
        self.placeControl(label, posh + 3, 0, columnspan=4)
        self.tabCast = [] 
        if pos in range(nbListe):
            casting1 = liste[pos]
            if casting1[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting1[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting1[0], casting1[1])
            bcast1 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast1, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast1, lambda: self.affCastingFilmo(str(casting1[3])))
            self.tabCast.append(bcast1)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting2 = liste[pos]
            if casting2[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting2[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting2[0], casting2[1])
            bcast2 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast2, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast2, lambda: self.affCastingFilmo(str(casting2[3])))
            self.tabCast.append(bcast2)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting3 = liste[pos]
            if casting3[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting3[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting3[0], casting3[1])
            bcast3 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast3, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast3, lambda: self.affCastingFilmo(str(casting3[3])))
            self.tabCast.append(bcast3)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting4 = liste[pos]
            if casting4[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting4[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting4[0], casting4[1])
            bcast4 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast4, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast4, lambda: self.affCastingFilmo(str(casting4[3])))
            self.tabCast.append(bcast4)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting5 = liste[pos]
            if casting5[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting5[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting5[0], casting5[1])
            bcast5 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast5, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast5, lambda: self.affCastingFilmo(str(casting5[3])))
            self.tabCast.append(bcast5)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting6 = liste[pos]
            if casting6[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting6[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting6[0], casting6[1])
            bcast6 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast6, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast6, lambda: self.affCastingFilmo(str(casting6[3])))
            self.tabCast.append(bcast6)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting7 = liste[pos]
            if casting7[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting7[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting7[0], casting7[1])
            bcast7 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast7, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast7, lambda: self.affCastingFilmo(str(casting7[3])))
            self.tabCast.append(bcast7)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting8 = liste[pos]
            if casting8[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting8[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting8[0], casting8[1])
            bcast8 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast8, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast8, lambda: self.affCastingFilmo(str(casting8[3])))
            self.tabCast.append(bcast8)
            posy += 2
            pos += 1
        if pos in range(nbListe):
            casting9 = liste[pos]
            if casting9[2]:
                imFoc = "http://image.tmdb.org/t/p/w92" + casting9[2]
            else:
                imFoc = ""
            txRea = "%s (%s)" %(casting9[0], casting9[1])
            bcast9 = pyxbmct.Button(txRea, focusTexture=imFoc, noFocusTexture=imFoc, font="font10", focusedColor='0xFFFF0000', alignment=pyxbmct.ALIGN_CENTER, shadowColor='0xFF000000')
            self.placeControl(bcast9, posh, posy, rowspan=posx, columnspan=2) 
            self.connect(bcast9, lambda: self.affCastingFilmo(str(casting9[3])))
            self.tabCast.append(bcast9)
            posy += 2
            pos += 1
        
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
            for i in range(len(self.tabCast)):
                self.tabCast[i].controlUp(self.menu)
                self.tabCast[i].controlDown(self.radiobutton)
                if (i + 1) < len(self.tabCast):
                    self.tabCast[i].controlRight(self.tabCast[i + 1])
                else:
                    if self.sagaOk:
                        self.tabCast[i].controlRight(self.bSaga)   
                if (i - 1) > -1:
                    self.tabCast[i].controlLeft(self.tabCast[i - 1])
                else:
                    if self.sagaOk:
                        self.tabCast[i].controlLeft(self.bSaga)
        if self.sagaOk:
            self.bSaga.controlUp(self.menu)
            self.bSaga.controlDown(self.radiobutton)
            self.bSaga.controlLeft(self.tabCast[8])
            self.bSaga.controlRight(self.tabCast[0])
            

        
    def radio_update(self):
        # Update radiobutton caption on toggle
        #liste favs
        if self.radiobutton.isSelected():
            self.radiobutton.setLabel("Retirer Fav's HK")
            gestionFavHK({"mode": "ajout", "u2p": self.numId, "typM": "movies"})
        else:
            self.radiobutton.setLabel("Ajouter Fav's HK")
            gestionFavHK({"mode": "sup", "u2p": self.numId, "typM": "movies"})

    def affCastingFilmo(self, numId):
        mediasHK({"famille": "cast", "u2p": numId})
        self.close()

    def listFunction(self, tx):
        #lsite fonction du menu
        self.close()
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

    def extractFanart(self, numId):
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

    def extractMedias(self, limit=0, offset=1, sql="", unique=0):
        cnx = sqlite3.connect(__repAddon__ + "medias.bd")
        cur = cnx.cursor()
        def normalizeTitle(tx):
            #tx = re.sub(r''' {2,}''', ' ', re.sub(r''':|;|'|"|,''', ' ', tx))
            tx = re.sub(r''':|;|'|"|,''', ' ', tx)
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

class MyWindow3(pyxbmct.AddonDialogWindow):

    def __init__(self, title=''):
        """Class constructor"""
        # Call the base class' constructor.
        super(MyWindow3, self).__init__(title)
        # Set width, height and the grid parameters
        self.setGeometry(1280, 720, 5, 4)
        # Call set controls method
        self.set_controls()
        # Call set navigation method.
        self.set_navigation()
        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):
        """Set up UI controls"""
        # Image control
        #self.group = pyxbmct.Group(1,2)
        image = pyxbmct.Image('https://peach.blender.org/wp-content/uploads/poster_rodents_small.jpg?3016dc', colorDiffuse='0x22FFFFFF')
        icon = xbmcgui.ListItem(label="Acteur\nrole")
        icon.setArt({"icon": 'https://peach.blender.org/wp-content/uploads/poster_rodents_small.jpg?3016dc', "thumb": 'https://peach.blender.org/wp-content/uploads/poster_rodents_small.jpg?3016dc'})
        self.placeControl(image, 0, 0, rowspan=3, columnspan=2)
        # Text label
        label = pyxbmct.Label('Your name:')
        self.placeControl(label, 3, 0)

        #
        text = "0xFFFFFFFF"
        self.listeActeur = pyxbmct.List(_imageWidth=150, _imageHeight=150, _itemHeight=150)
        
        #self.listeActeur.addItem()
        self.placeControl(self.listeActeur, 0, 3, rowspan=4, columnspan=1)
        #self.setFocus(self.listeActeur)
        #["Item {0}".format(i) for i in range(1, 11)] + 
        self.listeActeur.addItems([icon])
        # Text edit control
        self.name_field = pyxbmct.Edit('')
        self.placeControl(self.name_field, 3, 1)
        # Close button
        self.close_button = pyxbmct.Button('Close')
        self.placeControl(self.close_button, 4, 0)

        self.test_button = pyxbmct.Button('CTest')
        self.placeControl(self.test_button, 0, 2)
        # Connect close button
        self.connect(self.close_button, self.close)
        # Hello button.
        self.hello_buton = pyxbmct.Button('Hello')
        self.placeControl(self.hello_buton, 4, 1)
        # Connect Hello button.
        self.connect(self.hello_buton, lambda:
            xbmc.executebuiltin('Notification(Hello {0}!, Welcome to PyXBMCt.)'.format(
                self.name_field.getText())))
        

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        # Note there is a new feature:
        # if you instead write self.autoNavigation() PyXBMCT will set up
        # the navigation between the controls for you automatically!
        self.name_field.controlUp(self.hello_buton)
        self.name_field.controlDown(self.hello_buton)
        self.close_button.controlLeft(self.hello_buton)
        self.close_button.controlRight(self.hello_buton)
        self.hello_buton.setNavigation(self.name_field, self.name_field, self.close_button, self.close_button)
        # Set initial focus.
        self.setFocus(self.name_field)
        #self.setFocus(self.listeActeur)

        
        
    
class MyWindow2(pyxbmct.AddonDialogWindow):

    def __init__(self, title=''):
        # You need to call base class' constructor.
        super(MyWindow, self).__init__(title)
        # Set the window width, height and the grid resolution: 2 rows, 3 columns.
        self.setGeometry(350, 150, 2, 3)
        # Create a text label.
        label = pyxbmct.Label('This is a PyXBMCt window.', alignment=pyxbmct.ALIGN_CENTER)
        # Place the label on the window grid.
        self.placeControl(label, 0, 0, columnspan=3)
        # Create a button.
        button = pyxbmct.Button('Close')
        # Place the button on the window grid.
        self.placeControl(button, 1, 1)
        # Set initial focus on the button.
        self.setFocus(button)
        # Connect the button to a function.
        self.connect(button, self.close)
        # Connect a key action to a function.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
