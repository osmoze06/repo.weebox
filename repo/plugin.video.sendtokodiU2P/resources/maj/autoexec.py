# -*- coding: utf-8 -*-
import xbmc
import time
import xbmcaddon
import scraperUPTO
import threading
import datetime

time.sleep(1)
addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
if addon.getSetting("majhk2")  != "false":
    if addon.getSetting("actifnewpaste")  != "false":
        xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.ExecuteAddon", "params": { "addonid": "plugin.video.sendtokodiU2P", "params": ["action=majhkneww"]}, "id":2}')
    if addon.getSetting("actifhk")  != "false":
        xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.ExecuteAddon", "params": { "addonid": "plugin.video.sendtokodiU2P", "params": ["action=maj"]}, "id":2}')
    time.sleep(0.5)
    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')