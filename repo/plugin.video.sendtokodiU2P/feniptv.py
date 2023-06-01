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
from ipt import IPTVMac
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

class MyDialog(pyxbmct.AddonDialogWindow):
    def __init__(self, title="test"):
        #super(MyDialog, self).__init__(title)
        #self.setGeometry(800, 560, 50, 30)
        self._monitor = xbmc.Monitor()
        self._player = xbmc.Player()

    def play(self, path):
        self._player.play(path)
        xbmc.sleep(200)  # Wait for the player to start, adjust the timeout if necessary
        self.close()
        while self._player.isPlaying():
            if self._monitor.waitForAbort(1):
                raise SystemExit
        self.doModal()

class FenIptvold(pyxbmct.AddonFullWindow):

    def __init__(self, *argvs):
        notice(argvs)
        super(FenIptv, self).__init__(argvs[0])
        self.setGeometry(700, 450, 9, 4)
        self.setBackground(back)
        self.set_info_controls()
        self.set_active_controls()
        self.set_navigation()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)


class FenIptv(pyxbmct.AddonFullWindow):

    def __init__(self, argvs):
        """Class constructor"""
        # Call the base class' constructor.
        title, chaines, epg = argvs
        self.chaines = chaines
        self.epg = epg
        #notice(self.epg.keys())
        #notice(self.chaines[0][2])
        super(FenIptv, self).__init__()
        # Set width, height and the grid parameters
        #self.setBackground(back)

        self.setGeometry(1250, 700, 50, 30, pos_x=0)
        # Call set controls method
        self.set_controls()
        # Call set navigation method.
        self.set_navigation()
        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):
        """Set up UI controls"""
        self.colorMenu = '0xFFFFFFFF'


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



    def chaine_update(self):
        nom = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
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

    def getChaine(self):
        nom = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
        chaine = [x for x in self.chaines if nom == x[1]]
        notice(chaine)

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        """
        self.menu.controlUp(self.radiobutton)
        #self.menu.controlDown(self.tabCast[0])
        #self.menu.controlLeft(self.tabCast[0])
        #self.radiobutton.controlUp(self.tabCast[0])
        self.menu.controlRight(self.radiobutton)
        self.radiobutton.controlRight(self.menu)
        self.radiobutton.controlLeft(self.menu)
        self.radiobutton.controlDown(self.menu)
        """
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
        chaine = [x for x in self.chaines if nom == x[1]]
        link = chaine[0][0]
        site = ADDON.getSetting("site1")
        mac = str.upper(ADDON.getSetting("mac1"))
        token = ADDON.getSetting("token1")
        iptv = IPTVMac(site, mac, token)
        notice(site)
        notice(mac)
        notice(token)
        notice(chaine)
        linkCMD = unquote(chaine[0][0])
        if "localhost" not in linkCMD and "http" in linkCMD:
            link = linkCMD.split(" ")[1]
        else:
            cmd = quote(linkCMD)
            #notice(cmd)
            link = iptv.getInfos(iptv.createLink.format(linkCMD)).json()["js"]["cmd"].split(" ")[1]
        result = {"url": link + "|User-Agent=Mozilla", "title": chaine[0][1]}
        if result and "url" in result.keys():
            listIt = createListItemFromVideo(result)
            xbmc.Player().play(link, listIt)
            #mplay = MyDialog()
            #mplay.play(link)
        #self.close()
        #ACTION_CONTEXT_MENU