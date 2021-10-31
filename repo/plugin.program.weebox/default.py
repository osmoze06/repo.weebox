# Module: default
# Author: Arias800, Osmoze06, Rayflix
# Created on: 25.10.2021
import sys
import xbmcplugin
import xbmcvfs
from urllib.parse import quote_plus, unquote_plus
import xbmcgui
import xbmc

artworkPath = xbmcvfs.translatePath('special://home/addons/plugin.program.weebox/resources/media/')
fanart = artworkPath + "fanart.jpg"

def add_dir(name, url, mode, thumb):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(name)
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': thumb})
    liz.setProperty("fanart_image", fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def main_menu():
    add_dir("[COLOR deepskyblue] OUTILS WEEBOX : [/COLOR] SELECTIONNER UNE FONCTION :", '', 'call_save', artworkPath + 'icone.png')
    add_dir("------------------------------------------------------------------------------------------------------------------------------", '', 'call_save', artworkPath + 'icone.png')	
    add_dir("[COLOR deepskyblue] VSTREAM : [/COLOR] >>> Upload de la Database sur Serveur.", 'upload_vstream_db', 'call_save', artworkPath + 'icone.png')
    add_dir("[COLOR deepskyblue] VSTREAM : [/COLOR] <<< Download de la Database du Serveur.", 'download_vstream_db', 'call_save', artworkPath + 'icone.png')
    add_dir("------------------------------------------------------------------------------------------------------------------------------", '', 'call_save', artworkPath + 'icone.png')
    add_dir("[COLOR deepskyblue] SKIN : [/COLOR] Mettre à jour le Skin.", 'pack_weebox', 'call_save', artworkPath + 'icone.png')
    add_dir("[COLOR deepskyblue] SKIN : [/COLOR] Sauvegarder du Skin en cours (ZIP en local).", 'skin_save_01', 'call_save', artworkPath + 'icone.png')
    add_dir("[COLOR red] SKIN : [/COLOR] Sauvegarder du Skin en cours (ZIP sur Serveur).", '', 'call_save', artworkPath + 'icone.png')
    add_dir("[COLOR red] SKIN : [/COLOR] Restauration du Skin sauvegardé (local).", '', 'call_save', artworkPath + 'icone.png')
    add_dir("------------------------------------------------------------------------------------------------------------------------------", '', 'call_save', artworkPath + 'icone.png')
	
def callSave(url):
    plugins = __import__('resources.lib.' + url)
    function = getattr(plugins, "load")
    function()

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params_l = sys.argv[2]
        cleanedparams = params_l.replace('?', '')
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

params = get_params()

try:
    mode = unquote_plus(params["mode"])
except:
    mode = None

try:
    url = unquote_plus(params["url"])
except:
    pass

if mode is None:
    main_menu()

elif mode == 'call_save':
    callSave(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))