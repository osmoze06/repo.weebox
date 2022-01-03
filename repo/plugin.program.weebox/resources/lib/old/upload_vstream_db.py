#!/usr/bin/python3
import xbmc
import xbmcvfs
import sys

source_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.vstream/vstream.db')
destination_dir = r"smb://MONITEUR:2929@192.168.1.10/laragon/kodi_sync/vstream.db"
xbmcvfs.copy(source_dir, destination_dir)

xbmc.executebuiltin("Notification(UPLOAD OK,DB envoyée au Serveur !)")
sys.exit()