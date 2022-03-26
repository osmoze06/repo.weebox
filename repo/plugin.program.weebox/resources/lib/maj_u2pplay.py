#!/usr/bin/python3
import xbmc
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import shutil
import os, sys
import time


xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "plugin.video.sendtokodiU2P", "enabled": false }}')

xbmc.executebuiltin("Notification(MISE A JOUR,Streaming Services...)")

# telechargement et extraction du zip
zipurl = 'https://github.com/osmoze06/addons_updates/raw/master/plugin.video.sendtokodiU2P.zip'
with urlopen(zipurl) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
        zfile.extractall(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/maj/'))

# copie des fichiers extraits
source_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/maj/plugin.video.sendtokodiU2P')
destination_dir = xbmc.translatePath('special://home/addons/plugin.video.sendtokodiU2P')
shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

xbmc.executebuiltin("Notification(EXTRACTION OK,Mise à jour effectuée !)")

xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "plugin.video.sendtokodiU2P", "enabled": true }}')

time.sleep(2000)
xbmc.executebuiltin('ReloadSkin')

xbmc.executebuiltin("Notification(Mise à jour,Database en cours...)")

xbmc.sleep(2000)

xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.ExecuteAddon", "params": { "addonid": "plugin.video.sendtokodiU2P", "params": ["action=maj"]}, "id":2}')
xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')

sys.exit()