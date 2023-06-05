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

        self.setGeometry(1250, 700, 50, 30, pos_x=0)
        #self.setBackground('special://home/addons/plugin.video.sendtokodiU2P/fanart.jpg')


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
        #noms = [x['name'] for x in self.chaines]
        noms = []
        self.menu.reset()
        for chaine in self.chaines:
            plot = ""
            prog = ""
            if self.epgs:
                epgOk = [(x[1], x[2], x[5], x[6]) for x in self.epgs if x[0] == chaine["epg_channel_id"]]
                for i, epg in enumerate(epgOk[:4]):
                    debut = epg[2][8:10] + ":" + epg[2][10:12]
                    fin = epg[3][8:10] + ":" + epg[3][10:12]
                    if epg[1]:
                        description = epg[1] + "..."
                    else:
                        description = ""
                    if i == 0:
                        #plot += " " * (40 - len(str(chaine["name"])))
                        plot += "[B][COLOR green] #[/COLOR][COLOR white]%s[/B][/COLOR]" %str(epg[0]) + ' ' + debut + " - " + fin + '[COLOR white] [/COLOR] '
                        prog = "[B]%s[/B]" %str(epg[0]) + '\n' + debut + " - " + fin + '\n' + "[I]%s[/I]" %description +'\n'
                    else:
                        #【】
                        plot += "[B][COLOR red] #[/COLOR][COLOR white]%s[/B][/COLOR]" %str(epg[0]) + ' ' + debut + " - " + fin + '[COLOR white] [/COLOR] '
            icon = xbmcgui.ListItem(label=chaine["name"] + "  " + plot)
            icon.setArt({"icon": chaine['stream_icon'], "thumb": chaine['stream_icon']})
            noms.append(icon)

        self.synopA.setText(prog)
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
        #self.removeControl(self.menu)
        self.insertChaines()
        #self.removeControl(self.menu)
        self.insertChaines()
        self.set_navigation()


    def set_controls(self):
        """Set up UI controls"""

        self.colorMenu = '0x00000000'
        self.synopA = pyxbmct.TextBox('font10', textColor='0xFFFFFFFF')
        self.placeControl(self.synopA, 0, 0, rowspan=10, columnspan=29)
        self.synopA.autoScroll(3000, 3000, 6000)

        self.menu = pyxbmct.List('font10', _itemHeight=30, _imageWidth=35, _imageHeight=35, _space=2)
        self.placeControl(self.menu, 11, 0, rowspan=45, columnspan=24)

        self.menuCat = pyxbmct.List('font10', _itemHeight=30, _imageWidth=35, _imageHeight=35)
        self.placeControl(self.menuCat, 11, 24, rowspan=45, columnspan=6)
        #self.menuCat.columnspan = 1
        noms = []
        for chaine in list(self.categoriesx.keys()):
            icon = xbmcgui.ListItem(label=chaine)
            icon.setArt({"icon": 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png', "thumb": 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/iptv.png'})
            noms.append(icon)

        self.menuCat.addItems(noms)
        self.connect(self.menuCat, lambda: self.listFunctionCat(self.menuCat.getListItem(self.menuCat.getSelectedPosition()).getLabel()))
        self.insertChaines()

    def getSynop(self, nom):
        prog = ""
        if self.epgs:
            chaine = [x for x in self.chaines if x["name"] == nom.strip()][0]
            epgOk = [(x[1], x[2], x[5], x[6]) for x in self.epgs if x[0] == chaine["epg_channel_id"]]
            if epgOk:
                epg = epgOk[0]
                debut = epg[2][8:10] + ":" + epg[2][10:12]
                fin = epg[3][8:10] + ":" + epg[3][10:12]
                if epg[1]:
                    description = epg[1] + "..."
                else:
                    description = ""
                prog = "[B]%s[/B]" %epg[0] + " " + debut + "-" + fin + "\n\n[I]%s[/I]" %description
        return prog

    def chaine_update(self):
        nom = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
        nom = nom.split("[B][COLOR")[0]
        prog = self.getSynop(nom)
        self.synopA.setText(prog)

        #item = self.menu.getSelectedItem()
        #self.menu.setImageDimensions(45, 45)

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
