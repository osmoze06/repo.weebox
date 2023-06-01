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
    add_dir("WEEBOX_News", 'script_infos', 'call_save', artworkPath + 'download.png')
    add_dir("Version_Plugin" 'script_addon_infos.py', 'call_save', artworkPath + 'download.png')
    add_dir("Version_KODI", 'script_verif_kodi', 'call_save', artworkPath + 'download.png')
    add_dir("SCRIPT4", 'script_infos', 'call_save', artworkPath + 'download.png')    

def callSave(url):
    plugins = __import__('resources.lib.' + url)
    function = getattr(plugins, "load")
    function()

def get_params():
    param = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params_l = sys.argv[2]
        cleanedparams = params_l.replace('?', '')
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if len(splitparams) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

params = get_params()

try:
    mode = unquote_plus(params["mode"])
except KeyError:
    mode = None

try:
    url = unquote_plus(params["url"])
except KeyError:
    url = None

if mode is None:
    main_menu()
elif mode == 'call_save':
    if url is not None:
        callSave(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
