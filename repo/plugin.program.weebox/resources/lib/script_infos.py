#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-
import xbmc

url = 'http://weeclic.ddns.net/libreelec/clients/WBOX_INFOS.jpg'
xbmc.executebuiltin('ShowPicture('+url+')')
xbmc.sleep(10000)
xbmc.executebuiltin("Action(Back)")

#BOUCLE REFRESH ET RELANCE TOUTES LES 60 SECONDES
#while (1):
    #xbmc.executebuiltin('ShowPicture('+url+')')
    #xbmc.sleep(60000)