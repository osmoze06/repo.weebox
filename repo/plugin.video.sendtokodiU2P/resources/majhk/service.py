import time
import xbmcaddon
import sys
import xbmcvfs
import sqlite3
import xbmc
import os
import loadhk3

pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor

time.sleep(0.1)
addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
interval = int(addon.getSetting("intmaj"))
delaiMaj = int(addon.getSetting("delaimaj"))
if interval:
    delai = time.sleep(delaiMaj * 60)
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        okMaj = False
        if addon.getSetting("majlecture") != "false":
            okMaj = True
        else:
            if xbmc.Player().isPlaying():
                intervalNew = 1
            else:
                okMaj = True
        if okMaj:
            actu = loadhk3.getLinks()
            intervalNew = interval
            #if addon.getSetting("actifStrm") != "false":
            #    a = 0
            #    while a < 60:
            #        time.sleep(1)
            #        a += 1
            #        if os.path.exists(fNewSerie):
            #           break
            #    xbmc.executebuiltin("RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=strms)")
        if monitor.waitForAbort(intervalNew * 60):
            break