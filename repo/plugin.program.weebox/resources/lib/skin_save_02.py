#!/usr/bin/python3
# creation initiale par osmoze06 le 09 10 21
import shutil
import xbmc
import xbmcvfs
import os, sys, stat

xbmc.executebuiltin("Notification(PREPARATION DES FICHIERS,Copie en cours...)")

# COPIE DES DOSSIERS ET FICHIERS DU SKIN
source_dir = xbmcvfs.translatePath('special://home/userdata/addon_data/skin.arctic.horizon.2')
destination_dir = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addon_data/skin.arctic.horizon.2')

source_dir1 = xbmcvfs.translatePath('special://home/userdata/addon_data/script.skinshortcuts')
destination_dir1 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addon_data/script.skinshortcuts')

source_dir2 = xbmcvfs.translatePath('special://home/userdata/guisettings.xml')
destination_dir2 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/guisettings.xml')

#source_dir3 = xbmcvfs.translatePath('special://home/addons/skin.arctic.horizon.2/extras/icons')
#destination_dir3 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addons/skin.arctic.horizon.2/extras/icons')

source_dir4 = xbmcvfs.translatePath('special://home/addons/skin.arctic.horizon.2/1080i')
destination_dir4 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addons/skin.arctic.horizon.2/1080i')

source_dir5 = xbmcvfs.translatePath('special://home/addons/skin.arctic.horizon.2/fonts')
destination_dir5 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addons/skin.arctic.horizon.2/fonts')


shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
shutil.copytree(source_dir1, destination_dir1, dirs_exist_ok=True)
#shutil.copytree(source_dir3, destination_dir3, dirs_exist_ok=True)
shutil.copytree(source_dir4, destination_dir4, dirs_exist_ok=True)
shutil.copytree(source_dir5, destination_dir5, dirs_exist_ok=True)
shutil.copy(source_dir2, destination_dir2)


# CREATION ARCHIVE ZIP
shutil.make_archive((xbmcvfs.translatePath('special://home/downloads/skin_save/skin.arctic.horizon.2')),'zip',(xbmcvfs.translatePath('special://home/downloads/skin_save/01')))

xbmc.executebuiltin("Notification(SKIN SAUVEGARDE, Archive ZIP créée !)")
sys.exit()