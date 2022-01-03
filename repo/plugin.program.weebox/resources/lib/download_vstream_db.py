import xbmc
import xbmcvfs
import xbmcgui
import shutil
import os

pDialog = xbmcgui.DialogProgress()
pDialog.create('WEEBOX', 'TELECHARGEMENT DATABASE, Synchronisation de la Bibliothèque Vidéos...')
xbmc.sleep(2000)
pDialog.update(50, 'Téléchargement de la DATABASE en cours - Prend environ 3 minutes...')

source_dir = r"smb://KODI:Ongran2021@192.168.1.1/kodi/sync/MyVideos119.db"
destination_dir = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.program.weebox/downloads/MyVideos119.db')
destination_dir2 = xbmcvfs.translatePath('special://home/userdata/Database/MyVideos119.db')
xbmcvfs.copy(source_dir, destination_dir)

pDialog.update(75, 'Installation de la DATABASE...')

shutil.move(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.program.weebox/downloads/MyVideos119.db'), destination_dir2)

pDialog.update(100, 'DATABASE OK, Rechargement des données en cours...')
xbmc.sleep(2000)
pDialog.close()

xbmc.executebuiltin('ReloadSkin')
sys.exit()