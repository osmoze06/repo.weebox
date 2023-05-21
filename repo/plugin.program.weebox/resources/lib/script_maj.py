#!/usr/bin/python3
import xbmc
import xbmcvfs
import xbmcgui
import urllib.request
import shutil
#import subprocess


pDialog = xbmcgui.DialogProgress()
pDialog.create('WEEBOX - MISES A JOUR', 'Initialisation des téléchargements des Extensions...')
xbmc.sleep(2000)

pDialog.update(50, 'KODI MATRIX 19.5\n\nkodi-19.5-Matrix-armeabi-v7a.apk')
#sources_download = 'https://ftp2.nluug.nl/mediaplayer/xbmc/releases/android/arm/kodi-19.5-Matrix-armeabi-v7a.apk'
sources_download = 'https://www.mirrorservice.org/sites/mirrors.xbmc.org/releases/android/arm/kodi-20.0-Nexus_rc2-armeabi-v7a.apk'
sources_loc = '/storage/emulated/0/Download/Weebox/kodi.apk'
urllib.request.urlretrieve(sources_download, sources_loc)

pDialog.update(100, 'TELECHARGEMENT, Récupération du fichier APK depuis le site officiel effectué.')
xbmc.sleep(2000)
pDialog.close()

#dialog = xbmcgui.Dialog()
#i = dialog.ok("MISE A JOUR DU 27/02/2022","STREAMING :\n\n- Tri Liste Séries Documentaire\n- Amélioration de la Recherche\n- Retrait Time 70 secondes par défaut (Up Next)\n- Retrait Actualisation Skin en Auto-Update\n- Texte par défaut si Synopsis absent\nTV ET REPLAY :\n- Replay RMC BFM (compte à renseigner)\n- Chaînes RMC BFM Live fonctionnelles")

DIALOG = xbmcgui.Dialog()

if __name__ == "__main__":
    response = DIALOG.yesno('INSTALLER LES MISES A JOUR ?', 'Choisir le dossier DOWNLOAD et cliquer sur le fichier APK pour installer.\n\nkodi-19.4-Matrix-armeabi-v7a.apk', yeslabel='INSTALLER', nolabel='Quitter')

    if response:
        # call the script from with kodi
        xbmc.executebuiltin('StartAndroidActivity(com.lonelycatgames.Xplore)')
        #xbmc.executebuiltin('StartAndroidActivity(com.weebox.kodiinstaller)')
		#subprocess.call("adb install /Download/Weebox/maj/kodi.apk")
        
    else:
        xbmc.executebuiltin('ActivateWindow(10000,return)')
#xbmc.executebuiltin('RunScript(your_script)')