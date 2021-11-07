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
    add_dir("[COLOR deepskyblue] SKINS WEEBOX : SELECTIONNER UN SKIN A APPLIQUER[/COLOR]", '', 'call_save', artworkPath + 'skin0.png')
    add_dir("[COLOR green] SKIN PRINCIPAL : [/COLOR] Téléchargement et mise à jour du Skin principal.", 'pack_weebox_full', 'call_save', artworkPath + 'skin.png')
    add_dir("[COLOR deepskyblue] TV & REPLAY : [/COLOR] Téléchargement et application du Skin TV & REPLAY.", 'pack_weebox_tv', 'call_save', artworkPath + 'tv.png')
    add_dir("[COLOR deepskyblue] FILMS : [/COLOR] Téléchargement et application du Skin FILMS.", 'pack_weebox_films', 'call_save', artworkPath + 'films.png')
    add_dir("[COLOR deepskyblue] SERIES : [/COLOR] Téléchargement et application du Skin SERIES.", 'pack_weebox_series', 'call_save', artworkPath + 'series.png')
    add_dir("[COLOR deepskyblue] KIDS : [/COLOR] Téléchargement et application du Skin KIDS.", 'pack_weebox_series', 'call_save', artworkPath + 'kids.png')
    add_dir("[COLOR deepskyblue] DOCS & CONCERTS : [/COLOR] Téléchargement et application du Skin DOCS & CONCERTS.", 'pack_weebox_docs', 'call_save', artworkPath + 'docs.png')
    add_dir("------------------------------------------------------------------------------------------------------------------------------", '', 'call_save', artworkPath + 'icone.png')
    add_dir("[COLOR deepskyblue] SAUVEGARDE & RESTAURATION : SELECTIONNER UNE FONCTION[/COLOR]", '', 'call_save', artworkPath + 'save0.png')
    add_dir("[COLOR deepskyblue] SAUVEGARDER - SLOT 01 : [/COLOR] Sauvegarde du Skin en cours.", 'skin_save_01', 'call_save', artworkPath + 'save1.png')
    add_dir("[COLOR deepskyblue] SAUVEGARDER - SLOT 02 : [/COLOR] Sauvegarde du Skin en cours.", 'skin_save_02', 'call_save', artworkPath + 'save2.png')
    add_dir("[COLOR deepskyblue] SAUVEGARDER - SLOT 03 : [/COLOR] Sauvegarde du Skin en cours.", 'skin_save_03', 'call_save', artworkPath + 'save3.png')
    add_dir("[COLOR deepskyblue] RESTAURER - SLOT 01 : [/COLOR] Restauration du Skin sauvegardé.", 'skin_restor_01', 'call_save', artworkPath + 'restore1.png')
    add_dir("[COLOR deepskyblue] RESTAURER - SLOT 02 : [/COLOR] Restauration du Skin sauvegardé.", 'skin_restor_02', 'call_save', artworkPath + 'restore2.png')
    add_dir("[COLOR deepskyblue] RESTAURER - SLOT 03 : [/COLOR] Restauration du Skin sauvegardé.", 'skin_restor_03', 'call_save', artworkPath + 'restore3.png')
    add_dir("------------------------------------------------------------------------------------------------------------------------------", '', 'call_save', artworkPath + 'icone.png')	
    add_dir("[COLOR green] SPECIAL : [/COLOR] SELECTIONNER UNE FONCTION (EN COURS...) :", '', 'call_save', artworkPath + 'private0.png')    
    add_dir("[COLOR deepskyblue] VSTREAM : [/COLOR] >>> Upload de la Database sur Serveur.", 'upload_vstream_db', 'call_save', artworkPath + 'upload.png')
    add_dir("[COLOR deepskyblue] VSTREAM : [/COLOR] <<< Download de la Database du Serveur.", 'download_vstream_db', 'call_save', artworkPath + 'download.png')
    add_dir("[COLOR red] SKIN : [/COLOR] Sauvegarde du Skin en cours (ZIP sur Serveur).", '', 'call_save', artworkPath + 'save.png')
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