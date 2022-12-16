import requests
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
import os
import re
import io
import time
import sys
import unicodedata
import threading
import json
from medias import Media, TMDB
import sqlite3
from util import *
import widget
from apiTraktHK import TraktHK
pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor
if pyVersionM == 11:
    import cryptPaste11 as cryptage
    import scraperUPTO11 as scraperUPTO
elif pyVersionM == 8:
    #import pasteCrypt3 as cryptage
    import cryptPaste8 as cryptage
    import scraperUPTO8 as scraperUPTO
elif pyVersionM == 9:
    import cryptPaste9 as cryptage
    import scraperUPTO9 as scraperUPTO
else:
    import cryptPaste10 as cryptage
    import scraperUPTO10 as scraperUPTO
import ast

try:
    import xbmc
    import xbmcvfs
    import xbmcaddon
    import xbmcgui
    import xbmcplugin

    ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    KEYTMDB = ADDON.getSetting("apikey")
    HANDLE = int(sys.argv[1])
    BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmarkUptobox.db')
    BDFLDP = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mymedia.db')
    BDREPONEW = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasNew.bd')
    NBMEDIA = int(ADDON.getSetting("nbupto"))
except: pass

class RenameMedia:

    def extractInfo(self, name, typM="serie"):
        name = unquote(name)
        if typM == "movie":
            motif = r"""(?P<film>.*)([_\.\(\[ -]{1})(?P<an>19\d\d|20\d\d)([_\.\)\] -]{1})(.*)"""
            try:
                r = re.match(motif, name)
                title = r.group('film')
            except:
                title = name[:-4]
            try:
                year = int(r.group('an').replace('.', ''))
            except:
                year = 0
            if r:
                nameFinal = self.correctNom(title)
                nameFinal = nameFinal.replace(str(year), "")
            else:
                nameFinal = name

            return [nameFinal, year]

        else:
            for m in ["_", " ", "[", "]", "-", "(", ")", "{", "}"]:
                name = name.replace(m, ".")
            tab_remp = [r'''-|_|iNTERNAL|MULTi|2160p|4k|1080p|720p|480p|WEB-DL|hdlight|WEB|AC3|aac|hdtv|hevc|\d\dbit|subs?\.|vos?t?|x\.?265|STEGNER|x\.?264|FRENCH|DD\+.5.1|DD\+| |SR\.?71|h264|h265|1920x1080''', '.']
            name = re.sub(tab_remp[0], tab_remp[1], name, flags=re.I)
            name = re.sub(r"\.{2,}", ".", name)
            masque = r'(?P<year>19\d\d|20\d\d)'
            r = re.search(masque, name)
            if r:
                year = r.group("year")
            else:
                year = 0

            if year:
                name = name.replace(year, "")
            masques = [r'[sS](?P<saison>\d?\d)\.?(ep?)\.?(?P<episode>\d\d\d\d)\.',
                       r'[sS](?P<saison>\d?\d)\.?(ep?)\.?(?P<episode>\d?\d?\d)\.',
                       r'(?P<saison>\d?\d)\.?(x)\.?(?P<episode>\d?\d?\d)\.',
                       r'(\.)(ep?)\.?(?P<episode>\d?\d?\d)\.',
                       r'(part)\.?(?P<episode>\d)\.',
                       r'(dvd)\.?(?P<episode>\d)\.',
                       r'(Saison)\.?(?P<saison>\d?\d)\.?(Episode|e)\.?(?P<episode>\d?\d)\.',
                       r'[sS](?P<saison>\d?\d)\.?(ep?)\.?(?P<episode>\d?\d?\d)',
                       r'(ep?)\.?(?P<episode>[0-1][0-8]\d\d)\.',
                       r'(ep?)\.?(?P<episode>\d?\d?\d)',
                       r'(?P<episode>[0-1][0-8]\d\d)',
                       r'(?P<episode>\d?\d?\d)',
                       ]

            for motif in masques:
                r = re.search(motif, name, re.I)
                if r:
                    try:
                        try:
                            saison = "%s" %r.group("saison").zfill(2)
                            valid = 1
                        except:
                            saison = "01"
                        try:
                            numEpisode = "S%sE%s" %(saison, r.group("episode").zfill(4))
                        except:
                            numEpisode = ""

                    except Exception as e:
                        print(e)
                    nameFinal = name[:r.start()]
                    break
            if r:
                return [nameFinal, saison, numEpisode, year]
            else:
                return [name, "", "", year]

    def correctNom(self, title, tabRep=[]):
        title = unquote(title, encoding='latin-1', errors='replace')
        title = unicodedata.normalize('NFD', title).encode('ascii','ignore').decode("latin-1")
        tab_remp = [r'''\(.*\)|_|\[.*\]| FR |Episode| {2,}''', ' ']
        title = re.sub(tab_remp[0], tab_remp[1], title, flags=re.I)
        for repl in tabRep:
                title = title.replace(repl[0], repl[1])
        title = re.sub(r"^ \.?", "", title, flags=re.I)
        title = re.sub(r"\.{2,}", ".", title, flags=re.I)
        title = re.sub(r" {2,}", " ", title, flags=re.I)
        return title

    def nettNom(self, title, tabRep=[]):
        title = unquote(title, encoding='latin-1', errors='replace')
        title = unicodedata.normalize('NFD', title).encode('ascii','ignore').decode("latin-1")
        for repl in tabRep:
            title = title.replace(repl[0], repl[1])
        return title

