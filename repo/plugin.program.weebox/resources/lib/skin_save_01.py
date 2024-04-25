#!/usr/bin/python3
# création initiale par osmoze06 le 09 10 21
import shutil
import xbmc
import xbmcvfs
import os, sys, stat

xbmc.executebuiltin("Notification(PREPARATION DES FICHIERS,Nettoyage...)")

# Suppression du dossier temporaire
dirPath = xbmcvfs.translatePath('special://home/downloads/skin_save/01/')
try:
    shutil.rmtree(dirPath)
except:
    print('Error while deleting directory')

xbmc.executebuiltin("Notification(PREPARATION DES FICHIERS,Copie en cours...)")

# COPIE DES DOSSIERS ET FICHIERS DU SKIN
source_dir1 = xbmcvfs.translatePath('special://home/userdata/addon_data/skin.arctic.fuse')
destination_dir1 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addon_data/skin.arctic.fuse')

source_dir2 = xbmcvfs.translatePath('special://home/userdata/addon_data/script.skinvariables')
destination_dir2 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addon_data/script.skinvariables')

source_dir3 = xbmcvfs.translatePath('special://home/addons/skin.arctic.fuse/1080i')
destination_dir3 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addons/skin.arctic.fuse/1080i')

source_dir4 = xbmcvfs.translatePath('special://home/addons/skin.arctic.fuse/fonts')
destination_dir4 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addons/skin.arctic.fuse/fonts')

source_dir5 = xbmcvfs.translatePath('special://home/addons/skin.arctic.fuse/extras/icons')
destination_dir5 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addons/skin.arctic.fuse/extras/icons')

source_dir6 = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.program.autowidget')
destination_dir6 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addon_data/plugin.program.autowidget')

source_file1 = xbmcvfs.translatePath('special://home/userdata/advancedsettings.xml')
destination_file1 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/advancedsettings.xml')

source_file2 = xbmcvfs.translatePath('special://home/addons/resource.language.fr_fr/resources/strings.po')
destination_file2 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/language_kodi/strings.po')

source_file3 = xbmcvfs.translatePath('special://home/addons/skin.arctic.fuse/language/resource.language.fr_fr/strings.po')
destination_file3 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/language_skin/strings.po')

# Création des répertoires language_kodi et language_skin s'ils n'existent pas
os.makedirs(os.path.dirname(destination_file2), exist_ok=True)
os.makedirs(os.path.dirname(destination_file3), exist_ok=True)

shutil.copytree(source_dir1, destination_dir1, dirs_exist_ok=True)
shutil.copytree(source_dir2, destination_dir2, dirs_exist_ok=True)
shutil.copytree(source_dir3, destination_dir3, dirs_exist_ok=True)
shutil.copytree(source_dir4, destination_dir4, dirs_exist_ok=True)
shutil.copytree(source_dir5, destination_dir5, dirs_exist_ok=True)
shutil.copytree(source_dir6, destination_dir6, dirs_exist_ok=True)
shutil.copy(source_file1, destination_file1)
shutil.copy(source_file2, destination_file2)
shutil.copy(source_file3, destination_file3)


# CREATION ARCHIVE ZIP
shutil.make_archive((xbmcvfs.translatePath('special://home/downloads/skin_save/skin.arctic.fuse')),'zip',(xbmcvfs.translatePath('special://home/downloads/skin_save/01')))

xbmc.executebuiltin("Notification(SKIN SAUVEGARDE, Archive ZIP créée !)")
sys.exit()