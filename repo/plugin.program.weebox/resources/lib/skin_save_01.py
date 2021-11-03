#!/usr/bin/python3
# creation initiale par osmoze06 le 09 10 21
import shutil
import xbmc
import sys

xbmc.executebuiltin("Notification(PREPARATION DES FICHIERS,Copie en cours...)")

# COPIE DES DOSSIERS ET FICHIERS DU SKIN
source_dir = xbmc.translatePath('special://home/userdata/addon_data/skin.project.aura')
destination_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01/addon_data/skin.project.aura')

source_dir1 = xbmc.translatePath('special://home/userdata/addon_data/script.skinshortcuts')
destination_dir1 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01/addon_data/script.skinshortcuts')

source_dir2 = xbmc.translatePath('special://home/addons/skin.project.aura/1080i/script-skinshortcuts-includes.xml')
destination_dir2 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01/addons/skin.project.aura/1080i/script-skinshortcuts-includes.xml')

shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
shutil.copytree(source_dir1, destination_dir1, dirs_exist_ok=True)
shutil.copy(source_dir2, destination_dir2)

# CREATION ARCHIVE ZIP
shutil.make_archive((xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01/skin_save_01')),'zip',(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01')))

xbmc.executebuiltin("Notification(SKIN SAUVEGARDE, SLOT 01 - Archive ZIP créée !)")
sys.exit()