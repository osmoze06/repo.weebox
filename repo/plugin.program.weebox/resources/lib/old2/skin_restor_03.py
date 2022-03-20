#!/usr/bin/python3
# creation initiale par osmoze06 le 09 10 21
import xbmc
import shutil
import sys


# copie des fichiers sauvegarde
source_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/03/addon_data')
destination_dir = xbmc.translatePath('special://home/userdata/addon_data')

source_dir2 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/03/addons/skin.project.aura')
destination_dir2 = xbmc.translatePath('special://home/addons/skin.project.aura')

shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
shutil.copytree(source_dir2, destination_dir2, dirs_exist_ok=True)

xbmc.executebuiltin("Notification(COPIE OK,Mise à jour effectuée !)")
xbmc.sleep(5000)

# ACTUALISATION DU SKIN
xbmc.executebuiltin("Notification(ACTUALISATION DU SKIN, Sauvegarde SLOT 03...)")
xbmc.sleep(2000)
xbmc.executebuiltin('ReloadSkin')
sys.exit()