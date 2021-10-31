#!/usr/bin/python3
# creation initial par osmoze06 le 09 10 21
# modifié par rayflix le 23 10 21
import xbmc
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import os
import shutil

xbmc.executebuiltin("Notification(OPTION DE VSTREAM,Effacement en cours...)")

# suppression du setting de vstream
# nous devrions vérifier si le fichier existe ou non avant de le supprimer.
if os.path.isfile(xbmc.translatePath('special://home/userdata/addon_data/plugin.video.vstream/settings.xml')):
    os.remove(xbmc.translatePath('special://home/userdata/addon_data/plugin.video.vstream/settings.xml'))
else:
    print("Impossible de supprimer le fichier car il n'existe pas")
xbmc.sleep(2000)

xbmc.executebuiltin("Notification(COMPTE 2,Téléchargement en cours...)")

# telechargement et extraction du zip
zipurl = 'https://github.com/rayflix76/pack/raw/kodi/cpt_mst2.zip'
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
xbmc.sleep(2000)
xbmc.executebuiltin("Notification(VOUS POUVEZ CHOISIR UN SKIN,Attention les skin full sont plus gourmand !)")