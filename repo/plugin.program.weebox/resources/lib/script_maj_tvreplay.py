#!/usr/bin/python3
import xbmc
import xbmcvfs
import xbmcgui
import urllib.request
import shutil


pDialog = xbmcgui.DialogProgress()
pDialog.create('WEEBOX - MISES A JOUR', 'Initialisation des téléchargements des Extensions...')
xbmc.sleep(2000)

pDialog.update(50, 'TV & REPLAY SERVICES \n\nplugin.video.catchuptvandmore-dev.zip')
#url = 'http://weeclic.ddns.net/libreelec/clients/addons/plugin.video.sendtokodiU2P.zip'
url = 'https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore/archive/refs/heads/dev.zip'
loc = xbmc.translatePath('special://home/downloads/updates/plugin.video.catchuptvandmore-dev.zip')
urllib.request.urlretrieve(url, loc)

pDialog.update(100, 'TELECHARGEMENT, Récupération archive ZIP effectuée...')
xbmc.sleep(2000)
pDialog.close()

#dialog = xbmcgui.Dialog()
#i = dialog.ok("MISE A JOUR DU 27/02/2022","STREAMING :\n\n- Tri Liste Séries Documentaire\n- Amélioration de la Recherche\n- Retrait Time 70 secondes par défaut (Up Next)\n- Retrait Actualisation Skin en Auto-Update\n- Texte par défaut si Synopsis absent\nTV ET REPLAY :\n- Replay RMC BFM (compte à renseigner)\n- Chaînes RMC BFM Live fonctionnelles")

DIALOG = xbmcgui.Dialog()

if __name__ == "__main__":
    response = DIALOG.yesno('INSTALLER LES MISES A JOUR ?', 'Choisir la source WEEBOX UPDATES et cliquer sur ce ZIP pour mettre a jour.\n\nplugin.video.catchuptvandmore-dev.zip', yeslabel='INSTALLER', nolabel='Quitter')

    if response:
        # call the script from with kodi
        xbmc.executebuiltin('installfromzip')

    else:
        xbmc.executebuiltin('ActivateWindow(10000,return)')
#xbmc.executebuiltin('RunScript(your_script)')