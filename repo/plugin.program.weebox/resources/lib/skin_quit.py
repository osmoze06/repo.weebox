import xbmc
import shutil
import sys

# copie des fichiers sauvegarde
source_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01/addon_data')
destination_dir = xbmc.translatePath('special://home/userdata/addon_data')

source_dir2 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/01/addons/skin.cosmic')
destination_dir2 = xbmc.translatePath('special://home/addons/skin.cosmic')

shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
shutil.copytree(source_dir2, destination_dir2, dirs_exist_ok=True)

# ACTUALISATION DU SKIN
xbmc.executebuiltin("Notification(WEEBOX, Fermeture en cours...)")

xbmc.executebuiltin('Quit')
sys.exit()