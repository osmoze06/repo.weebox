import xbmc
import xbmcvfs
import xbmcgui
import shutil
import os

pDialog = xbmcgui.DialogProgress()
pDialog.create('WEEBOX', 'UPLOAD DATABASE, Envoi de la Bibliothèque et historique vers le Serveur...')
xbmc.sleep(2000)
pDialog.update(50, 'Upload de la DATABASE en cours...')

source_dir1 = xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/medias.bd')
destination_dir1 = r"smb://KODI:Ongran2021@192.168.1.1/kodi/sync/medias.bd"
xbmcvfs.copy(source_dir1, destination_dir1)

source_dir2 = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db')
destination_dir2 = r"smb://KODI:Ongran2021@192.168.1.1/kodi/sync/bookmark.db"
xbmcvfs.copy(source_dir2, destination_dir2)

pDialog.update(100, 'DATABASE ENVOYEE, Fermeture en cours...')
xbmc.sleep(2000)
pDialog.close()

xbmc.executebuiltin('Quit')
sys.exit()