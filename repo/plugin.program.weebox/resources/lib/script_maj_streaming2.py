# -*- coding: ISO-8859-1 -*-
import xbmc
import xbmcvfs
import xbmcgui
import urllib.request
import shutil

#ACTUALISATION FICHIERS CONFIGURATION U2P

settings_download = 'http://localhost/libreelec/clients/HOME_Localhost/SETTINGS_U2P/settings.xml'
settings_loc = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/settings.xml')

#db_download = 'http://localhost/libreelec/clients/HOME_Localhost/SETTINGS_U2P/bookmark.db'
#db_loc = xbmc.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db')

urllib.request.urlretrieve(settings_download, settings_loc)
#urllib.request.urlretrieve(db_download, db_loc)

xbmc.executebuiltin("Notification(EXTRACTION OK,Mise à jour des paramètres effectuée !)")
xbmc.sleep(2000)

#MISE A JOUR ZIP U2P

pDialog = xbmcgui.DialogProgress()
pDialog.create('WEEBOX - MISES A JOUR', 'Initialisation des téléchargements des Extensions...')
xbmc.sleep(2000)

pDialog.update(50, 'STREAMING SERVICES \n\nplugin.video.sendtokodiU2P.zip')
url = 'http://localhost/libreelec/clients/addons/plugin.video.sendtokodiU2P.zip'
loc = xbmc.translatePath('special://home/downloads/updates/plugin.video.sendtokodiU2P.zip')
urllib.request.urlretrieve(url, loc)

pDialog.update(100, 'TELECHARGEMENT, Récupération archive ZIP effectuée...')
xbmc.sleep(2000)
pDialog.close()

DIALOG = xbmcgui.Dialog()

if __name__ == "__main__":
    response = DIALOG.yesno('INSTALLER LES MISES A JOUR ?', 'Choisir la source WEEBOX UPDATES et cliquer sur ce ZIP pour mettre a jour.\n\nplugin.video.sendtokodiU2P.zip', yeslabel='INSTALLER', nolabel='Quitter')

    if response:
        # call the script from with kodi
        xbmc.executebuiltin('installfromzip')

    else:
        xbmc.executebuiltin('ActivateWindow(10000,return)')
#xbmc.executebuiltin('RunScript(your_script)')
