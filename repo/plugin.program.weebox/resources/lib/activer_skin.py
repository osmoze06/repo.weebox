import xbmc
import xbmcgui

# Fonction pour activer le skin Arctic Fuse
def activer_skin_arctic_fuse():
    # Chemin vers le skin Arctic Fuse
    chemin_skin = "special://skin/arctic.zephyr.fuse/"

    # Vérifier si le skin Arctic Fuse est déjà installé
    if xbmcvfs.exists(chemin_skin):
        # Activer le skin Arctic Fuse
        xbmc.setSkin(chemin_skin)
        xbmc.executebuiltin('Skin.Reset')
        xbmc.executebuiltin('Skin.SetString(skin.estuary.showfullscreen,false)')
        xbmc.executebuiltin('ReloadSkin()')
        xbmc.executebuiltin('Dialog.Close(busydialog)')

        xbmcgui.Dialog().ok("Succès", "Le skin Arctic Fuse a été activé avec succès!")
    else:
        xbmcgui.Dialog().ok("Erreur", "Le skin Arctic Fuse n'est pas installé!")

# Appel de la fonction pour activer le skin Arctic Fuse
activer_skin_arctic_fuse()