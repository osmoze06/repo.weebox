#!/usr/bin/python3
xbmc.executebuiltin("Notification(ENVOI SUR SERVEUR,Upload en cours...)")
import xbmcvfs
source_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.vstream/vstream.db')
destination_dir = r"smb://MONITEUR:2929@192.168.8.10/PUBLIC/LIBREELEC/SYNC/vstream.db"
xbmcvfs.copy(source_dir, destination_dir)
xbmc.executebuiltin("Notification(UPLOAD OK,DB envoyée au Serveur !)")