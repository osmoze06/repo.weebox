import xbmcaddon
import xbmcgui
import xbmcplugin
from lib.tmdb import TMDB
import os
import xbmc
import json

# Récupération de la clé API de TMDB depuis le fichier settings.xml
ADDON = xbmcaddon.Addon()
API_KEY = ADDON.getSetting("api_key")

# Initialisation de la classe TMDB avec la clé API
tmdb = TMDB(API_KEY)

# Recherche de tous les widgets dans Kodi
list_items = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["widgetcontainers"]},"id":1}')

# Traitement de la réponse JSON
if 'result' in list_items:
    containers = list_items['result']['widgetcontainers']

    # Parcours de tous les widgets trouvés
    for container in containers:
        widgets = container['widgets']
        for widget in widgets:
            # Vérification que le widget contient du texte
            if 'text' in widget:
                title = widget['text']

                # Récupération du clearlogo correspondant depuis l'API de TMDB
                clearlogo_url = tmdb.get_clearlogo(title)

                # Remplacement du titre par le clearlogo dans le widget
                if clearlogo_url:
                    widget['image'] = clearlogo_url
                    widget['text'] = ""

    # Envoi des modifications de widgets à Kodi
    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.SetProperties","params":{"widgetcontainers":' + json.dumps(containers) + '},"id":1}')
