import xbmc
import xbmcaddon
import sys

# Remplacez 'nom_du_referentiel' par le nom du référentiel que vous souhaitez ajouter.
repository_name = 'repository.vstream'

# Remplacez 'nom_de_l_addon' par le nom de l'addon que vous souhaitez installer à partir du référentiel.
addon_name = 'plugin.video.vstream'

# Installez le référentiel
xbmc.executebuiltin('InstallAddon(' + repository_name + ')')

# Attendez quelques secondes pour que le référentiel soit installé.
xbmc.sleep(5000)

# Installez l'addon à partir du référentiel
xbmc.executebuiltin('InstallAddon(' + addon_name + ')')
xbmc.executebuiltin("Notification(INSTALLATION, Plugin)")
# Vous pouvez également redémarrer Kodi pour appliquer les modifications si nécessaire.
#xbmc.executebuiltin('RestartApp()')

sys.exit()