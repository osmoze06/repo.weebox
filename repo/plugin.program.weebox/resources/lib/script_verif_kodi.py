import xbmc
import xbmcgui
import urllib.request
import xbmcvfs

kodi_version = xbmc.getInfoLabel("System.BuildVersion")
latest_version = "20.1"

if kodi_version < latest_version:
    message = "Votre version de Kodi : " + kodi_version +"\nVoulez-vous télécharger la dernière version de Kodi ?"
    choice = xbmcgui.Dialog().yesno("Info Version Kodi", message)
    if choice:
        url = "https://ftp2.nluug.nl/mediaplayer/xbmc/releases/android/arm/kodi-20.1-Nexus-armeabi-v7a.apk"
        file_name = "/storage/emulated/0/Download/KODI.apk"
        progress = xbmcgui.DialogProgress()
        progress.create("Téléchargement", "Téléchargement en cours...")
        def reporthook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            message = "Téléchargement de {} en cours...".format(file_name)
            progress.update(percent, message)
        urllib.request.urlretrieve(url, file_name, reporthook)
        progress.close()
        message_run = "Le fichier APK a été téléchargé, voulez-vous l'exécuter ?"
        choice_run = xbmcgui.Dialog().yesno("Info Version Kodi", message_run)
        if choice_run:
            xbmc.executebuiltin('StartAndroidActivity(com.lonelycatgames.Xplore)')
    else:
        xbmcgui.Dialog().notification("Téléchargement", "Le téléchargement de la dernière version de Kodi a été annulé", xbmcgui.NOTIFICATION_WARNING, 5000)

else:
    message = "Votre version de Kodi : " + kodi_version + "\nVous utilisez la dernière version de Kodi"
    xbmcgui.Dialog().notification("Info Version Kodi", message, xbmcgui.NOTIFICATION_INFO, 5000)