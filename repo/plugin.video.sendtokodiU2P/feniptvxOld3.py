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
import threading
import datetime
import widget
from datetime import datetime
from datetime import timedelta
from util import *
import iptvXtream as iptvx
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
BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/iptv.db')


class FenIptvX(pyxbmct.AddonFullWindow):

    def __init__(self, num=1):
        """Class constructor"""

        self.title = "XTREAM U2Pplay"
        # Call the base class' constructor.
        super(FenIptvX, self).__init__()
        # Set width, height and the grid parameters
        #self.setBackground(back)


        self.setGeometry(1250, 700, 50, 30, pos_x=0)

        self.getEpg()

        self.categoriesx = self.getCat(num)
        notice(self.categoriesx)
        if not self.categoriesx:
            self.close()

        self.getChaines(self.categoriesx[list(self.categoriesx.keys())[0]])

        # Call set controls method
        self.set_controls()

        # Call set navigation method.
        self.set_navigation()

        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def getChaines(self, num):
        self.chaines = self.itv.streamsByCategory(self.itv.liveType, num)
        notice(self.chaines)

    def aut(self, num=1):
        self.itv = iptvx.IPTVXtream(num)
        try:
            cc = self.itv.authenticate()
            notice(cc)
            if cc["user_info"]["status"] == "Active":
                valid = True
                notice('server ok')
                notice(cc["user_info"]["exp_date"])
            else:
                valid = False
        except Exception as e:
            valid = False
            notice(e)
            dialog = xbmcgui.Dialog()
            dialog.ok("Compte Out", str(e))
        return valid

    def getCat(self, num=1):
        if self.aut(num):
            dictCat = {genre["category_name"]: genre["category_id"] for genre in self.itv.categories(self.itv.liveType)}
        else:
            dictCat = {}
        return dictCat

    def getEpg(self):
        bd = iptvx.BookmarkIPTVXtream(BDBOOKMARK)
        self.epgs = bd.extractEpgX()

    def insertChaines(self):
        self.menu = pyxbmct.List('font10', _itemHeight=35, _imageWidth=35, _imageHeight=35)
        self.placeControl(self.menu, 0, 0, rowspan=55, columnspan=8)
        #noms = [x['name'] for x in self.chaines]
        noms = []
        self.dictEpgChaine = {}
        for chaine in self.chaines:
            plot = ""
            prog = ""
            if self.epgs:
                epgOk = [(x[1], x[2], x[5], x[6]) for x in self.epgs if x[0] == chaine["epg_channel_id"]]
                for i, epg in enumerate(epgOk[:20]):
                    debut = epg[2][8:10] + ":" + epg[2][10:12]
                    fin = epg[3][8:10] + ":" + epg[3][10:12]
                    if epg[1]:
                        description = epg[1][:250] + "..."
                    else:
                        description = ""
                    #if i == 0:
                    #    prog = " [B]%s[/B]" %str(epg[0]) + ' ' + debut + " - " + fin
                    if i < 2:
                        plot += "[B]%s[/B]" %str(epg[0]) + '\n' + debut + " - " + fin + '\n' + "[I]%s[/I]" %description + '\n\n'
                    else:
                        plot += "[B]%s[/B]" %str(epg[0]) + '  ' + debut + " - " + fin + '\n\n'

            icon = xbmcgui.ListItem(label=chaine["name"] + prog)
            icon.setArt({"icon": chaine['stream_icon'], "thumb": chaine['stream_icon']})
            noms.append(icon)
            self.dictEpgChaine[chaine["name"]] = plot

        self.menu.addItems(noms)


        self.synopA.setText(self.dictEpgChaine[self.chaines[0]["name"]])
        #self.synopA.setText("Synopsis")
        self.connect(self.menu, lambda: self.listFunction(self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()))
        self.connectEventList([pyxbmct.ACTION_MOVE_UP,
                               pyxbmct.ACTION_MOVE_DOWN,
                               pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
                               pyxbmct.ACTION_MOUSE_WHEEL_UP,
                               pyxbmct.ACTION_MOUSE_MOVE],
                              self.chaine_update)




    def listFunctionCat(self, nom):
        self.getChaines(self.categoriesx[nom])
        self.removeControl(self.menu)
        self.insertChaines()
        self.removeControl(self.menu)
        self.insertChaines()
        self.set_navigation()

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=200 time=700',),
                                ('WindowClose', 'effect=fade start=200 end=0 time=700',)])


    def set_controls(self):
        """Set up UI controls"""

        self.colorMenu = '0xFFFFFFFF'
        self.synopA = pyxbmct.TextBox('font10', textColor='0xFFFFFFFF')
        self.placeControl(self.synopA, 0, 9, rowspan=55, columnspan=15)

        self.menuCat = pyxbmct.List('font10', _itemHeight=35, _imageWidth=35, _imageHeight=35)
        self.placeControl(self.menuCat, 0, 24, rowspan=55, columnspan=6)
        #self.menuCat.columnspan = 1
        noms = []
        for chaine in list(self.categoriesx.keys()):
            icon = xbmcgui.ListItem(label=chaine)
            icon.setArt({"icon": 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png', "thumb": 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png'})
            noms.append(icon)

        self.menuCat.addItems(noms)
        self.connect(self.menuCat, lambda: self.listFunctionCat(self.menuCat.getListItem(self.menuCat.getSelectedPosition()).getLabel()))
        self.insertChaines()

        # self menuChaines
        """
        self.imageLogo = pyxbmct.Image(self.chaines[0][3])
        self.placeControl(self.imageLogo, 34, 25, rowspan=14, columnspan=5)


        self.tabNom = [c[1] for c in self.chaines]
        self.menu = pyxbmct.List('font13', _itemHeight=30)
        self.placeControl(self.menu, 29, 0, rowspan=24, columnspan=25)

        self.menu.addItems(self.tabNom)
        self.connect(self.menu, lambda: self.listFunction(self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()))
        self.connectEventList([pyxbmct.ACTION_MOVE_UP,
                               pyxbmct.ACTION_MOVE_DOWN,
                               pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
                               pyxbmct.ACTION_MOUSE_WHEEL_UP,
                               pyxbmct.ACTION_MOUSE_MOVE],
                              self.chaine_update)

        a = time.time() + 7200
        plot = "Pas d'information..."
        nomTV = "Inconnu"
        tx = " - "
        positionEmission  = 0
        numChaine = str(self.chaines[0][2])
        if numChaine in self.epg.keys():
            for i, e in enumerate(self.epg[numChaine]):
                #notice([e['start_timestamp'], int(a), e['stop_timestamp']])
                if e['start_timestamp'] < int(a) and int(a) < e['stop_timestamp']:
                    nomTV = "[COLOR red]%s[/COLOR]" %e['name']
                    plot = e["descr"]
                    tx = "%s - %s" %(e["time"][11:-3], e["time_to"][11:-3])
                    positionEmission = (a - float(e['start_timestamp'])) / (float(e['stop_timestamp']) - e['start_timestamp']) * 100
                    break

        self.nomTV = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.nomTV, 0, 0, rowspan=4, columnspan=22)
        self.nomTV.setText(nomTV)

        self.heure  = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.heure, 3, 0, rowspan=3, columnspan=12)
        self.heure.setText(tx)

        self.synop = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.synop, 6, 0, rowspan=11, columnspan=22)
        self.synop.setText(plot)
        self.synop.autoScroll(1000, 2000, 3000)

        self.slider = pyxbmct.Slider(orientation=xbmcgui.HORIZONTAL)
        self.placeControl(self.slider, 4, 4, pad_y=1, rowspan=1, columnspan=4)
        self.slider.setPercent(positionEmission)


        plot = "Pas d'information..."
        nomTV = "Inconnu"
        tx = " - "
        try:
            e = self.epg[self.chaines[0][2]][i + 1]
            nomTV = "[COLOR red]%s[/COLOR]" %e['name']
            plot = e["descr"]
            tx = "%s - %s" %(e["time"][11:-3], e["time_to"][11:-3])
        except: pass

        pos = 17
        self.nomTVA = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.nomTVA, 0 + pos, 0, rowspan=4, columnspan=22)
        self.nomTVA.setText(nomTV)

        self.synopA = pyxbmct.TextBox('font13', textColor='0xFFFFFFFF')
        self.placeControl(self.synopA, 3 + pos, 0, rowspan=8, columnspan=22)
        self.synopA.setText(plot)
        """



    def chaine_update(self):
        nom = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
        notice(self.dictEpgChaine[nom])
        try:
            self.removeControl(self.synopA)
        except: pass
        self.synopA = pyxbmct.TextBox('font10', textColor='0xFFFFFFFF')
        self.placeControl(self.synopA, 0, 9, rowspan=55, columnspan=15)
        self.synopA.setText(self.dictEpgChaine[nom])

        """
        chaine = [x for x in self.chaines if nom == x[1]]
        #self.image.setImage(chaine[0][3])
        self.removeControl(self.imageLogo)
        self.imageLogo = pyxbmct.Image(chaine[0][3])
        self.placeControl(self.imageLogo, 34, 25, rowspan=14, columnspan=5)
        a = time.time() + 7200
        plot = "Pas d'information..."
        nomTV = ""
        tx = ""
        positionEmission  = 0
        numChaine = str(chaine[0][2])
        if numChaine in self.epg.keys():
            for i, e in enumerate(self.epg[numChaine]):
                if e['start_timestamp'] < int(a) and int(a) < e['stop_timestamp']:
                    nomTV = "[COLOR red]%s[/COLOR]" %e['name']
                    plot = e["descr"]
                    tx = "%s - %s" %(e["time"][11:-3], e["time_to"][11:-3])
                    positionEmission = (a - float(e['start_timestamp'])) / (float(e['stop_timestamp']) - e['start_timestamp']) * 100
                    break
        self.nomTV.setText(nomTV)
        self.heure.setText(tx)
        self.synop.setText(plot)
        self.slider.setPercent(positionEmission)

        plot = "Pas d'information..."
        nomTV = "Inconnu"
        tx = " - "
        try:
            e = self.epg[chaine[0][2]][i + 1]
            nomTV = "[COLOR red]%s[/COLOR]" %e['name']
            plot = e["descr"]
            tx = "%s - %s" %(e["time"][11:-3], e["time_to"][11:-3])
        except: pass
        pos = 17
        self.nomTVA.setText(nomTV)
        self.synopA.setText(plot)
        """

    def getChaine(self):
        nom = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
        chaine = [x for x in self.chaines if nom == x[1]]
        notice(chaine)

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""

        self.menu.controlLeft(self.menuCat)
        self.menu.controlRight(self.menuCat)

        self.menuCat.controlLeft(self.menu)
        self.menuCat.controlRight(self.menu)


        self.setFocus(self.menu)



    def radio_update(self):
        if self.radiobutton.isSelected():
            self.radiobutton.setLabel("Retirer Fav's HK")
            gestionFavHK({"mode": "ajout", "u2p": self.numId, "typM": "movies"})
        else:
            self.radiobutton.setLabel("Ajouter Fav's HK")
            gestionFavHK({"mode": "sup", "u2p": self.numId, "typM": "movies"})

    def listFunction(self, nom):
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()
        #nom = nom.split("\n")[0]
        notice(nom)
        nom = nom.split("[B][COLOR")[0]
        num = [(x["stream_type"], x['stream_id']) for x in self.chaines if nom.strip() == x["name"]][0]
        link = self.itv.link.format(num[0], num[1]) + ".ts"
        result = {"url": link + "|User-Agent=Mozilla", "title": nom, "plot": self.getSynop(nom)}
        if result and "url" in result.keys():
            listIt = createListItemFromVideox(result, self.chaines)
            xbmc.Player().play(link, listIt)

def createListItemFromVideox(video, chaines):
    try:
        media = MediaSp(**video)
        li = xbmcgui.ListItem(media.title, path=media.url)
        updateInfoTagVideo2(li, media)
        notice(media.title)
        chaine = [x for x in chaines if x["name"] == media.title.strip()][0]
        notice(chaine)
        li.setArt({"icon": chaine['stream_icon'], "thumb": chaine['stream_icon']})
    except Exception as e:
        notice("feniptvx.py - createListItemFromVideo::createListItemFromVideo " + str(e))
    return li

