# -*- coding: utf-8 -*-
import xbmc
import time


time.sleep(1)
xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.ExecuteAddon", "params": { "addonid": "plugin.video.sendtokodiU2P", "params": ["action=maj"]}, "id":2}')
#time.sleep(0.5)
xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')