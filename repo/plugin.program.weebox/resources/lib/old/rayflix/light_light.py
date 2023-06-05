#!/usr/bin/python3
# creation initial par osmoze06 le 09 10 21
# modifié par rayflix le 23 10 21
import xbmc
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import shutil

xbmc.executebuiltin("Notification(PACK SKIN LIGHT,Téléchargement en cours...)")

# telechargement et extraction du zip
zipurl = 'https://github.com/rayflix76/pack/raw/kodi/light_light.zip'
with urlopen(zipurl) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
        zfile.extractall(xbmc.translatePath('special://home/temp/temp/'))

# copie des fichiers extraie
source_dir = xbmc.translatePath('special://home/temp/temp/addon_data')
destination_dir = xbmc.translatePath('special://home/userdata/addon_data')
source_dir2 = xbmc.translatePath('special://home/temp/temp/addons/skin.project.aura')
destination_dir2 = xbmc.translatePath('special://home/addons/skin.project.aura')
shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
shutil.copytree(source_dir2, destination_dir2, dirs_exist_ok=True)

xbmc.executebuiltin("Notification(EXTRACTION OK,Mise à jour effectuée !)")
xbmc.sleep(5000)

# actualisation du skin
xbmc.executebuiltin("Notification(ACTUALISATION DU SKIN, Pack Skin Light...)")
xbmc.sleep(2000)
xbmc.executebuiltin('ReloadSkin')