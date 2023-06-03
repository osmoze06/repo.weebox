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

    def __init__(self, argvs):
        """Class constructor"""


        # Call the base class' constructor.
        super(FenIptvX, self).__init__()
        # Set width, height and the grid parameters
        self.title = "XTREAM U2Pplay"
        self.setBackground('special://home/addons/plugin.video.sendtokodiU2P/fanart.jpg')

        self.setGeometry(1250, 700, 50, 30, pos_x=0)

        f = 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/fond.png'
        #f = 'special://home/addons/plugin.video.sendtokodiU2P/fanart.jpg'
        #fond = pyxbmct.Image(f)
        #self.placeControl(fond, 0, 0, rowspan=54, columnspan=30)

        self.getEpg()

        self.categoriesx = self.getCat(1)

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

        self.menu = pyxbmct.List('font10', _itemHeight=125, _imageWidth=60, _imageHeight=60, _space=2)
        self.placeControl(self.menu, 0, 0, rowspan=58, columnspan=24)
        #noms = [x['name'] for x in self.chaines]
        noms = []
        for chaine in self.chaines:
            if self.epgs:
                plot = ""
                epgOk = [(x[1], x[2], x[5], x[6]) for x in self.epgs if x[0] == chaine["epg_channel_id"]]
                for i, epg in enumerate(epgOk[:2]):
                    debut = epg[2][8:10] + ":" + epg[2][10:12]
                    fin = epg[3][8:10] + ":" + epg[3][10:12]
                    if epg[1]:
                        description = epg[1][:110] + "..."
                    else:
                        description = ""
                    if i == 0:
                        plot += "[B]%s[/B]" %str(epg[0]) + '\n' + debut + " - " + fin + '\n' + "[I]%s[/I]" %description +'\n'
                    else:
                        plot += "[B]%s[/B]" %str(epg[0]) + '\n' + debut + " - " + fin + '\n'
            icon = xbmcgui.ListItem(label=chaine["name"] + "\n" + plot)
            icon.setArt({"icon": chaine['stream_icon'], "thumb": chaine['stream_icon']})
            noms.append(icon)

        self.menu.addItems(noms)
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
        self.set_navigation()


    def set_controls(self):
        """Set up UI controls"""

        self.colorMenu = '0x00000000'
        self.menuCat = pyxbmct.List('font10', _itemHeight=30, _imageWidth=35, _imageHeight=35)
        self.placeControl(self.menuCat, 0, 24, rowspan=58, columnspan=6)
        #self.menuCat.columnspan = 1
        noms = []
        for chaine in list(self.categoriesx.keys()):
            icon = xbmcgui.ListItem(label=chaine)
            icon.setArt({"icon": 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png', "thumb": 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png'})
            noms.append(icon)

        self.menuCat.addItems(noms)
        self.connect(self.menuCat, lambda: self.listFunctionCat(self.menuCat.getListItem(self.menuCat.getSelectedPosition()).getLabel()))
        self.insertChaines()



    def chaine_update(self):
        nom = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()


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
        nom = nom.split("\n")[0]
        num = [(x["stream_type"], x['stream_id']) for x in self.chaines if nom == x["name"]][0]
        link = self.itv.link.format(num[0], num[1])
        result = {"url": link + "|User-Agent=Mozilla", "title": nom}
        if result and "url" in result.keys():
            listIt = createListItemFromVideo(result)
            xbmc.Player().play(link, listIt)


