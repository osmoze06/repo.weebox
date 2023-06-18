import xbmcgui
import os
import xbmcvfs

# Chemin vers le fichier texte
path = xbmcvfs.translatePath('special://home/addons/plugin.program.weebox/resources/lib/weebox_news.txt')

# Lecture du contenu du fichier avec l'encodage utf-8
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Création de la fenêtre Kodi
dialog = xbmcgui.Dialog()
dialog.textviewer('[COLOR deepskyblue]WEEBOX[/COLOR] - INFORMATIONS', content)