#!/usr/bin/python3
# creation initial par osmoze06 le 09 10 21
import shutil
import xbmc
import sys

xbmc.executebuiltin("Notification(PREPARATION DES FICHIERS,Copie en cours...)")

# COPIE DES DOSSIERS ET FICHIERS DU SKIN
source_dir = xbmc.translatePath('special://home/userdata/addon_data/skin.project.aura')
destination_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/02/addon_data/skin.project.aura')

source_dir1 = xbmc.translatePath('special://home/userdata/addon_data/script.skinshortcuts')
destination_dir1 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/02/addon_data/script.skinshortcuts')

source_dir2 = xbmc.translatePath('special://home/addons/skin.project.aura/1080i/script-skinshortcuts-includes.xml')
destination_dir2 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/02/addons/skin.project.aura/1080i/script-skinshortcuts-includes.xml')

source_dir3 = xbmc.translatePath('special://home/addons/skin.project.aura/extras/icons')
destination_dir3 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01/addons/skin.project.aura/extras/icons')


shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
shutil.copytree(source_dir1, destination_dir1, dirs_exist_ok=True)
shutil.copytree(source_dir3, destination_dir3, dirs_exist_ok=True)
shutil.copy(source_dir2, destination_dir2)

# CREATION ARCHIVE ZIP
shutil.make_archive((xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/skin_save_02')),'zip',(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/02')))

xbmc.executebuiltin("Notification(SKIN SAUVEGARDE, SLOT 02 - Archive ZIP créée !)")
sys.exit()