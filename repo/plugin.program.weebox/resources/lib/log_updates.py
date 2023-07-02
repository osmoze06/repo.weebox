import xbmcgui
import os
import xbmcvfs
import sys
import urllib.request


# Téléchargement du fichier texte
sources_download = 'http://localhost/libreelec/clients/log_updates.txt'											
sources_loc = xbmcvfs.translatePath('special://home/downloads/log_updates.txt')											
urllib.request.urlretrieve(sources_download, sources_loc)

# Chemin vers le fichier texte
path = xbmcvfs.translatePath('special://home/downloads/log_updates.txt')

# Lecture du contenu du fichier avec l'encodage utf-8
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Création de la fenêtre Kodi
dialog = xbmcgui.Dialog()
dialog.textviewer('[COLOR deepskyblue]WEEBOX[/COLOR] - MISE A JOUR', content)

sys.exit()