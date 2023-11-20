import xbmc
import xbmcaddon
import sys
import urllib.request
import xbmcvfs

# Remplacez 'nom_du_referentiel' par le nom du référentiel que vous souhaitez ajouter.
repository_name = 'repository.vstream'

# Remplacez 'nom_de_l_addon' par le nom de l'addon que vous souhaitez installer à partir du référentiel.
addon_name = 'plugin.video.vstream'

xbmc.executebuiltin("Notification(INSTALLATION, Lancement)")

# Vérifiez si le référentiel est installé
if not xbmc.getCondVisibility('System.HasAddon(' + repository_name + ')'):
    xbmc.executebuiltin("Notification(INSTALLATION, Référentiel non installé, installation en cours)")
    # Installez le référentiel
    xbmc.executebuiltin('InstallAddon(' + repository_name + ')')
    
    # Attendez que le référentiel soit installé
    while not xbmc.getCondVisibility('System.HasAddon(' + repository_name + ')'):
        xbmc.sleep(1000)  # Attendre 1 seconde avant de vérifier à nouveau

# Le référentiel est installé, passez à l'installation de l'addon
xbmc.executebuiltin("Notification(INSTALLATION, Référentiel installé, installation de l'addon en cours)")

# Installez l'addon à partir du référentiel
xbmc.executebuiltin('InstallAddon(' + addon_name + ')')

# Attendez que l'addon soit installé
while not xbmc.getCondVisibility('System.HasAddon(' + addon_name + ')'):
    xbmc.sleep(1000)  # Attendre 1 seconde avant de vérifier à nouveau

# L'addon est installé, procédez au téléchargement des fichiers
xbmc.executebuiltin("Notification(INSTALLATION, Addon installé, téléchargements en cours)")

settings_download2 = 'http://weeclic.ddns.net/libreelec/clients/_SETTINGS_VSTREAM/settings.xml'
settings_loc2 = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.vstream/settings.xml')
urllib.request.urlretrieve(settings_download2, settings_loc2)

settings_download3 = 'http://weeclic.ddns.net/libreelec/clients/_SETTINGS_VSTREAM/sites.json'
settings_loc3 = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.vstream/sites.json')
urllib.request.urlretrieve(settings_download3, settings_loc3)

settings_download4 = 'http://weeclic.ddns.net/libreelec/clients/_SETTINGS_VSTREAM/pastebin_cache.db'
settings_loc4 = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.vstream/pastebin_cache.db')
urllib.request.urlretrieve(settings_download4, settings_loc4)

xbmc.executebuiltin("Notification(INSTALLATION, Téléchargements terminés)")
sys.exit()