import xbmcaddon
import xbmcgui
import xbmc
import sys

addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
version = addon.getAddonInfo('version')
latest_version = "0.9.15"
name = addon.getAddonInfo('name')
kodi_version = xbmc.getInfoLabel("System.BuildVersion")

if version == latest_version:
    message = "Extension Streaming - Version : " +"[COLOR deepskyblue]" + version + "[/COLOR]" + "\nPropulsé par KODI - Version : " +"[COLOR deepskyblue]" + kodi_version + "[/COLOR]" + "[COLOR greenyellow]\n\nL'extension est à jour, version actuelle : [/COLOR]"+ version
    xbmcgui.Dialog().ok("WEEBOX INFORMATION : VERSIONS", message)
else:
    xbmc.executebuiltin('UpdateAddon(plugin.video.sendtokodiU2P)')
    xbmcgui.Dialog().notification("WEEBOX INFORMATION : VERSIONS", "Mise à jour terminée", xbmcgui.NOTIFICATION_INFO, 5000)
    new_version = addon.getAddonInfo('version') #get the new version
    message = "Extension Streaming - Version : " +"[COLOR deepskyblue]" + new_version + "[/COLOR]" + "\nPropulsé par KODI - Version : " +"[COLOR deepskyblue]" + kodi_version + "[/COLOR]" + "[COLOR greenyellow]\n\nL'extension a été mise à jour en version : [/COLOR]"+ version
    xbmcgui.Dialog().ok("VERSION A JOUR", message)

sys.exit()