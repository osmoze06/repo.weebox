import xbmc
import xbmcvfs
import xbmcgui
import shutil
import os

pDialog = xbmcgui.DialogProgress()
pDialog.create('WEEBOX', 'TELECHARGEMENT DATABASE, Synchronisation de la Bibliothèque Vidéos...')
xbmc.sleep(2000)
pDialog.update(50, 'Téléchargement de la DATABASE en cours...')

source_dir1 = r"smb://KODI:Ongran2021@192.168.1.1/kodi/sync/medias.bd"
destination_dir1 = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/medias.bd')
xbmcvfs.copy(source_dir1, destination_dir1)

pDialog.update(75, 'Syncronisation des historiques de lecture...')

source_dir2 = r"smb://KODI:Ongran2021@192.168.1.1/kodi/sync/bookmark.db"
destination_dir2 = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db')
xbmcvfs.copy(source_dir2, destination_dir2)

pDialog.update(100, 'DATABASE OK, Rechargement des données en cours...')
xbmc.sleep(2000)
pDialog.close()

xbmc.executebuiltin('ReloadSkin')
sys.exit()