import time
import xbmcaddon
import sys
import xbmcvfs
import sqlite3

pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor
if pyVersionM == 11:
    import cryptPaste11 as cryptage
    import scraperUPTO11 as scraperUPTO
elif pyVersionM == 8:
    import cryptPaste8 as cryptage
    import scraperUPTO8 as scraperUPTO
elif pyVersionM == 9:
    import cryptPaste9 as cryptage
    import scraperUPTO9 as scraperUPTO
elif pyVersionM == 10:
    import cryptPaste10 as cryptage
    import scraperUPTO10 as scraperUPTO

time.sleep(0.1)
addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
interval = int(addon.getSetting("intmaj"))
delaiMaj = int(addon.getSetting("delaimaj"))
#scraperUPTO.extractEpisodesOnContinue()
if interval:
    time.sleep(delaiMaj * 60)
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        actu = scraperUPTO.majHkNewStart()
        if monitor.waitForAbort(interval * 60):
            break