class BookmarkUpto:

    def __init__(self, database):
        self.database = database
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS series(
          `id`    INTEGER PRIMARY KEY,
          repo TEXT,
          rep TEXT,
          nom TEXT,
          num INTEGER,
          actif INTEGER DEFAULT 1,
          UNIQUE (repo, rep))
            """)
        cur.execute("""CREATE TABLE IF NOT EXISTS lock(
          repo TEXT,
          lock INTEGER DEFAULT 1,
          UNIQUE (repo))
            """)
        cnx.commit()
        cur.close()
        cnx.close

    def lockGroupe(self, repo, lock=1):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO lock (repo, lock) VALUES (?, ?)", (repo, lock, ))
        cnx.commit()
        cur.close()
        cnx.close

    def getLockGroupe(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT repo FROM lock WHERE lock=1")
        liste = [x[0] for x in cur.fetchall()]
        cnx.commit()
        cur.close()
        cnx.close
        return liste

    def insertSeries(self, repo, tab):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("UPDATE series SET actif=0 WHERE repo=?", (repo,))
        cnx.commit()
        for t in tab:
            try:
                cur.execute("INSERT INTO series (repo, rep, nom, num) VALUES (?, ?, ?, ?)", (repo, t[0], t[1], t[2],))
            except sqlite3.Error as er:
                cur.execute("UPDATE series SET actif=1 WHERE repo=? and rep=?", (repo, t[0],))
        cnx.commit()
        cur.close()
        cnx.close

    def getSeries(self, repo, limit, offset):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        sql = "SELECT nom, rep FROM series WHERE repo='{}' AND actif=1 ORDER BY id DESC LIMIT {} OFFSET {}".format(repo, limit, offset)
        cur.execute(sql)
        liste = cur.fetchall()
        cur.close()
        cnx.close
        return liste

class Uptobox:

    def __init__(self, key=''):
        self.baseurl = "https://uptobox.com"
        self.urlFile = self.baseurl + '/api/user/files'
        self.key = key.strip()
        self.totalSize = 0
        self.tabFolder = []

    def getFileFolderPublic(self, folder="", hash="", limit=100, offset=0):
        """extract info folder upto publique"""
        tabMedia = []
        url = self.baseurl + "/api/user/public?folder={}&hash={}&limit={}&offset={}".format(folder, hash, limit, offset)
        data = self.getDataJson(url)
        if data['data']["list"]:
            [tabMedia.append((d['file_created'], d['file_name'], d['file_code'])) for d in data['data']["list"]]
            #[tabMedia.append((d['file_name'], d['file_code'])) for d in data['data']["list"]]
        return tabMedia

    def getFileFolderPublicAll(self, folder="", hash=""):
        """extract info folder upto publique"""
        i, j = 100, 0
        tabMedia = []
        while 1:
            try:
                url = self.baseurl + "/api/user/public?folder={}&hash={}&limit={}&offset={}".format(folder, hash, i, j)
                r = requests.get(url)
                data = r.json()
                if data['data']["list"]:
                    [tabMedia.append((d['file_created'], d['file_name'], d['file_code'])) for d in data['data']["list"]]
                    j += i
                else:
                    break
            except: break
        return [(x[1], x[2]) for x in tabMedia[::-1]]

    def singleFolder(self, rep="//", nbFile=20, offset=0):
        """extraction infos rep + fichiers"""
        if nbFile > 100:
            nbFile = 100
        tabFile = []

        tabFolder = []
        url = self.baseurl + "/api/user/files?token=%s&path=%s&limit=%d&offset=%d" %(self.key, rep, nbFile, offset)
        try:
            data = self.getDataJson(url)
            if data:
                for file in data['data']["files"]:
                    tabFile.append((file["file_name"], file["file_code"]))
        except Exception as e:
            sys.exit()
        tabFolderChild = [(folder["fullPath"], folder["name"], folder["fld_id"]) for folder in data['data']["folders"]]
        try:
            tabFolder = (rep, data['data']['currentFolder']["name"], nbFile, data['data']['currentFolder']["fld_id"], tabFile, tabFolderChild)
        except:
            tabFolder = (rep, "racine", nbFile, data['data']['currentFolder']["fld_id"], tabFile, tabFolderChild)
        return tabFolder

    def singleFolderMyUpto(self, rep="//", nbFileTotal=20, offset=0):
        """extraction infos rep + fichiers"""
        tabFile = []
        tabFolder = []
        nbFile = 0
        while nbFileTotal > 0:
            url = self.baseurl + "/api/user/files?token=%s&path=%s&limit=100&offset=%d" %(self.key, rep, offset)
            try:
                data = self.getDataJson(url)
                if data:
                    if not nbFile:
                        nbFile = data['data']['currentFolder']['fileCount']
                    for file in data['data']["files"]:
                        tabFile.append((file["file_name"], file["file_code"]))
            except Exception as e:
                sys.exit()
            nbFile -= 100
            nbFileTotal -= 100
            offset += 100
            if nbFile < 0:
                break

        tabFolderChild = [(folder["fullPath"], folder["name"], folder["fld_id"]) for folder in data['data']["folders"]]
        try:
            tabFolder = (rep, data['data']['currentFolder']["name"], nbFile, data['data']['currentFolder']["fld_id"], tabFile, tabFolderChild)
        except:
            tabFolder = (rep, "racine", nbFile, data['data']['currentFolder']["fld_id"], tabFile, tabFolderChild)
        return tabFolder


    def singleFolderFolder(self, rep="//", nbFolder=20, offset=0):
        """extraction infos rep"""
        tabFolder = []
        url = self.baseurl + "/api/user/files?token=%s&path=%s&limit=1&offset=0" %(self.key, rep)
        try:
            data = self.getDataJson(url)
        except Exception as e:
            sys.exit()

        tabFolderChild = [(folder["fullPath"], folder["name"], folder["fld_id"]) for folder in data['data']["folders"]]
        return tabFolderChild

    def nbFilesRep(self, rep="//"):
        """ renvoi le nombre de fichier dans un repertoire """
        i = 5
        j = 0
        url = self.baseurl + "/api/user/files?token=%s&path=%s&limit=%d&offset=%d" %(self.key, rep, i, j)
        data = self.getDataJson(url)
        try:
            nbMedia = int(data['data']['currentFolder']['fileCount'])
        except Exception as e:
            sys.exit()
        return nbMedia

    def deleteFile(self, filecode):
        url = self.baseurl + "/api/user/files?token=%s&file_codes=%s" %(self.key, filecode)
        try:
            requests.delete(url)
        except: pass


    def extractAll(self):
        url = self.baseurl + "/api/user/files/all?token=%s" %self.key
        data = self.getDataJson(url)
        #print(str(data.keys()).encode(sys.stdout.encoding, errors='replace'))
        if "data" in data.keys():
            tabFiles = [(x["file_name"], x['file_code']) for x in data['data']]
        else:
            tabFiles = []
        return tabFiles

    def getDataJson(self, url, nbTest=1):
        """reconnection error json"""
        headers = {'Accept': 'application/json'}
        try:
            data = requests.get(url, headers=headers).json()
        except :
            time.sleep(0.5 * nbTest)
            nbTest += 1
            if nbTest > 5:
                sys.exit()
            return self.getDataJson(url, nbTest)
        else:
            return data

    def linkDownload(self, fileCode):
        url1 = self.baseurl + "/api/link?token=%s&file_code=%s" % (self.key, fileCode)
        try:
            req = requests.get(url1)
            dict_liens = req.json()
            dlLink = dict_liens["data"]["dlLink"]
            statut = dict_liens["statusCode"]
        except Exception as e:
            dlLink = ""
            statut = "err"

        return dlLink, statut

    def file_search(self, path: str, limit: int, offset: int, search: str):
        url1 = self.baseurl + "/api/user/files?token={}&path={}&limit={}&searchField=file_name&search={}&offset={}".format(self.key, path, limit, search, offset)
        request = requests.get(url1).text
        info = json.loads(request)
        files_name = [(element["file_name"], element["file_code"]) for element in info["data"]["files"]]
        return files_name

    def _linkDownloadUptostream(self, fileCode):
        url1 = self.baseurl +  "/api/streaming?token=%s&file_code=%s" % (self.key, fileCode)
        req = requests.get(url1)
        dict_liens = req.json()
        notice(dict_liens)
        link = dict_liens["data"]['streamLinks']["src"]
        return link

class Alldedrid:

    def __init__(self, key):
        self.key = key.strip()
        self.urlBase = "https://api.alldebrid.com"

    @property
    def extractMagnets(self):
        url = self.urlBase + "/v4/magnet/status?agent=u2p&apikey=%s" %self.key
        tx = requests.get(url)
        dictInfo = json.loads(tx.text)
        tabLinks = []
        for media in dictInfo["data"]["magnets"]:
            if media["status"] == "Ready":
                for link in media["links"]:
                    if link["filename"][-4:] in [".mp4", ".mkv", ".avi", "dixw", ".mp3"]:
                        tabLinks.append((link["filename"], link["link"].replace("https://uptobox.com/", "")))
        return tabLinks[::-1]

    def extractListe(self, t="history"):
        #history , links
        url = self.urlBase + "/v4/user/%s?agent=u2p&apikey=%s" %(t, self.key)
        tx = requests.get(url)
        dictInfo = json.loads(tx.text)
        notice(dictInfo)
        tabLinks = []
        for link in dictInfo["data"]["links"]:
            if link["filename"][-4:] in [".mp4", ".mkv", ".avi", "dixw", ".mp3"]:
                tabLinks.append((link["filename"], link["link"].replace("https://uptobox.com/", "")))
        return tabLinks

    def linkDownload(self, lien):
        dlLink = ""
        url1 = self.urlBase + "/v4/link/unlock?agent=u2p&apikey=%s&link=https://uptobox.com/%s" % (self.key , lien)
        req = requests.get(url1)
        dict_liens = req.json()
        try:
            if dict_liens["status"] == "success":
                dlLink = dict_liens['data']['link']
                statut = "success"
            else:
                statut = dict_liens["error"]["code"]
        except:
            dlLink = ""
            statut = "err"
        return dlLink, statut

#===================================================================================== fonctions ==========================================================================
def actifTrakt():
    trk = None
    if ADDON.getSetting("bookonline") != "false":
        userPass = [x[1] for x in widget.usersBookmark() if x[0] == ADDON.getSetting("profiltrakt")]
        if userPass and ADDON.getSetting("bookonline_name") == userPass[0]:
                trk = TraktHK()
    else:
        trk = TraktHK()
    return trk

def loadUpto(params):
    # par nom de folder
    rep = params["rep"]
    offset = params["offset"]
    key = ADDON.getSetting("keyUpto")
    if key:
        up = Uptobox(key=key)
        tabExtract = up.singleFolder(rep=rep, nbFile=NBMEDIA, offset=int(offset))
        medias = ventilationType(tabExtract[4])
        affUptobox("movie", [x[1:]  for x in medias], params)

def loadUptoP(params):
    #folder public
    numHash = params["hash"]
    folder = params["folder"]
    offset = int(params["offset"])
    up = Uptobox(key="123456789")
    tabExtract = up.getFileFolderPublicAll(hash=numHash, folder=folder)
    medias = ventilationType(tabExtract[offset: offset + NBMEDIA])
    affUptobox("movie", [x[1:]  for x in medias], params)

def searchUpto(params):
    # recherche dans le nom de fichier
    offset = int(params["offset"])
    dialog = xbmcgui.Dialog()
    if "rech" in params.keys():
        d = params['rech']
    else:
        d = dialog.input("Texte recherche", type=xbmcgui.INPUT_ALPHANUM)
    if d:
        params['rech'] = d
        key = ADDON.getSetting("keyUpto")
        if key:
            up = Uptobox(key=key)
            tabFiles = up.file_search("//", NBMEDIA, offset, d)
            medias = ventilationType(tabFiles)
            affUptobox("movie", [x[1:]  for x in medias], params)

def loadSeriesUpto(params):
    #extraction des dossiers serie
    rep = params["rep"]
    offset = int(params["offset"])
    key = ADDON.getSetting("keyUpto")
    if key:
        bd = BookmarkUpto(BDBOOKMARK)
        mDB = TMDB(KEYTMDB)
        if offset == 0:
            up = Uptobox(key=key)
            tabExtract = up.singleFolderFolder(rep=rep, nbFolder=NBMEDIA, offset=offset)
            bd.insertSeries(rep, tabExtract[::-1])
        liste =  bd.getSeries(rep, NBMEDIA, offset)
        for i, (nom, rep) in enumerate(liste):
            r = re.search(r"(TM)(?P<num>\d*)(TM)", nom)
            if r:
                numId = r.group("num")
                threading.Thread(name="tet", target=mDB.tvshowId, args=(nom, rep, i, numId,)).start()
            else:
                r = re.search(r"(?P<name>.*)\((?P<year>\d*)\)", nom)
                if r:
                    year = r.group("year").strip()
                    nom = r.group("name").strip()
                else:
                    year = 0
                threading.Thread(name="tet", target=mDB.searchTVshow, args=(nom, rep, i, int(year),)).start()
        #while threading.active_count() > 1:
        #    time.sleep(0.1)
        testThread()
        medias = mDB.extractListe
        affUptoboxSeries("tvshow", [x[1:]  for x in medias], params)

def verifLock(repo):
    bd = BookmarkUpto(BDBOOKMARK)
    if repo in bd.getLockGroupe():
        if ADDON.getSetting("passtmp") == "ok":
            ok = True
        else:
            dialog = xbmcgui.Dialog()
            d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if d == "x2015x":
                ok = True
                ADDON.setSetting("passtmp", "ok")
            else:
                ok = False
                ADDON.setSetting("passtmp", "ko")
    else:
        ok = True
    return ok

def lockRep(params):
    repo = params["repo"]
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Protection Accés répertoire ', 'Que veux tu faire?', nolabel="Oter la protection", yeslabel="Protéger")
    bd = BookmarkUpto(BDBOOKMARK)
    if not ret:
        #oter
        d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        if d == "x2015x":
            bd.lockGroupe(repo, 0)
        else:
            return
    else:
        bd.lockGroupe(repo)

def loadFoldersPub(params):
    #extraction des dossiers serie
    typM = params["typM"]
    offset = int(params["offset"])
    repo = params["repo"]

    valid = verifLock(repo)
    if valid:
        #cnx = sqlite3.connect(BDFLDP)
        cnx = sqlite3.connect(BDREPONEW)
        cur = cnx.cursor()
        if typM == "series":
            txdff = "tvshows"
            cur.execute("SELECT m.title, m.numId FROM seriesPub as m WHERE m.numId IN (SELECT d.numId FROM  seriesRepos as d WHERE d.nom='{}') AND actif=1".format(repo) + " ORDER BY m.id DESC LIMIT {} OFFSET {}".format(50, offset))
        elif typM == "divers":
            txdff = "files"
            cur.execute("SELECT m.nom, m.title FROM divers as m  WHERE m.theme='{}' AND actif=1".format(repo) + " ORDER BY m.id DESC LIMIT {} OFFSET {}".format(50, offset))
        else:
            #majRepsFilms()
            txdff = "movies"
            cur.execute("SELECT m.title, m.numId FROM filmsPub as m WHERE m.numId IN (SELECT d.numId FROM filmsRepos as d WHERE d.nom='{}')".format(repo) + " ORDER BY m.id DESC LIMIT {} OFFSET {}".format(50, offset))
        liste = cur.fetchall()
        mDB = TMDB(KEYTMDB)
        #notice(liste)
        if liste:
            if typM == "divers":
                if repo == "fankai":
                    fankai = xbmcvfs.translatePath('special://home/userdata/addon_data/fankai/fankai.json')
                    if os.path.isfile(fankai):
                        txdff = "files*tvshows"
                        f = io.open(fankai, encoding="utf-8")
                        dictFankai = ast.literal_eval(f.read())
                        #notice([x[0] for x in liste])
                        medias = []
                        for i, (nom, nom1) in enumerate(liste):
                            if nom in dictFankai.keys():
                                #title, overview, year, poster, numId, genre, popu
                                poster = xbmcvfs.translatePath('special://home/userdata/addon_data/fankai/poster/%s.jpg' %nom.strip())
                                banner = xbmcvfs.translatePath('special://home/userdata/addon_data/fankai/banner/%s.jpeg' %nom.strip())
                                medias.append((i, nom, dictFankai[nom][0], 0, poster, 0, repo, 0.0, '', banner, 0, 0))
                            else:
                                medias.append((i, nom, nom1, 0, '', 0, repo, 0.0, '', '', 0, 0))
                    else:
                        medias = [(i, x[0], x[1], 0, '', 0, repo, 0.0, '', '', 0, 0) for i, x in enumerate(liste)]
                else:
                    medias = [(i, x[0], x[1], 0, '', 0, repo, 0.0, '', '', 0, 0) for i, x in enumerate(liste)]
            else:
                for i, l in enumerate(liste):
                    nom = l[0]
                    rep = ""
                    numId = l[1]
                    try:
                        cur.execute("SELECT link FROM filmsPubLink WHERE numId={}".format(numId))
                        liste = cur.fetchall()
                        #notice(nom  +  " " + str(numId) +  " " + str(liste))
                        link = "*".join([x[0] for x in liste])
                        if typM in ["series"]:
                            threading.Thread(name="tet", target=mDB.tvshowId, args=(nom, rep, i, numId,)).start()
                        else:
                            threading.Thread(name="tet", target=mDB.movieNumId, args=(link, i, numId,)).start()
                    except: pass
                testThread()
                medias = mDB.extractListe
            cur.close()
            cnx.close()
            affUptoboxSeriesFolderPub(txdff, [x[1:]  for x in medias], params)

        else:
            cur.close()
            cnx.close()
            return
    else:
        return

def affUptoboxSeriesFolderPub(typM, medias, params=""):
    try:
        typM, typFankai = typM.split("*")
    except:
        typM, typFankai = typM, ""
    xbmcplugin.setPluginCategory(HANDLE, typM)
    if typFankai:
        xbmcplugin.setContent(HANDLE, typFankai)
    else:
        xbmcplugin.setContent(HANDLE, typM)
    i = -1
    for i, media in enumerate(medias):
        if typM == "files":
            try:
                med = Media("fankai", *media[:-1])
            except:
                med = Media("fankai", *media)
        else:
            try:
                med = Media("movie", *media[:-1])
            except:
                med = Media("movie", *media)
        if typM == "tvshows":
            ok = addDirectoryUptobox("%s" %(med.title), isFolder=True, parameters={"action": "affSaisonUptofoldercrypt", "u2p": med.numId}, media=med)
        elif typM == "files":
            ok = addDirectoryUptobox(med.title, isFolder=True, parameters={"action": "affFoldercryptDivers", "nom": med.title, "repo": med.genre}, media=med)
        else:
            ok = addDirectoryUptobox("%s" %(med.title), isFolder=True, parameters={"action": "affdetailfilmpoiss", "lien": med.link, "u2p": med.numId}, media=med)

    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    if i > -1:
        if i >= (NBMEDIA - 1):
            addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def affLiens(numId, typM, liste):
    xbmcplugin.setPluginCategory(HANDLE, "Liens")
    xbmcplugin.setContent(HANDLE, 'files')
    mDB = TMDB(KEYTMDB)
    mDB.movieNumId("liens", 0, numId)
    lFinale = mDB.extractListe[0]
    #m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id
    #(0, 'Miranda Veil', '', 2020, '/mpYUoSS7TyxtaMEaTb88LaQTuR2.jpg', 744428, 'Horreur, Fantastique', 6.0, 'IBSfuEFS2@otWGG54PdCj9#1080.Light.VOSTFR.WEBRIP', None, 0, 0)
    movie = [lFinale[1], lFinale[2], lFinale[3], lFinale[4], lFinale[5], lFinale[6], lFinale[7], "", 0, lFinale[5]]
    for l in liste:
        l = list(l)
        l += movie
        media = Media("lien", *l)
        media.typeMedia = typM
        addDirectoryUptobox("%s" %(l[0]), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "poiss": "ok"}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def loadFolderCryptDivers(params):
    nom = params["nom"]
    repo = params["repo"]
    cnx = sqlite3.connect(BDREPONEW)
    cur = cnx.cursor()
    cur.execute("SELECT folder, hsh FROM divers WHERE nom=? and theme=?", (nom, repo,))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    #notice(liste)
    listeFiles = scraperUPTO.extractFolderCrypt(str(liste[0][0]), liste[0][1])
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    xbmcplugin.setContent(HANDLE, 'files')
    for release, link in  listeFiles:
        media = ""
        addDirectoryMenu(release[:-4], isFolder=False, parameters={"action": "playHK", "lien": link, "u2p": "0", "typMedia": "divers"}, media=media)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def getEpisodesSuite(numId):
    cnx = sqlite3.connect(BDREPONEW)
    cur = cnx.cursor()
    cur.execute('SELECT folder, hsh FROM seriesfolderHash WHERE numId={}'.format(numId))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    '''
    a = time.time()
    for folder, hsh in liste:
        tabExtract += scraperUPTO.extractFolderCrypt(folder, hsh)
    notice(time.time() - a)
    '''
    a = time.time()
    eRep = scraperUPTO.ExtractRep()
    tabExtract = eRep.extractAll(liste)
    tabFiles = []
    if tabExtract:
        renam = RenameMedia()
        for nom, filecode in tabExtract:
            n = renam.extractInfo(nom, typM="tvshow")
            try:
                tabFiles.append((n[2], filecode))
            except:
                notice(n)
    tabFiles = [(int(x[0].replace("S", "").replace("E", "")), x[1], x[0]) for x in tabFiles if x[0][0] == "S"]
    return tabFiles

def getEpisodesSaison(numId):
    try:
        if ADDON.getSetting("bookonline") != "false":
            vus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
        else:
            vus =  widget.getVu("tvshow")
    except:
        vus = []
    vus = [("Saison %s" %x.split("-")[1].zfill(2), x.split("-")[2]) for x in vus if x.split("-")[0] == str(numId)]

    cnx = sqlite3.connect(BDREPONEW)
    cur = cnx.cursor()
    cur.execute('SELECT folder, hsh FROM seriesfolderHash WHERE numId={}'.format(numId))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    eRep = scraperUPTO.ExtractRep()
    tabExtract = eRep.extractAll(liste)
    if tabExtract:
        tabFiles = []
        liste = []
        renam = RenameMedia()
        for nom, filecode in tabExtract:
            n = renam.extractInfo(nom, typM="tvshow")
            try:
                tabFiles.append(("Saison %s" %n[1], int(n[2].split("E")[1]), filecode))
                liste.append(("Saison %s" %n[1], int(n[2].split("E")[1])))
            except:
                notice(n)

    dictSaisons = {}
    for saison in list(set([x[0] for x in liste])):
        nbTotal = len([x for x in list(set(liste)) if x[0] == saison])
        nbVus = len([x for x in vus if x[0] == saison])
        if nbVus == 0:
            c = "red"
        elif nbVus == nbTotal:
            c = "green"
        else:
            c = "orange"
        dictSaisons[saison] = (c, nbVus, nbTotal)
    return dictSaisons, tabFiles

def loadSaisonsUptoFolderCrypt(params):
    typMedia = "tvshow"
    numId = params["u2p"]

    choixsaisons = []
    mDB = TMDB(KEYTMDB)
    dictSaison = mDB.serieNumIdSaison(numId)

    dictSaisonsVU, tabFiles = getEpisodesSaison(numId)

    dictEpisodesSaison = {}
    if tabFiles:
        for saison in sorted(list(set([x[0] for x in tabFiles]))):
            dictEpisodesSaison[saison] = [x[1:] for x in tabFiles if x[0] == saison]
            #notice(dictEpisodesSaison[saison])
            r = re.search(r"(?P<num>\d+)", saison)
            if r:
                numSaison = int(r.group('num'))
                infos = dictSaison.get(numSaison, ('Saison %d' %numSaison, None, 'Pas de Synopsis....'))
                #Înotice(infos)
                sTmp = "Saison %s" %str(numSaison).zfill(2)
                choixsaisons.append(("%s [COLOR %s](%d/%d)[/COLOR]" %(infos[0], dictSaisonsVU[sTmp][0], dictSaisonsVU[sTmp][1], dictSaisonsVU[sTmp][2]), \
                    {"action": "visuEpisodesFolderCrypt", "u2p": numId, "saison": numSaison, "newhk": "1", "episodes": str(dictEpisodesSaison[saison])}))
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    xbmcplugin.setContent(HANDLE, 'episodes')
    categories = [("[COLOR red]Bande Annonce[/COLOR]", {"action": "ba", "u2p": numId, "typM": typMedia})] + choixsaisons + \
        [("Acteurs", {"action": "affActeurs", "u2p": numId, "typM": typMedia}),\
        ("Similaires", {"action": "suggest", "u2p": numId, "typ": "Similaires","typM": typMedia}), \
        ("Recommandations", {"action": "suggest", "u2p": numId, "typ": "Recommendations", "typM": typMedia})]

    #liste lastview
    if ADDON.getSetting("bookonline") != "false":
        listeView = widget.responseSite("http://%s/requete.php?name=%s&type=view&media=tv" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
        listeView = [int(x) for x in listeView]
    else:
        listeView = list(widget.extractIdInVu(t="tvshow"))
    if int(numId) in listeView:
        categories.append(("Retirer Last/View", {"action": "supView", "u2p": numId, "typM": typMedia}))

    #liste favs
    if ADDON.getSetting("bookonline") != "false":
        listeM = widget.responseSite("http://%s/requete.php?name=%s&type=favs&media=tvshow" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
        listeM = [int(x) for x in listeM]
    else:
        listeM = list(widget.extractFavs(t="tvshow"))
    if int(numId) in listeM:
        categories.append(("Retirer fav's-HK", {"action": "fav", "mode": "sup", "u2p": numId, "typM": "tvshow"}))
    else:
        categories.append(("Ajouter fav's-HK", {"action": "fav", "mode": "ajout", "u2p": numId, "typM": "tvshow"}))

    for cat in categories:
        if "saison" in cat[1].keys():
            numSaison = cat[1]["saison"]
            try:
                tab = dictSaison.get(numSaison, ('Saison %d' %numSaison, None, 'Pas de Synopsis....'))
                lFinale = ["", tab[2], "", "", tab[1], "", numId, tab[1]]
            except Exception as e:
                notice(str(e))

            media = Media("menu", *lFinale)
            media.saison = numSaison
            media.typeMedia = typMedia
        else:
            media = ""
        addDirectoryMenu(cat[0], isFolder=True, parameters=cat[1], media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)


def loadSaisonsUpto(params):
    typMedia = "tvshow"
    numId = params["u2p"]
    try:
        rep = params["rep"]
    except: pass

    mDB = TMDB(KEYTMDB)
    dictSaison = mDB.serieNumIdSaison(numId)
    key = ADDON.getSetting("keyUpto")
    up = Uptobox(key=key)
    choixsaisons = []
    if "tabsaison" in params.keys():
        tabExtract = [("", x, "") for x in params["tabsaison"].split("*")]

    else:
        tab = up.singleFolderMyUpto(rep=rep, nbFileTotal=1200, offset=0)
        tabExtract = tab[5]

    if tabExtract:
        for rep, saison, num in tabExtract:
            r = re.search(r"(?P<num>\d+)", saison)
            if r:
                numSaison = int(r.group('num'))
                try:
                    infos = dictSaison[numSaison]
                except:
                    infos = ('Saison {}'.format(numSaison), '', "pas de synop...")
                if "tabsaison" in params.keys():
                    choixsaisons.append((infos[0], {"action": "visuEpisodesUptoPoiss", "u2p": numId, "saison": numSaison}))
                else:
                    choixsaisons.append((infos[0], {"action": "visuEpisodesUpto", "u2p": numId, "saison": numSaison, "rep": rep}))
    else:
        tabFiles = []
        renam = RenameMedia()
        for nom, filecode in tab[4]:
            n = renam.extractInfo(nom, typM="tvshow")
            tabFiles.append(("Saison %s" %n[1], int(n[2].split("E")[1]), filecode))
        for saison in sorted(list(set([x[0] for x in tabFiles]))):
            r = re.search(r"(?P<num>\d+)", saison)
            if r:
                numSaison = int(r.group('num'))
                try:
                    infos = dictSaison[numSaison]
                except:
                    infos = ('Saison {}'.format(numSaison), '', "pas de synop...")
                choixsaisons.append((infos[0], {"action": "visuEpisodesUpto", "u2p": numId, "saison": numSaison, "rep": rep, "filtre": "1"}))
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    xbmcplugin.setContent(HANDLE, 'episodes')
    categories = [("[COLOR red]Bande Annonce[/COLOR]", {"action": "ba", "u2p": numId, "typM": typMedia})] + choixsaisons + \
        [("Acteurs", {"action": "affActeurs", "u2p": numId, "typM": typMedia}),\
        ("Similaires", {"action": "suggest", "u2p": numId, "typ": "Similaires","typM": typMedia}), \
        ("Recommandations", {"action": "suggest", "u2p": numId, "typ": "Recommendations", "typM": typMedia})]
    for cat in categories:
        if "saison" in cat[1].keys():
            numSaison = cat[1]["saison"]
            try:
                tab = dictSaison[numSaison]
                lFinale = ["", tab[2], "", "", tab[1], "", numId, tab[1]]
            except Exception as e:
                notice(str(e))

            media = Media("menu", *lFinale)
            media.saison = numSaison
            media.typeMedia = typMedia
        else:
            media = ""
        addDirectoryMenu(cat[0], isFolder=True, parameters=cat[1], media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def detailFilmPoiss(params):
    typMedia = "movie"
    links = params["lien"]
    numId = params["u2p"]
    mDB = TMDB(KEYTMDB)
    mDB.movieNumId(links, 0, numId)
    lFinale = mDB.extractListe[0]
    xbmcplugin.setPluginCategory(HANDLE, "Menu")
    xbmcplugin.setContent(HANDLE, 'episodes')
    categories = [("[COLOR red]Bande Annonce[/COLOR]", {"action": "ba", "u2p": numId, "typM": typMedia}), ("[COLOR green]Lire[/COLOR]", {"action": "afficheLiens", "lien": links, "u2p": numId, "poiss": "ok"}),\
                ("Acteurs", {"action": "affActeurs", "u2p": numId, "typM": typMedia}),\
                ("Similaires", {"action": "suggest", "u2p": numId, "typ": "Similaires", "typM": typMedia}), ("Recommandations", {"action": "suggest", "u2p": numId, "typ": "Recommendations", "typM": typMedia})]
    for cat in categories:
        media = Media("movie", *lFinale[1:])
        media.typeMedia = typMedia
        addDirectoryMenu(cat[0], isFolder=True, parameters=cat[1], media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def addDirectoryMenu(name, isFolder=True, parameters={}, media="" ):
    li = xbmcgui.ListItem(label=name)
    if media:
        li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre,
                "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu})
        li.setArt({'icon': media.backdrop,
                    "thumb": media.poster,
                    'poster':media.poster,
                    'fanart': media.backdrop
                    })
        if "newhk" in parameters.keys():
            commands = []
            commands.append(('[COLOR yellow]Gestion Vus/Non-Vus[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=vuNonVu&saison=%d&u2p=%s&refresh=1&newhk=1)' %(media.saison, media.numId)))
            li.addContextMenuItems(commands, replaceItems=False)
    if not isFolder:
        li.setInfo('video', {"title": name})
        li.setProperty('IsPlayable', 'true')

    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def testThread():
    a = 0
    tActif = True
    while tActif:
        tActif = False
        for t in threading.enumerate():
            if "tet" == t.getName():
                tActif = True
        time.sleep(0.1)
        a += 1
        if a > 150:
            break
    return True

def majRepsFilms():
    maj =  scraperUPTO.MAJrep()
    maj.gestionMajRep()
    """
    tOut = True
    for t in threading.enumerate():
        if "majRepCr" == t.getName():
            tOut = False
            break
    if tOut:
        params = {}
        threading.Thread(name="majRepCr", target=scraperUPTO.gestionMajRep, args=(params,)).start()
    """

def extractMedias(limit=0, offset=1, sql="", unique=0):
    cnx = sqlite3.connect(BDFLDP)
    cur = cnx.cursor()
    def normalizeTitle(tx):
        #tx = re.sub(r''' {2,}''', ' ', re.sub(r''':|;|'|"|,''', ' ', tx))
        tx = re.sub(r''':|;|'|"|,|\-''', ' ', tx)
        tx = re.sub(r''' {2,}''', ' ', tx)
        tx = str(tx).lower()
        return unicodedata.normalize('NFD', tx).encode('ascii','ignore').decode("latin-1")
    cnx.create_function("normalizeTitle", 1, normalizeTitle)
    if sql:
        cur.execute(sql)
        if unique:
            requete = [x[0] for x in cur.fetchall()]
        else:
            requete = cur.fetchall()
    cur.close()
    cnx.close()
    return requete

def ventilationType(tabFiles):
    # ventilation films, serie divers
    tabCorrect = [("[", "."), ("]", "."), ("{", "."), ("}", "."), (" ", "."), ("(", "."), (")", ".")]
    renam = RenameMedia()
    mDB = TMDB(KEYTMDB)
    for i, (nom, filecode) in enumerate(tabFiles):
        release = nom[:-4].replace(".", " ").replace("_", " ")
        nom = renam.nettNom(nom, tabCorrect)
        if nom[-4:] not in [".zip", ".rar", ".pdf", ".doc", ".xls", ".txt", ".mp3"]:
            if re.search(r"s\d\d?\d?\.?e\d\d?\d?\.", nom, re.I) or re.search(r"\.e\d\d?\d?\.", nom, re.I):
                title, saison, episode, year = renam.extractInfo(nom, typM="tvshow")
                threading.Thread(name="tet", target=mDB.searchEpisode, args=(title, saison, episode, filecode, i, int(year), release, )).start()
            elif re.search(r"\.19\d\d\.|\.20\d\d\.", nom):
                title, year = renam.extractInfo(nom, typM="movie")
                threading.Thread(name="tet", target=mDB.searchMovie, args=(title, filecode, i, year, release)).start()
            else:
                mDB.tabMediaFinal.append((i, nom, "", 0, "", 0, "", "", filecode, "", 0, 0))
        else:
            mDB.tabMediaFinal.append((i, nom, "", 0, "", 0, "", "", filecode, "", 0, 0))
    #while threading.active_count() > 1:
    #    time.sleep(0.1)
    testThread()
    medias = mDB.extractListe
    return sorted(medias)

def regroupeEpisodes(tab, saison):
    saison = "S" + str(saison).zfill(2)
    renam = RenameMedia()
    tabTMP = []
    for nom, filecode in tab:
        _, _, episode, _ = renam.extractInfo(nom, typM="tvshow")
        tabTMP.append((episode, filecode))
    tabNum = sorted(list(set([x[0] for x in tabTMP if saison in x[0]])))
    return [(y , "*".join([x[1] for x in tabTMP if x[0] == y])) for y in tabNum]

def getLinkUpNext(numId, saison, episode):
    cnx = sqlite3.connect(BDREPONEW)
    cur = cnx.cursor()
    cur.execute('SELECT folder, hsh FROM seriesfolderHash WHERE numId={}'.format(numId))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    eRep = scraperUPTO.ExtractRep()
    tabExtract = eRep.extractAll(liste)
    tabExtract = regroupeEpisodes(tabExtract, saison)
    for ep, link in tabExtract:
        if int(episode) == int(ep.split("E")[1]):
            return [link]
    return [""]

def getEpisodesSerie(numId, saison):
    cnx = sqlite3.connect(BDREPONEW)
    cur = cnx.cursor()
    cur.execute('SELECT folder, hsh FROM seriesfolderHash WHERE numId={}'.format(numId))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    eRep = scraperUPTO.ExtractRep()
    tabExtract = eRep.extractAll(liste)
    tabExtract = regroupeEpisodes(tabExtract, saison)
    return [x[0] for x in tabExtract if int(saison) == int(x[0].split("E")[0][1:])]


def affEpisodesFolderCrypt(params):
    typMedia = "tvshow"
    numId = params["u2p"]
    saison = params["saison"]
    Tsaison = str(saison).zfill(2)
    episodes = ast.literal_eval(params["episodes"])
    typM = "episode"
    #cnx = sqlite3.connect(BDFLDP)

    """
    cnx = sqlite3.connect(BDREPONEW)
    cur = cnx.cursor()
    cur.execute('SELECT folder, hsh FROM seriesfolderHash WHERE numId={}'.format(numId))
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    choixsaisons = []
    tabExtract = []
    eRep = scraperUPTO.ExtractRep()
    tabExtract = eRep.extractAll(liste)
    #for folder, hsh in liste:
    #    tabExtract += scraperUPTO.extractFolderCrypt(folder, hsh)
    """
    mDB = TMDB(KEYTMDB)
    tabEpisodes = mDB.saison(numId, saison)
    tabExtract = []
    for episode in list(set([x[0] for x in episodes])):
        tabExtract.append(("S%sE%s" %(Tsaison, str(episode).zfill(4)), "*".join([x[1] for x in episodes if x[0] == episode])))

    #tabExtract = [("S%sE%d" %(Tsaison, x[0]), x[1]) for x in episodes]
    if tabExtract:
        #tabExtract = regroupeEpisodes(tabExtract, saison)
        #notice(tabExtract)
        try:
            if ADDON.getSetting("bookonline") != "false":
                vus = widget.responseSite("http://%s/requete.php?name=%s&type=getvu" %(ADDON.getSetting("bookonline_site"), ADDON.getSetting("bookonline_name")))
            else:
                vus =  widget.getVu("tvshow")
        except:
            vus = []
        vus = [x for x in vus if x.split("-")[0] == str(numId)]
        #notice(vus)

        xbmcplugin.setPluginCategory(HANDLE, "Episodes")
        xbmcplugin.setContent(HANDLE, 'episodes')
        for episode, filecode in sorted(tabExtract):
            ep = "%d-%d-%d" %(int(numId), int(saison), int(episode.split("E")[1]))
            if ep in vus:
                isVu = 1
            else:
                isVu = 0
            #notice(ep)
            #notice(isVu)

            numEpisode = int(episode.split("E")[1])
            #"72879"    "Saison 05" "S05E59"    "7UM9cgSAc@TEgCpOiQtH3G#1080P"
            l = [numId, saison, episode, filecode]
            try:
                lFinale = list(l) + list([episode for episode in tabEpisodes if numEpisode == episode[-1]][0])
            except:
                lFinale = list(l) + ["Episode", "Pas de synopsis ....", "", "", "", saison, numEpisode]
            lFinale.append(isVu)
            media = Media("episode", *lFinale)
            media.typeMedia = typM
            media.numId = int(numId)
            addDirectoryUptobox("E%d - %s" %(numEpisode, media.title), isFolder=False, \
                parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode, "saison": media.saison}, media=media)
        xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)


def affEpisodesUpto(params):
    numId = params["u2p"]
    saison = params["saison"]
    rep = params["rep"]
    key = ADDON.getSetting("keyUpto")
    renam = RenameMedia()
    if key:
        up = Uptobox(key=key)
        tabExtract = up.singleFolderMyUpto(rep=rep, nbFileTotal=1200, offset=0)
        liste = tabExtract[4]
        if "filtre" in params.keys():
            renam = RenameMedia()
            liste = [x for x in liste if int(saison) == int(renam.extractInfo(x[0])[1])]
        typM = "episode"
        xbmcplugin.setPluginCategory(HANDLE, "Episodes")
        xbmcplugin.setContent(HANDLE, 'episodes')
        mdb = TMDB(KEYTMDB)
        tabEpisodes = mdb.saison(numId, saison)

        for nom, filecode in sorted(liste):
            _, _, episode, _ = renam.extractInfo(nom, typM="tvshow")
            numEpisode = int(episode.split("E")[1])
            #"72879"    "Saison 05" "S05E59"    "7UM9cgSAc@TEgCpOiQtH3G#1080P"
            l = [numId, saison, episode, filecode]
            try:
                lFinale = list(l) + list([episode for episode in tabEpisodes if numEpisode == episode[-1]][0])
            except:
                lFinale = list(l) + ["Episode", "Pas de synopsis ....", "", "", "", saison, numEpisode]
            isVu = 0
            lFinale.append(isVu)
            media = Media("episode", *lFinale)
            media.typeMedia = typM
            media.numId = int(numId)
            #notice(lFinale)
            #addDirectoryEpisodes("E%d - %s" %(numEpisode, media.title), isFolder=False, parameters={"action": "playMediaUptobox", "lien": media.link, "u2p": media.numId, "episode": media.episode}, media=media)
            addDirectoryUptobox("E%d - %s" %(numEpisode, media.title), isFolder=False, \
                parameters={"action": "playMediaUptobox", "lien": media.link, "u2p": media.numId, "episode": media.episode, "saison": media.saison, "rep": rep}, media=media)
        xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def affEpisodesUptoPoissRelease(numId, saison, liste):
    xbmcplugin.setPluginCategory(HANDLE, "Release")
    xbmcplugin.setContent(HANDLE, 'files')
    tabRelease = []
    for numEpisode, filecodes in sorted(liste):
        for filecode in filecodes.split("*"):
            rel = filecode.split("#")[1]
            if rel:
                tabRelease.append(rel)
            else:
                tabRelease.append("ind")
        tabRelease = sorted(list(set(tabRelease)))
    choix = [(t, {"action": "visuEpisodesUptoPoiss", "release": t, "saison": saison, "u2p": numId}, 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/liste.png', "Release %s" %t) for t in tabRelease]
    for ch in sorted(choix):
        name, parameters, picture, texte = ch
        li = xbmcgui.ListItem(label=name)
        li.setInfo('video', {"title": name, 'plot': texte,'mediatype': 'video'})
        li.setArt({'thumb': picture,
                  'icon': ADDON.getAddonInfo('icon'),
                  'icon': ADDON.getAddonInfo('icon'),
                  'fanart': ADDON.getAddonInfo('fanart')})
        url = sys.argv[0] + '?' + urlencode(parameters)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def affEpisodesUptoPoiss(numId, saison, liste, release):
    typM = "episode"
    xbmcplugin.setPluginCategory(HANDLE, "Episodes")
    xbmcplugin.setContent(HANDLE, 'episodes')
    mdb = TMDB(KEYTMDB)
    tabEpisodes = mdb.saison(numId, saison)

    cr = cryptage.Crypt()
    dictResos = cr.extractReso([(y.split("#")[0].split("@")[0], y.split("#")[0].split("@")[1]) for x in [z[1] for z in liste] for y in x.split("*")])
    for numEpisode, filecodes in sorted(liste):
        for filecode in filecodes.split("*"):
            rel = filecode.split("#")[1]
            notice(filecode)
            if rel == release:
                values = dictResos[filecode.split("#")[0].split("@")[1]]
                taille = int(values[1]) / 1000000000.0
                nomrelease = values[2][:-4].replace(".", " ").replace("_", " ")
                l = [numId, saison, numEpisode, filecode]
                try:
                    lFinale = list(l) + list([episode for episode in tabEpisodes if numEpisode == episode[-1]][0])
                except:
                    lFinale = list(l) + ["Episode", "Pas de synopsis ....", "", "", "", saison, numEpisode]
                isVu = 0
                lFinale.append(isVu)
                media = Media("episode", *lFinale)
                media.typeMedia = typM
                media.overview =  "Release: %s\nTaille: %.2f G\n---------------------\n%s" %(nomrelease, taille, media.overview)
                media.numId = int(numId)
                addDirectoryUptobox("E%d - %s" %(numEpisode, media.title), isFolder=False, \
                    parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "episode": media.episode, "saison": media.saison, "poiss": "1"}, media=media)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True)

def affUptoboxSeries(typM, medias, params=""):
    xbmcplugin.setPluginCategory(HANDLE, typM)
    xbmcplugin.setContent(HANDLE, "tvshows")
    i = -1
    for i, media in enumerate(medias):
        try:
            med = Media("movie", *media[:-1])
        except:
            med = Media("movie", *media)
        ok = addDirectoryUptobox("%s" %(med.title), isFolder=True, parameters={"action": "affSaisonUpto", "rep": quote(med.link), "u2p": med.numId}, media=med)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    if i > -1:
        if i >= (NBMEDIA - 1):
            addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def magnets(params):
    offset = int(params["offset"])
    key = ADDON.getSetting("keyalldebrid")
    if key:
        up = Alldedrid(key=key)
        tabFiles = up.extractMagnets
        medias = ventilationType(tabFiles[::-1][offset: offset + NBMEDIA])
        affUptobox("movie", [x[1:]  for x in medias], params)

def listeAllded(params):
    offset = int(params["offset"])
    t = params["typeL"]
    key = ADDON.getSetting("keyalldebrid")
    if key:
        up = Alldedrid(key=key)
        tabFiles = up.extractListe(t)
        medias = ventilationType(tabFiles[::-1][offset: offset + NBMEDIA])
        affUptobox("movie", [x[1:]  for x in medias], params)

def newUpto(params):
    offset = int(params["offset"])
    key = ADDON.getSetting("keyUpto")
    if key:
        up = Uptobox(key=key)
        tabFiles = up.extractAll()
        medias = ventilationType(tabFiles[::-1][offset: offset + NBMEDIA])
        affUptobox("movie", [x[1:]  for x in medias], params)

def getFilmsUptoNews(tabFiles):
    mDB = TMDB(KEYTMDB)
    for i, (numId, link) in enumerate(tabFiles):
        threading.Thread(name="tet", target=mDB.movieNumId, args=(link, i, numId,)).start()
        time.sleep(0.05)
    testThread()
    medias = mDB.extractListe
    return medias

def getSeriesUptoNews(tabFiles):
    mDB = TMDB(KEYTMDB)
    for i, numId in enumerate(tabFiles):
        threading.Thread(name="tet", target=mDB.tvshowId, args=("", "", i, numId,)).start()
    testThread()
    medias = mDB.extractListe
    return medias

def affUptobox(typM, medias, params=""):
    xbmcplugin.setPluginCategory(HANDLE, typM)
    xbmcplugin.setContent(HANDLE, 'movies')
    i = -1
    for i, media in enumerate(medias):
        try:
            media = Media(typM, *media[:-1])
        except:
            media = Media(typM, *media)
        if "*" in media.link:
            paramsIn = dict(parse_qsl(media.link.split("*")[1]))
            ok = addDirectoryUptobox("%s" %(media.title), isFolder=False, parameters=paramsIn, media=media)
        else:
            delF = "ko"
            if "rep" in params.keys() and params["rep"] == "//":
                    delF = "ok"
            if " (S" in media.title:
                ok = addDirectoryUptobox("%s" %(media.title), isFolder=False, parameters={"action": "playMediaUptobox", "lien": media.link, "u2p": media.numId, "typM": media.title.split(" ")[-1], "delF": delF}, media=media)
            else:
                ok = addDirectoryUptobox("%s" %(media.title), isFolder=False, parameters={"action": "playMediaUptobox", "lien": media.link, "u2p": media.numId, "delF": delF}, media=media)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    if i > -1:
        if i >= (NBMEDIA - 1):
            addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def affUptoboxNews(typM, medias, params="", cr=0):
    xbmcplugin.setPluginCategory(HANDLE, typM)
    xbmcplugin.setContent(HANDLE, 'movies')
    i = -1
    for i, media in enumerate(medias):
        try:
            media = Media(typM, *media[:-1])
        except:
            media = Media(typM, *media)
        if "*" in media.link and not cr:
            paramsIn = dict(parse_qsl(media.link.split("*")[1]))
            ok = addDirectoryUptobox("%s" %(media.title), isFolder=False, parameters=paramsIn, media=media)
        else:
            if " (S" in media.title:
                ok = addDirectoryUptobox("%s" %(media.title), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId, "typM": media.title.split(" ")[-1]}, media=media)
            else:
                if media.numId:
                    ok = addDirectoryUptobox("%s" %(media.title), isFolder=True, parameters={"action": "affdetailfilmpoiss", "lien": media.link, "u2p": media.numId}, media=media)
                else:
                    ok = addDirectoryUptobox("%s" %(media.title), isFolder=False, parameters={"action": "playHK", "lien": media.link, "u2p": media.numId}, media=media)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    if i > -1:
        if i >= (NBMEDIA - 1):
            addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def affUptoboxNewsSerie(typM, medias, params=""):
    xbmcplugin.setPluginCategory(HANDLE, typM)
    xbmcplugin.setContent(HANDLE, 'movies')
    i = -1
    for i, media in enumerate(medias):
        try:
            media = Media(typM, *media[:-1])
        except:
            media = Media(typM, *media)
        ok = addDirectoryUptobox("%s" %(media.title), isFolder=True, parameters={"action": "affSaisonUptoPoiss", "u2p": media.numId}, media=media)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    if i > -1:
        if i >= (NBMEDIA - 1):
            addDirNext(params)
    xbmcplugin.endOfDirectory(handle=HANDLE, succeeded=True, cacheToDisc=True)

def addDirectoryEpisodes(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(label=("%s" %(name)))
    li.setInfo('video', {"title": media.title, 'plot': media.overview, 'genre': media.genre, 'playcount': media.vu, "dbid": media.numId + 500000,
        "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu, "episode": media.episode, "season": media.saison})

    li.setArt({'icon': media.backdrop,
              "fanart": media.backdrop})
    li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def addDirectoryUptobox(name, isFolder=True, parameters={}, media="" ):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(label=name)
    li.setUniqueIDs({ 'tmdb' : media.numId }, "tmdb")
    li.setInfo('video', {"title": media.title.replace("00_", ""), 'plot': media.overview, 'genre': media.genre, "dbid": int(media.numId) + 500000,
            "year": media.year, 'mediatype': media.typeMedia, "rating": media.popu, "duration": media.duration * 60 })
    if media.poster[-4:] == ".jpg":
        li.setArt({'icon': media.backdrop,
            'thumb': media.poster,
            'poster': media.poster,
            'fanart': media.backdrop})
    else:
        li.setArt({'icon': media.backdrop,
            'thumb': media.backdrop,
            'poster': media.backdrop,
            'fanart': media.backdrop})
    if media.clearlogo :
        li.setArt({'clearlogo': media.clearlogo})
    if media.clearart :
        li.setArt({'clearart': media.clearart})
    try:
        if media.vu:
            li.setInfo('video', {'playcount': media.vu})
    except:
        pass
    commands = []
    if parameters["action"] == "playHK" and "poiss" in parameters.keys():
        commands.append(('[COLOR yellow]Add Compte Uptobox[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=addcompte&lien=%s)' %(media.link)))
    if "delF" in parameters.keys() and parameters["delF"] == "ok":
        commands.append(('[COLOR yellow]Retirer Compte Uptobox[/COLOR]', 'RunPlugin(plugin://plugin.video.sendtokodiU2P/?action=delcompte&lien=%s)' %(media.link)))
    if commands:
        li.addContextMenuItems(commands)
    li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def debridLien(link):
    ApikeyUpto = ADDON.getSetting("keyUpto")
    if ApikeyUpto:
        up = Uptobox(key=ApikeyUpto)
        url, statut = up.linkDownload(link)
        return url, statut
    key = ADDON.getSetting("keyalldebrid")
    if key:
        up = Alldedrid(key=key)
        url, statut = up.linkDownload(link)
        return url, statut
    return "", "pas de key debrid"

def playMediaUptobox(params):
    notice(params)
    #{'action': 'playMediaUptobox', 'lien': 'g0r0exdlkawk', 'u2p': '86430', 'episode': '1', 'saison': '1', 'rep': '//emby/series/Your Honor TM86430TM/Saison 01'}
    #{'action': 'playMediaUptobox', 'lien': 'ktpgmdw8gx0p', 'u2p': '119950', 'typM': '(S01E4)'}
    #{'action': 'playMediaUptobox', 'lien': '8arzvw60723w', 'u2p': '959810'}
    trk = actifTrakt()
    link = params['lien']
    url, statut = debridLien(link)
    if url:
        result = {"url": url, "title": unquote(url.split("/")[-1])}
        if result and "url" in result.keys():
            listIt = createListItemFromVideo(result)
            xbmcplugin.setResolvedUrl(HANDLE, True, listitem=listIt)
            """
            # scrobble
            try:
                if trk and numId != "divers" and str(numId) != "0":
                    pos = 0.0
                    if typMedia == "movie":
                        trk.scrobble(title="", year=0, numId=numId, pos=pos, typM="movie", mode="start")
                    else:
                        trk.scrobble(title="", year=0, numId=numId, pos=pos, season=saison, number=numEpisode, typM="show", mode="start")
            except: pass
            while xbmc.Player().isPlaying():
                time.sleep(1)
            """

def playMediabaext(params):
    link = params['lien']
    ApikeyUpto = ADDON.getSetting("keyUpto")
    if ApikeyUpto:
        up = Uptobox(key=ApikeyUpto)
        try:
            url = up._linkDownloadUptostream(link)
        except:
            url, statut = up.linkDownload(link)
        if url:
            result = {"url": url, "title": "bande Annonce"}
            if result and "url" in result.keys():
                listIt = createListItemFromVideo(result)
                xbmcplugin.setResolvedUrl(HANDLE, True, listitem=listIt)

def addDirNext(params):
    isFolder = True
    li = xbmcgui.ListItem(label="[COLOR red]Page Suivante[/COLOR]")
    li.setInfo('video', {"title": "     ", 'plot': "", 'genre': "", "dbid": 500000,
            "year": "", 'mediatype': "movies", "rating": 0.0})
    li.setArt({
              'thumb': 'special://home/addons/plugin.video.sendtokodiU2P/resources/png/next.png',
              'icon': ADDON.getAddonInfo('icon'),
              'fanart': ADDON.getAddonInfo('fanart'),
              })
    try:
        params["offset"] = str(int(params["offset"]) + NBMEDIA)
    except: pass
    url = sys.argv[0] + '?' + urlencode(params)
    return xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=isFolder)

def getHistoUpto(bd):
    cnx2 = sqlite3.connect(bd)
    cur2 = cnx2.cursor()
    cur2.execute("SELECT (SELECT f.strFilename FROM files as f WHERE b.idFile=f.idFile) FROM bookmark as b")
    bookmark = [x[0] for x in cur2.fetchall() if "playMediaUptobox" in x[0]]
    cur2.close()
    cnx2.close()
    mDB = TMDB(KEYTMDB)
    for i, media in enumerate(bookmark):
        params = dict(parse_qsl(media.split("?")[1]))
        #notice(params)
        numId = params["u2p"]
        link = params["lien"]
        if "rep" in params.keys():
            threading.Thread(name="tet", target=mDB.tvshowId, args=(" (S%sE%s)" %(params["saison"], params["episode"]), link, i, numId, media.split("?")[1])).start()
        elif "typM" in params.keys():
            threading.Thread(name="tet", target=mDB.tvshowId, args=(" %s" %(params["typM"]), link, i, numId, media.split("?")[1])).start()
        else:
            threading.Thread(name="tet", target=mDB.movieNumId, args=(link, i, numId,)).start()
    #while threading.active_count() > 1:
    #    time.sleep(0.1)
    testThread()
    medias = mDB.extractListe
    affUptobox("movie", [x[1:]  for x in medias if x[1] != "Inconnu"], params)

if __name__ == '__main__':
    pass
