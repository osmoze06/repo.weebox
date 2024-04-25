import xbmc
import xbmcvfs
import shutil
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

# Suppression du dossier temporaire
dirPath = xbmcvfs.translatePath('special://home/downloads/skin_save/01/')
try:
    shutil.rmtree(dirPath)
except:
    print('Error while deleting directory')

xbmc.executebuiltin("Notification(MISE A JOUR SKIN,Téléchargement en cours...)")

# telechargement et extraction du zip
zipurl = 'http://kbusuttil.free.fr/libreelec/skin/skin.arctic.fuse.zip'
with urlopen(zipurl) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
        zfile.extractall(xbmcvfs.translatePath('special://home/downloads/skin_save/01/'))

xbmc.executebuiltin("Notification(TELECHARGEMENT OK,Préparation...)")

# Désactiver l'addon autowidget
xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "plugin.program.autowidget", "enabled": false }}')
xbmc.sleep(3000)

# copie des fichiers extraits
source_dir1 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addon_data')
destination_dir1 = xbmcvfs.translatePath('special://home/userdata/addon_data')

source_dir2 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/addons/skin.arctic.fuse')
destination_dir2 = xbmcvfs.translatePath('special://home/addons/skin.arctic.fuse')

source_file1 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/guisettings.xml')
destination_file1 = xbmcvfs.translatePath('special://home/userdata/guisettings.xml')

source_file2 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/language_kodi/strings.po')
destination_file2 = xbmcvfs.translatePath('special://home/addons/resource.language.fr_fr/resources/strings.po')

source_file3 = xbmcvfs.translatePath('special://home/downloads/skin_save/01/language_skin/strings.po')
destination_file3 = xbmcvfs.translatePath('special://home/addons/skin.arctic.fuse/language/resource.language.fr_fr/strings.po')


shutil.copytree(source_dir1, destination_dir1, dirs_exist_ok=True)
shutil.copytree(source_dir2, destination_dir2, dirs_exist_ok=True)
shutil.copy(source_file1, destination_file1)
shutil.copy(source_file2, destination_file2)
shutil.copy(source_file3, destination_file3)

# Réactiver l'addon autowidget
xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "plugin.program.autowidget", "enabled": true }}')
xbmc.sleep(3000)

xbmc.executebuiltin("Notification(MISE A JOUR,Terminée !)")
xbmc.sleep(2000)
xbmc.executebuiltin('ReloadSkin')