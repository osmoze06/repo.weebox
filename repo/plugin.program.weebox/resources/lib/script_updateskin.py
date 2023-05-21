import xbmcgui
import urllib.request

message = "Voulez-vous télécharger la nouvelle interface pour votre WeeBox ?"
if xbmcgui.Dialog().yesno("Nouvelle Interface", message):
    url = "http://weeclic.ddns.net/libreelec/clients/KODI_WEEBOX.zip"
    file_name = "/storage/emulated/0/Download/KODI_WEEBOX.zip"
    progress = xbmcgui.DialogProgress()
    progress.create("Téléchargement", "Téléchargement en cours...")
    
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        message = "Téléchargement en cours... {}%".format(percent)
        progress.update(percent, message)
    
    urllib.request.urlretrieve(url, file_name, reporthook)
    progress.close()
    
    #message_run = "L'archive ZIP a été téléchargé, voulez-vous l'exécuter ?"
    #if xbmcgui.Dialog().yesno("Nouvelle Interface", message_run):
        #xbmc.executebuiltin('StartAndroidActivity(com.lonelycatgames.Xplore)')
        #xbmc.executebuiltin('StartAndroidActivity(com.rarlab.rar)')
else:
    xbmcgui.Dialog().notification("Téléchargement", "Le téléchargement de la nouvelle interface WeeBox a été annulé", xbmcgui.NOTIFICATION_WARNING, 5000)

message2 = "Voulez-vous télécharger WEEBOX Unzip ?"
if xbmcgui.Dialog().yesno("Nouvelle Interface", message2):
    url = "http://weeclic.ddns.net/libreelec/clients/WEEBOX_Unzip.apk"
    file_name = "/storage/emulated/0/Download/WEEBOX_Unzip.apk"
    progress = xbmcgui.DialogProgress()
    progress.create("Téléchargement", "Téléchargement en cours...")
    
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        message = "Téléchargement en cours... {}%".format(percent)
        progress.update(percent, message)
    
    urllib.request.urlretrieve(url, file_name, reporthook)
    progress.close()
    
    message_run = "L'application a été téléchargée, voulez-vous l'installer ?"
    if xbmcgui.Dialog().yesno("Nouvelle Interface", message_run):
        xbmc.executebuiltin('StartAndroidActivity(com.lonelycatgames.Xplore)')
        #xbmc.executebuiltin('StartAndroidActivity(com.rarlab.rar)')
else:
    xbmcgui.Dialog().notification("Téléchargement", "Le téléchargement de WEEBOX Unizip a été annulé", xbmcgui.NOTIFICATION_WARNING, 5000)