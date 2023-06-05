#!/usr/bin/python3
# creation initial par osmoze06 le 09 10 21
# modifié par rayflix le 23 10 21
import xbmc
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import shutil
import os, sys, stat

#Supression lecture seule du fichier
os.chmod(xbmc.translatePath('special://home/userdata/addon_data/skin.cosmic/settings.xml'), stat.S_IWRITE)

xbmc.executebuiltin("Notification(MISE A JOUR SKIN,Téléchargement en cours...)")

# telechargement et extraction du zip
zipurl = 'https://github.com/osmoze06/skin_pack/raw/main/weebox_cosmic.zip'
with urlopen(zipurl) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
        zfile.extractall(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/maj/'))

# copie des fichiers extrais
source_dir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/maj/addon_data')
destination_dir = xbmc.translatePath('special://home/userdata/addon_data')
source_dir2 = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.weebox/skin_save/maj/addons/skin.cosmic')
destination_dir2 = xbmc.translatePath('special://home/addons/skin.cosmic')
shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
shutil.copytree(source_dir2, destination_dir2, dirs_exist_ok=True)

xbmc.executebuiltin("Notification(EXTRACTION OK,Mise à jour effectuée !)")
xbmc.sleep(2000)
xbmc.executebuiltin('ReloadSkin')
sys.exit()