#!/usr/bin/python3
import xbmc
import xbmcvfs
import sys

source_dir = r"smb://MONITEUR:2929@192.168.8.10/PUBLIC/LIBREELEC/SYNC/vstream.db"
destination_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.vstream/vstream.db')
xbmcvfs.copy(source_dir, destination_dir)
xbmc.executebuiltin("Notification(BASE DE DONNEES OK,Mise à jour effectuée !)")
xbmc.sleep(2000)
xbmc.executebuiltin("Notification(ACTUALISATION, Chargement en cours...)")
xbmc.sleep(2000)
xbmc.executebuiltin('ReloadSkin')
sys.exit()