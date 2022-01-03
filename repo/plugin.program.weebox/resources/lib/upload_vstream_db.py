import xbmc
import xbmcvfs
import xbmcgui
import shutil
import os

pDialog = xbmcgui.DialogProgress()
pDialog.create('WEEBOX', 'UPLOAD DATABASES, Bibliothèque Vidéos vers le Serveur...')
xbmc.sleep(2000)
pDialog.update(50, 'Upload de la DATABASE en cours - Prend environ 3 minutes...')

source_dir = xbmcvfs.translatePath('special://home/userdata/Database/MyVideos119.db')
#destination_dir = r"smb://MONITEUR:2929@192.168.1.10/laragon/kodi_sync/MyVideos119.db"
destination_dir = r"smb://KODI:Ongran2021@192.168.1.1/kodi/sync/MyVideos119.db"
xbmcvfs.copy(source_dir, destination_dir)

pDialog.update(100, 'DATABASE ENVOYEE, Fermeture en cours...')
xbmc.sleep(2000)
pDialog.close()

sys.exit()