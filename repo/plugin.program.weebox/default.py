import xbmcgui
import xbmcplugin
import subprocess

# Liste des scripts à exécuter avec leurs noms affichés dans le menu
scripts = [
    {"name": "INFORMATIONS", "script": "special://home/addons/service.autoexec/script_infos.py", "icon": "special://skin/extras/icons/year.png", "fanart": "special://skin/extras/icons/fanart_script1.jpg"},
    {"name": "Script 2", "script": "special://home/addons/service.autoexec/script2.py", "icon": "special://skin/extras/icons/icone_script2.png", "fanart": "special://skin/extras/icons/fanart_script2.jpg"},
    {"name": "Script 3", "script": "special://home/addons/service.autoexec/script3.py", "icon": "special://skin/extras/icons/icone_script3.png", "fanart": "special://skin/extras/icons/fanart_script3.jpg"},
]

# Fonction pour exécuter le script sélectionné
def run_script(script_path):
    try:
        subprocess.Popen(["python", script_path])
    except Exception as e:
        xbmcgui.Dialog().ok("Erreur", str(e))

# Fonction principale pour créer le menu
def create_menu():
    xbmcplugin.setPluginCategory(handle=int(sys.argv[1]), category="Scripts")
    xbmcplugin.setContent(handle=int(sys.argv[1]), content="files")

    for script in scripts:
        list_item = xbmcgui.ListItem(label=script["name"])
        list_item.setArt({'icon': script["icon"], 'fanart': script["fanart"]})
        url = "{}/run_script/{}".format(sys.argv[0], script["script"])
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=False)

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

# Point d'entrée de l'addon
if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "run_script":
            script_path = sys.argv[2]
            run_script(script_path)
    else:
        create_menu()