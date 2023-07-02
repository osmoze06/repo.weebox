import xbmc
import xbmcgui
import os
import xbmcvfs
import sys
import shutil

xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "service.autoexec", "enabled": false }}')

source = xbmcvfs.translatePath('special://home/downloads/autoexec.py')
destination = xbmcvfs.translatePath('special://home/addons/service.autoexec/autoexec.py')
shutil.copy(source, destination)

xbmc.executebuiltin("Notification(RECUPERATION, Profil)")
xbmc.sleep(2000)

xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "service.autoexec", "enabled": true }}')

sys.exit()