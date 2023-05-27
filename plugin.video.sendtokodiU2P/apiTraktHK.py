import sys, os
import json
import requests
import datetime
import time
import io
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import widget
from util import notice

ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")

class ApiTrakt:

    def __init__(self, **kwargs):
        self.client_id = ""
        self.client_secret = ""
        self.access_token = ""
        self.refresh_token = ""
        self.pincode = ""
        self.baseurl = 'https://api.trakt.tv'
        self.config_parser = ''
        self.config_path = ""
        self.keyExpire = "0"
        self.dictUsers = {}
        self.tabmedia = []
        self.d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        for attr_name, attr_value in kwargs.items():
            setattr(self, attr_name, attr_value)

        if self.client_id and self.client_secret:
            if self.keyExpire:
                if ((int(self.keyExpire) - time.time()) < 0 and self.refresh_token):
                    self.refreshToken()
        self.headers = {
                'Accept'            : 'application/json',   # required per API
                'Content-Type'      : 'application/json',   # required per API
                'User-Agent'        : 'Tratk importer',     # User-agent
                'Connection'        : 'Keep-Alive',         # Thanks to urllib3, keep-alive is 100% automatic within a session!
                'trakt-api-version' : '2',                  # required per API
                'trakt-api-key'     : self.client_id,                   # required per API
                'Authorization'     : 'Bearer %s' %self.access_token,                   # required per API
            }


    def refreshToken(self):
        url = self.baseurl + '/oauth/token'
        values = {
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "grant_type": "refresh_token"
            }
        request = requests.post(url, data=values)
        response = request.json()
        self.access_token = response["access_token"]
        self.refresh_token = response['refresh_token']
        self.keyExpire =  int(response["created_at"]) + int(response["expires_in"])

    def getUserlists(self, userlist, page=1):
        self.dictUsers = {}
        url = self.baseurl + '/users/{user}/lists'.format(
                            user=userlist, page=page, limit=1000)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        listes = json.loads(r.text)
        self.dictUsers[userlist] = {liste["ids"]["slug"]: (liste["ids"]["trakt"], liste["name"], liste['item_count'], liste["user"]["ids"]["slug"], liste["user"]["username"]) for liste in listes}
        return self.dictUsers

    def getUserListsLight(self, userlist, page=1):
        self.dictUsers = {}
        url = self.baseurl + '/users/{user}/lists/?description={desc}'.format(
                            user=userlist, page=page, limit=1000, desc=self.d)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        try:
            listes = json.loads(r.text)
            self.dictUsers[userlist] = {liste["name"]: (liste["user"]["ids"]["slug"], liste["ids"]["slug"], liste["name"], liste['item_count']) for liste in listes}
        except:
            self.dictUsers = {}
        return self.dictUsers

    def getList(self, userlist, numList, nomList, typMedia="movies", page=1):
        url = self.baseurl + '/users/{user}/lists/{list_id}/items/{type}?page={page}&limit={limit}'.format(
                            user=userlist, list_id=numList, type=typMedia, page=page, limit=1000)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        listeMedias = json.loads(r.text)
        for media in listeMedias:
            typ = media["type"]
            self.tabmedia.append(media[typ]["ids"]['tmdb'])
        if 'X-Pagination-Page-Count' in r.headers and r.headers['X-Pagination-Page-Count']:
            print("Recup page {page} of {PageCount} pages for num {list} list".format(
                    page=page, PageCount=r.headers['X-Pagination-Page-Count'], list=numList))
            if page != int(r.headers['X-Pagination-Page-Count']):
                getList(userlist, numList, nomList, typMedia=typMedia, page=page + 1)

    def getListId(self, numList):
        url = self.baseurl + '/lists/{list_id}/items/?limit={nb}&description={desc}'.format(
                            list_id=numList[0], nb=numList[0], desc=self.d)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        listeMedias = json.loads(r.text)
        return listeMedias

    def extractList(self, user, nomList, typMedia="movies"):
        self.getUserlists(user)
        self.tabmedia = []
        try:
            self.getList(user, self.dictUsers[user][nomList][0], self.dictUsers[user][nomList][1], typMedia)
        except Exception as e:
            print("err", e)
            print("liste User")
            print(self.dictUsers[user])
        return self.tabmedia

    def extractListsUser(self, name):
        listsUser = []
        user = self.getUserlists(name)
        for nom, listes in user.items():
            for nomListe, liste in listes.items():
                username, name, num = liste[-1], liste[1], liste[0]
                medias = self.getListId(num)
                tabTMDB = []
                for media in medias:
                    typ = media["type"]
                    tabTMDB.append(media[typ]["ids"]["tmdb"])
                listsUser.append((username, typ, name, tabTMDB))
        return listsUser

    def getToken(self):
        values = {
            "client_id": self.client_id
                 }
        headers = {
            'Content-Type'      : 'application/json'
                }

        url = self.baseurl + '/oauth/device/code'
        request = requests.post(url, data=json.dumps(values), headers=headers)
        r = request.json()
        return r["device_code"], r["user_code"], r["verification_url"]

    def getToken2(self, device_code):
        headers = {
            'Content-Type'      : 'application/json'
        }

        values = {
            "code": device_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
                }

        url = self.baseurl + '/oauth/device/token'
        request = requests.post(url, data=json.dumps(values), headers=headers)
        r = request.json()
        return r

    def getUserListsLikes(self, userlist):
        self.dictUsers = {}
        url = self.baseurl + '/users/{user}/likes/?description={desc}&limit=50'.format(
                            user=userlist, desc=self.d)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        listes = json.loads(r.text)
        self.dictUsers[userlist] = {liste["list"]["name"]: (liste["list"]["ids"]["trakt"], liste["list"]["item_count"]) for liste in listes if liste['type'] == "list" }
        return self.dictUsers

    def getUserWatchlist(self, userlist, typM="movies"):
        """shows or movies"""
        self.dictUsers = {}
        url = self.baseurl + '/users/{user}/watchlist/{typM}/?description={desc}'.format(
                            user=userlist, typM=typM, desc=self.d)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        listes = json.loads(r.text)
        tabId = [liste[typM[:-1]]["ids"]["tmdb"] for liste in listes if liste]
        return tabId

    def extractListsIdUser(self, name=""):
        if not name:
            name= "me"
        user = self.getUserlists(name)
        for nom, listes in user.items():
            dictListe = {liste[1]: (liste[0], liste[2]) for nomListe, liste in listes.items()}
        return {nom: dictListe}

    def recommendations(self, user, typM="movies"):
        url = self.baseurl + '/recommendations/{typM}/?limit=100'.format(
                            typM=typM)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        listes = json.loads(r.text)
        tabId = [liste["ids"]["tmdb"] for liste in listes if liste]
        return tabId

    def scrobble(self, title="", year=0, numId="", pos=0.0, season=1, number=1, typM="movie", mode="start"):
        d = datetime.datetime.now().strftime("%Y-%m-%d")
        values = {
            "progress": pos,
            "app_version": "1.0",
            "app_date": d
                }
        if typM == "movie":
            values["movie"] = {"title": title, "year": year, "ids": {"tmdb": numId}}
        else:
            values["show"] = {"title": title, "year": year, "ids": {"tmdb": numId}}
            values["episode"] = {"season": season, "number": number}
        if mode == "start":
            url = self.baseurl + '/scrobble/start'
        else:
            url = self.baseurl + '/scrobble/stop'
        request = requests.post(url, data=json.dumps(values), headers=self.headers)
        r = self.getDataJson(url, values)
        return r

    def getDataJson(self, url, values, nbTest=1):
        """reconnection error json"""
        try:
            r = requests.post(url, data=json.dumps(values), headers=self.headers)
            data = json.loads(r.text)
        except :
            time.sleep(0.5 * nbTest)
            notice("tentative reconnection : %.2fs" % (0.5 * nbTest))
            nbTest += 1
            if nbTest > 10:
                notice("error: reconnection")
                sys.exit()
            return self.getDataJson(url, values, nbTest)
        else:
            return data

    def getDataJsonGet(self, url, nbTest=1):
        """reconnection error json"""
        try:
            r = requests.get(url, headers=self.headers)
            data = json.loads(r.text)
        except :
            time.sleep(0.5 * nbTest)
            notice("tentative reconnection : %.2fs" % (0.5 * nbTest))
            nbTest += 1
            if nbTest > 10:
                notice("error: reconnection")
                sys.exit()
            return self.getDataJson(url, nbTest)
        else:
            return data

    def gestionWatchlist(self, numId=[], season=None, number=[], typM="movie", mode="add"):
        """mode add/remove  typm movie/show
        ajpute ou retire de la watchlist"""
        values = {}
        if typM == "movie":
            values["movies"] = [{"ids": {"tmdb": x}} for x in numId]
        else:
            if season and number:
                values["shows"] = [{"ids": {"tmdb": numId[0]}, "seasons" :[{"number": season, "episodes": [{"number": x} for x in number]}]}]
            else:
                values["shows"] = [{"ids": {"tmdb": x}} for x in numId]
        if mode == "add":
            url = self.baseurl + '/sync/watchlist'
        else:
            url = self.baseurl + '/sync/watchlist/remove'
        request = requests.post(url, data=json.dumps(values), headers=self.headers)
        r = request.json()
        notice(r)

    def gestionWatchedHistory(self, numId=[], season=None, number=[], typM="movie", mode="add"):
        """mode add/remove  typm movie/show
        met vu ou non vue"""
        values = {}
        if typM == "movie":
            values["movies"] = [{"ids": {"tmdb": x}} for x in numId]
        else:
            if season and number:
                values["shows"] = [{"ids": {"tmdb": numId[0]}, "seasons" :[{"number": season, "episodes": [{"number": x} for x in number]}]}]
            else:
                values["shows"] = [{"ids": {"tmdb": x}} for x in numId]
        if mode == "add":
            url = self.baseurl + '/sync/history'
        else:
            url = self.baseurl + '/sync/history/remove'
        notice(values)
        notice(url)
        request = requests.post(url, data=json.dumps(values), headers=self.headers)
        r = request.json()

    def history(self, typM="movies"):
        """recup historique des vus"""
        dStart = "2015-06-01T00:00:00.000Z"
        d = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:00.000Z")
        url = self.baseurl + '/sync/history/{typM}?start_at={dstart}&end_at={dstop}&limit=10000'.format(
                            typM=typM, dstart=dStart, dstop=d)
        r = requests.get(url, headers=self.headers, timeout=(5, 60))
        listes = json.loads(r.text)
        if typM == "movies":
            tabId = [liste[typM[:-1]]["ids"]["tmdb"] for liste in listes if liste and liste[typM[:-1]]["ids"]["tmdb"]]
        else:
            tabId = [(liste[typM[:-1]]["ids"]["tmdb"], liste["episode"]["season"], liste["episode"]["number"]) for liste in listes if liste and liste[typM[:-1]]["ids"]["tmdb"]]
        return tabId

def showInfoNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message, xbmcgui.NOTIFICATION_INFO, 5000)

class TraktHK(ApiTrakt):

    def __init__(self):
        cfg = {
            "client_id": ADDON.getSetting("clientid").strip(),
            "client_secret": ADDON.getSetting("clientsecret").strip(),
            "access_token": ADDON.getSetting("clientacces").strip(),
            "refresh_token": ADDON.getSetting("clientrefresh").strip(),
            "keyExpire": ADDON.getSetting("clientexpire").strip(),
            }
        ApiTrakt.__init__(self, **cfg)
        if not cfg["access_token"]:
            device, code, url = self.getToken()
            if device:
                dialog = xbmcgui.Dialog()
                ok = dialog.yesno('Validation device Trakt', "Valides le code %s\nsur la page %s\nQuand c'est fait, click sur OUI" %(code, url))
                if ok:
                    response = self.getToken2(device)
                    access_token = response["access_token"]
                    refresh_token = response['refresh_token']
                    keyExpire = int(response["created_at"]) + int(response["expires_in"])
                    ADDON.setSetting("clientacces", access_token)
                    ADDON.setSetting("clientrefresh", refresh_token)
                    ADDON.setSetting("clientexpire", str(keyExpire))
                else:
                    return
        else:
            ADDON.setSetting("clientacces", self.access_token)
            ADDON.setSetting("clientrefresh", self.refresh_token)
            ADDON.setSetting("clientexpire", str(self.keyExpire))

    def importListes(self, typM="movie"):
        dialog = xbmcgui.Dialog()
        d = dialog.input("User Trakt (exemple: alKODIque):", type=xbmcgui.INPUT_ALPHANUM)
        if d:
            dictListes = self. getUserListsLight(d)
            if dictListes:
                choix = list(dictListes[d].keys())
                dialog = xbmcgui.Dialog()
                chListes = dialog.multiselect("Selectionner la/les liste(s) à importer", choix, preselect=[])
                if chListes:
                    tabListe = [dictListes[d][x] for i, x in enumerate(choix) if i in chListes]
                    listeRep = list(widget.getListesT("movie"))
                    listeGroupes = ["Nouveau"] + list(set([x[3] for x in listeRep]))
                    dialog = xbmcgui.Dialog()
                    ret = dialog.select("Insérer dans le groupe: ", listeGroupes)
                    if ret != -1:
                        if ret == 0:
                            d = dialog.input("Nom du Groupe", type=xbmcgui.INPUT_ALPHANUM)
                            if d:
                                groupe = d
                            else:
                                return
                        else:
                            groupe = listeGroupes[ret]
                        [widget.insertTrakt(*(x[0], x[1], typM, groupe, x[2])) for x in tabListe]
                        showInfoNotification("Création listes ok!!")







