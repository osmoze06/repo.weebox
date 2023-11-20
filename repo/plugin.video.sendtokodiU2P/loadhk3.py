import time
import sys
import sqlite3
import os
import requests
import threading

pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor

try:
    import xbmc
    import xbmcvfs
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
    ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
    BDREPO = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mymedia.db')
    BDREPONEW = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/mediasNew.bd')
    CHEMIN = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P')
    CHEMINPASTE = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/pastes')
    NUMHEBERG = ADDON.getSetting("numHeberg")
    HEBERG = ADDON.getSetting("heberg")
    KEYTMDB = ADDON.getSetting("apikey")
    try:
        os.mkdir(CHEMINPASTE)
    except: pass
    try:
        from util import *
    except:
        def notice(content):
            log(content, xbmc.LOGINFO)

        def log(msg, level=xbmc.LOGINFO):
            addon = xbmcaddon.Addon()
            addonID = ADDON.getAddonInfo('id')
            xbmc.log('%s: %s' % (addonID, msg), level)

        def showInfoNotification(message):
            xbmcgui.Dialog().notification("U2Pplay", message, xbmcgui.NOTIFICATION_INFO, 5000)
except: pass

class BDMedia:
    def __init__(self, database="../bdFinal/mediasNew.bd"):
        self.database = database
        notice(database)
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS seriesPub(
                id INTEGER PRIMARY KEY,
                numId INTEGER,
                title TEXT,
                overview TEXT,
                poster TEXT,
                year TEXT,
                genres TEXT,
                backdrop TEXT,
                popu REAL,
                votes INTEGER,
                dateRelease TEXT,
                runtime INTEGER,
                lang TEXT,
                logo TEXT,
                saga INTEGER,
                certif INTEGER,
                imdb TEXT,
                maj INTEGER,
                actif INTEGER default 1,
                UNIQUE (numId))
              """)
        cur.execute("""CREATE TABLE IF NOT EXISTS seriesfolderHash(
              id INTEGER PRIMARY KEY,
              numId INTEGER,
              folder TEXT,
              hsh TEXT,
              actif INTEGER DEFAULT 1,
              UNIQUE (numId, folder, hsh))
                """)
        cur.execute("""CREATE TABLE IF NOT EXISTS seriesRepos(
              nom TEXT,
              numId INTEGER,
              actif INTEGER DEFAULT 1,
              UNIQUE (nom, numId))
                """)
        cur.execute("""CREATE TABLE IF NOT EXISTS episodes(
              id INTEGER PRIMARY KEY,
              numId INTEGER,
              saison INTEGER,
              episode INTEGER,
              link TEXT,
              release TEXT,
              taille TEXT,
              UNIQUE (numId, link))
                """)
        cur.execute("""CREATE TABLE IF NOT EXISTS numMaj(
              num INTEGER,
              nom TEXT,
              UNIQUE (nom))""")
        cur.execute("""CREATE TABLE IF NOT EXISTS filmsPub(
                id INTEGER PRIMARY KEY,
                numId INTEGER,
                title TEXT,
                overview TEXT,
                poster TEXT,
                year TEXT,
                genres TEXT,
                backdrop TEXT,
                popu REAL,
                votes INTEGER,
                dateRelease TEXT,
                runtime INTEGER,
                lang TEXT,
                logo TEXT,
                saga INTEGER,
                certif INTEGER,
                imdb TEXT,
                maj INTEGER,
                actif INTEGER default 1,
                UNIQUE (numId))
              """)
        cur.execute("""CREATE TABLE IF NOT EXISTS filmsPubLink(
              id INTEGER PRIMARY KEY,
              numId INTEGER,
              link TEXT,
              release TEXT,
              taille TEXT,
              UNIQUE (numId, link))
                """)
        cur.execute("""CREATE TABLE IF NOT EXISTS filmsRepos(
              famille TEXT,
              nom TEXT,
              numId INTEGER,
              actif INTEGER DEFAULT 1,
              UNIQUE (famille, nom, numId))
                """)

        cur.execute("""CREATE TABLE IF NOT EXISTS diversPub(
                id INTEGER PRIMARY KEY,
                numId INTEGER,
                title TEXT,
                overview TEXT,
                poster TEXT,
                year TEXT,
                genres TEXT,
                backdrop TEXT,
                popu REAL,
                votes INTEGER,
                dateRelease TEXT,
                runtime INTEGER,
                lang TEXT,
                logo TEXT,
                saga INTEGER,
                certif INTEGER,
                imdb TEXT,
                maj INTEGER,
                actif INTEGER default 1,
                UNIQUE (numId))
              """)
        cur.execute("""CREATE TABLE IF NOT EXISTS diversPubLink(
              id INTEGER PRIMARY KEY,
              numId INTEGER,
              link TEXT,
              release TEXT,
              taille TEXT,
              UNIQUE (numId, link))
                """)
        cur.execute("""CREATE TABLE IF NOT EXISTS diversRepos(
              famille TEXT,
              nom TEXT,
              numId INTEGER,
              actif INTEGER DEFAULT 1,
              UNIQUE (famille, nom, numId))
                """)

        cur.execute("""CREATE TABLE IF NOT EXISTS divers(
            id INTEGER PRIMARY KEY,
            nom TEXT,
            title TEXT,
            folder TEXT,
            hsh TEXT,
            theme TEXT,
            maj INTEGER,
            actif INTEGER default 1,
            UNIQUE (nom))
              """)

        listTables = cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='divC'; """).fetchall()
        if not listTables:
            print("delete")
            cur.execute("""CREATE TABLE IF NOT EXISTS divC (nom TEXT)""")
            cur.execute("DROP TABLE divers")

            cur.execute("""CREATE TABLE IF NOT EXISTS divers(
                id INTEGER PRIMARY KEY,
                nom TEXT,
                title TEXT,
                folder TEXT,
                hsh TEXT,
                theme TEXT,
                maj INTEGER,
                actif INTEGER default 1,
                UNIQUE (nom))
                  """)
        cnx.commit()
        cur.close()
        cnx.close()


    def getMaj(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT num FROM numMaj")
        try:
            num = [x[0] for x in cur.fetchall()]
        except:
            num = []
        cur.close()
        cnx.close()
        return num

    def setMaj(self, num):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("REPLACE INTO numMaj (num, nom) VALUES (?, ?)", (num, num,))
        cnx.commit()
        cur.close()
        cnx.close()


    def reinitTables(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("DELETE FROM filmsRepos")
        cur.execute("UPDATE filmsPub set actif=0")
        cur.execute("DELETE FROM filmsPubLink")
        cnx.commit()
        cur.close()
        cnx.close()

    def reinitTablesSeries(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("UPDATE seriesfolderHash set actif=0")
        cur.execute("UPDATE seriesPub set actif=0")
        cur.execute("DELETE FROM seriesRepos")
        cnx.commit()
        cur.close()
        cnx.close()

    def reinitTablesDivers(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("UPDATE divers set actif=0")
        cnx.commit()
        cur.close()
        cnx.close()

    def getNumid(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()
        cur.execute("SELECT numId FROM filmsPub")
        tabFilms = cur.fetchall()
        cur.close()
        cnx.close()
        return tabFilms


    def joinBD(self):
        cnx = sqlite3.connect(self.database)
        cur = cnx.cursor()

        cnx2 = sqlite3.connect(os.path.join(CHEMIN, "combine.bd"))
        cur2 = cnx2.cursor()

        #rentry
        cur2.execute("SELECT num, nom FROM numMaj")
        liste = cur2.fetchall()
        if liste:
            cur.executemany("REPLACE INTO numMaj (num, nom) VALUES (?, ?)", liste)

        # films
        cur2.execute("SELECT numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb, maj, actif FROM filmsPub")
        liste = cur2.fetchall()
        if liste:
            cur.executemany("REPLACE INTO filmsPub (numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb, maj, actif) \
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", liste)

            cur2.execute("SELECT famille, nom, numId, actif FROM filmsRepos")
            cur.executemany("REPLACE INTO filmsRepos (famille, nom, numId, actif) VALUES (?, ?, ?, ?)", cur2.fetchall())

            cur.executemany("REPLACE INTO filmsPubLink (numId, link, release, taille) VALUES (?, ?, ?, ?)", cur2.execute("SELECT numId, link, release, taille FROM filmsPubLink"))


        # series
        cur2.execute("SELECT numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb, maj, actif FROM seriesPub")
        liste = cur2.fetchall()
        if liste:
            cur.executemany("REPLACE INTO seriesPub (numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb, maj, actif) \
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", liste)

            cur2.execute("SELECT nom, numId, actif FROM  seriesRepos")
            cur.executemany("REPLACE INTO seriesRepos (nom, numId, actif) VALUES (?, ?, ?)", cur2.fetchall())

            cur2.execute("SELECT numId, saison, episode, link, release, taille FROM episodes")
            cur.executemany("REPLACE INTO episodes (numId, saison, episode, link, release, taille) VALUES (?, ?, ?, ?, ?, ?)", cur2.fetchall())
            actu = 1

        #divers
        cur2.execute("SELECT nom, title, folder, hsh, theme, maj, actif FROM divers")
        cur.executemany("REPLACE INTO divers (nom, title, folder, hsh, theme, maj, actif) VALUES (?, ?, ?, ?, ?, ?, ?)", cur2.fetchall())


        cnx.commit()
        cur2.close()
        cnx2.close()

        cur.close()
        cnx.close()

class PopupWindowNew(xbmcgui.WindowDialog):
    def __init__(self, image, films=[], series=[]):
        ajoutSerie = max([0, 7 - len(films)])
        ajoutFilm = max([0, 7 - len(series)])
        l = 70
        lc = 100
        if series:
            lc += 55
        if films:
            lc += 55
        lc += min(14, len(films) + len(series)) * (l + 5)
        self.addControl(xbmcgui.ControlImage(x=20, y=15, width=lc, height=100, filename=xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/back.png')))
        self.addControl(xbmcgui.ControlImage(x=20, y=15, width=100, height=100, filename=image))
        x = 125
        if films:
            self.addControl(xbmcgui.ControlLabel(x=125, y=20, width=100, height=80, label="Last\nFilms"))
            x = 180
            for i, img in enumerate(films[: 7 + ajoutSerie]):
                if img:
                    image2 = "http://image.tmdb.org/t/p/w185" + img
                else:
                    image2 = ""
                pos = (x + (i * l) + (5 * i))
                self.addControl(xbmcgui.ControlImage(x=pos, y=15, width=l, height=100, filename=image2))
            pos += (l + 5)
        else:
            pos = x
        if series:
            self.addControl(xbmcgui.ControlLabel(x=pos, y=20, width=100, height=80, label="Last\nSeries"))
            x = pos + 55
            for i, img in enumerate(series[: 7 + ajoutSerie]):
                image2 = "http://image.tmdb.org/t/p/w185" + img
                pos = (x + (i * l) + (5 * i))
                self.addControl(xbmcgui.ControlImage(x=pos, y=15, width=l, height=100, filename=image2))



class CryptLink:

    def cryptFile(self, f, cr=1):
        tab0 = 'wTfLtya01MnzeYSW9d4FoHcNkJZCvXQ3bgiGpEu825RrjP7OVKUxDqAIlsBh6m'
        tab1 = "zvlEitNwd0bPqasYDArjgnJKIOoCSp589mM2TFy6WZk1RuxGBQL3hX7cHfeVU4"
        if cr:
            num = self.crypt(f, tab0, tab1)
        else:
            num = self.decrypt(f, tab0, tab1)
        return num

    def crypt(self, tx, tab0, tab1):
        texCrypt = ""
        tx = tx.strip()
        for j, t in enumerate(tx):
            try:
                tab0 = self._swapKey(tab0, j)
                d = {x: tab1[i] for i, x in enumerate(tab0)}
                texCrypt += d[t]
            except: pass
        return texCrypt

    def decrypt(self, tx, tab0, tab1):
        texCrypt = ""
        tx = tx.strip()
        #notice(tx)
        for j, t in enumerate(tx):
            tab0 = self._swapKey(tab0, j)
            d = {x: tab0[i] for i, x in enumerate(tab1)}
            texCrypt += d[t]
        return texCrypt

    def _swapKey(self, key, swap):
        key = "".join([key[(i + swap) % len(key)]  for i in range(len(key))])
        return key

class TMDBlinks:
    def __init__(self, key, database):
        self.key = key
        self.database = database
        self.tabSql = []
        self.dictInfosFilm = {}
        self.dictInfosSerie = {}
        self.numMaj = 0
        self.tabNumIdFilm = []

    def tvshowId(self, numId):
        """infos series suivant numID"""
        url1 = "https://api.themoviedb.org/3/tv/{}?api_key={}&language=fr&append_to_response=images,external_ids".format(numId, self.key)
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()

        title = dictInfos.get("name", "")
        poster = dictInfos.get("poster_path", "")
        backdrop = dictInfos.get("backdrop_path", "")
        try:
            genres = ", ".join([z for y in dictInfos["genres"] for x, z in y.items() if x =="name"])
        except:
            genres = ""
        try:
            year = dictInfos.get("first_air_date", '2010')[:4]
        except:
            year = "2010"
        overview = dictInfos.get("overview", "sans synopsis.....")
        popu = dictInfos.get("vote_average", 0.0)
        lang = dictInfos.get("original_language", "")
        votes = dictInfos.get("vote_count", 0)
        dateRelease = dictInfos.get("first_air_date", "2010-06-10")
        try:
            runTime = dictInfos.get("episode_run_time", [0])[0]
        except:
            runTime = 0
        try:
            logo = dictInfos["images"]["logos"][0]["file_path"]
        except:
            logo = ""
        try:
            imdb = dictInfos['external_ids']['imdb_id']
        except:
            imdb = ""
        certif = ""
        #if imdb:
        #    certif = self.certificationIMBD(imdb)
        #print("certification: %s" %str(certif))

        return numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, "", certif, imdb

    def movieNumId(self, numId):
        """infos films suivant numID"""
        url1 = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=fr&append_to_response=images,external_ids".format(numId, self.key)
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()
        try:
          saga = dictInfos.get("belongs_to_collection", {}).get("id", 0)
        except:
          saga = 0
        title = dictInfos.get("title", "")
        poster = dictInfos.get("poster_path", "")
        backdrop = dictInfos.get("backdrop_path", "")
        try:
            genres = ", ".join([z for y in dictInfos["genres"] for x, z in y.items() if x =="name"])
        except:
            genres = ""
        year = dictInfos.get("release_date", '2010')[:4]
        overview = dictInfos.get("overview", "sans synopsis.....")
        popu = dictInfos.get("vote_average", 0.0)
        lang = dictInfos.get("original_language", "")
        votes = dictInfos.get("vote_count", 0)
        dateRelease = dictInfos.get("release_date", "2010-06-10")
        runTime = dictInfos.get("runtime", 0)
        try:
            logo = dictInfos["images"]["logos"][0]["file_path"]
        except:
            logo = ""
        try:
            imdb = dictInfos['external_ids']['imdb_id']
        except:
            imdb = ""
        certif = ""
        #if imdb:
        #    certif = self.certificationIMBD(imdb)
        #print("certification: %s" %str(certif))
        return numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb

    def insertMovie(self, numId, release, fichCr, repo="film", taille=0):
        listeGroup = ["film", "concert", "spectacle", "sport", "docu", "qc"]
        try:
            repo = listeGroup[int(repo)]
        except:
            pass
        if numId in self.dictInfosFilm.keys():
            infos = self.dictInfosFilm[numId]
        else:
            infos = self.movieNumId(numId)
            self.dictInfosFilm[numId] = infos
        majFilm = 1
        self.tabSql.append(("insertFilms", [(numId, "film", repo, fichCr, infos, self.numMaj + 1, release, taille)]))


    def insertSerie(self, numId, release, fichCr, repo="serie", saison="", episode="", taille=0):
        listeGroup = ["serie", "manga", "animation", "docu", "qc"]
        try:
            repo = listeGroup[int(repo)]
        except:
            pass
        if numId in self.dictInfosSerie.keys():
            infos = self.dictInfosSerie[numId]
        else:
            infos = self.tvshowId(numId)
            self.dictInfosSerie[numId] = infos
        if episode and saison:
            self.tabSql.append(("insertSeries", [(numId, repo, infos, self.numMaj + 1)]))
            self.tabSql.append(("insertEpisodesSerie", [(numId, saison, episode, fichCr, release, taille)]))
        else:
            notice("Pb episode/saison")


    def injectSql(self):
            cnx = sqlite3.connect(self.database)
            cur = cnx.cursor()

            if self.tabSql:
                for commande in self.tabSql:
                    md, tab = commande
                    if md == "insertFilms":
                        for t in tab:
                            numId, typFilm, theme, numCryptFilecode, infos, maj, release, taille = t
                            if maj:
                                cur.execute("REPLACE INTO filmsPub (numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb) \
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", infos)
                                cur.execute("UPDATE filmsPub set maj=? WHERE numId=?", (maj, numId,))
                            else:
                                try:
                                    cur.execute("INSERT INTO filmsPub (numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb) \
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", infos)
                                    cur.execute("UPDATE filmsPub set maj=? WHERE numId=?", (maj, numId,))
                                except: pass
                            cur.execute("UPDATE filmsPub set actif=1 WHERE numId=?", (numId,))
                            cur.execute("REPLACE INTO filmsPubLink (numId, link, release, taille) VALUES (?, ?, ?, ?)", (numId, numCryptFilecode, release, taille,))
                            cur.execute("REPLACE INTO filmsRepos (famille, nom, numId, actif) VALUES (?, ?, ?, 1)", (typFilm, theme, numId,))

                    elif md == "insertSeries":
                        for t in tab:
                            numId, theme, infos, maj = t
                            if maj:
                                cur.execute("REPLACE INTO seriesPub (numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb) \
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", infos)
                                cur.execute("UPDATE seriesPub set maj=? WHERE numId=?", (maj, numId,))
                            else:
                                try:
                                    cur.execute("INSERT INTO seriesPub (numId, title, overview, poster, year, genres, backdrop, popu, votes, dateRelease, runTime, lang, logo, saga, certif, imdb) \
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", infos)
                                    cur.execute("UPDATE seriesPub set maj=? WHERE numId=?", (maj, numId,))
                                except:
                                    pass
                            cur.execute("UPDATE seriesPub set actif=1 WHERE numId=?", (numId,))
                            cur.execute("REPLACE INTO seriesRepos (nom, numId, actif) VALUES (?, ?, 1)", (theme, numId,))
                            print("Insert Serie Ok", numId)

                    elif md == "insertEpisodesSerie":
                        cur.executemany("REPLACE INTO episodes (numId, saison, episode, link, release, taille) \
                            VALUES (?, ?, ?, ?, ?, ?)", tab)


            cnx.commit()
            cur.close()
            cnx.close()

def testThread(nom):
    a = 0
    tActif = True
    while tActif:
        tActif = False
        for t in threading.enumerate():
            if nom == t.getName():
                tActif = True
        time.sleep(0.1)
        a += 1
        if a > 600:
            return False
    return True

def resetBdFull():
    xbmcvfs.delete(os.path.join(CHEMIN, "mediasNew.bd"))
    for db in os.listdir(CHEMINPASTE):
        xbmcvfs.delete(os.path.join(CHEMINPASTE, db))
    showInfoNotification("bd effacée")

def idRentry(lePaste, d=0):
    """extraction id paste d'un rentry"""
    cr = CryptLink()
    if d:
        urlCode = cr.cryptFile(lePaste, cr=0)
    else:
        urlCode = lePaste
    x = requests.get('https://rentry.org/{}/raw'.format(urlCode)).content
    if d:
        with open(os.path.join(CHEMINPASTE, lePaste), "w") as f:
            f.write(x.decode())

    return x.decode().splitlines()

def getLinks(visu=0):
    if visu:
        pDialog2 = xbmcgui.DialogProgressBG()
        pDialog2.create('M.A.J', 'Import Pastes...')
    else:
        if not xbmc.Player().isPlaying():
            showInfoNotification("M.a.j...")
    ajoutFilm = False
    ajoutSerie = False

    a = time.time()
    bd = BDMedia(BDREPONEW)
    #tabFilms  = bd.getNumid()
    pastesImport = bd.getMaj()
    #notice(pastesImport)
    if NUMHEBERG:
        if HEBERG == "Rentry":
            tab = idRentry(NUMHEBERG)
            for t in tab[:]:
                indice = t[0]
                paste = t[1:]

                if paste not in pastesImport:
                    if os.path.isfile(os.path.join(CHEMINPASTE, paste)):
                        with open(os.path.join(CHEMINPASTE, paste), "r") as f:
                            tx = f.read()
                        linksRecup = tx.splitlines()
                    else:
                        linksRecup = []

                    mdb = TMDBlinks(KEYTMDB, BDREPONEW)
                    #mdb.tabNumIdFilm = tabFilms

                    links = idRentry(paste, d=1)
                    links = [x for x in links if x not in linksRecup]
                    for i, link in enumerate(links):
                        if i % 51 == 0 and visu:
                            pos = int(((i + 1) / len(links)) * 100)
                            pDialog2.update(pos, "M.A.J", message=paste)
                        try:
                            typM, numId, group, saison, episode, taille, filecode, release = link.split(",")
                            taille = int("0x" + taille, 16)
                            if typM.strip() == "M":
                                ajoutFilm = True
                                threading.Thread(name="getInfos", target=mdb.insertMovie, args=(numId, release, filecode, group, taille,)).start()
                            else:
                                ajoutSerie = True
                                threading.Thread(name="getInfos", target=mdb.insertSerie, args=(numId, release, filecode, group, saison, episode, taille,)).start()
                        except: pass
                        time.sleep(0.01)
                    ok = testThread("getInfos")
                    mdb.injectSql()
                    if ok:
                        if indice.upper() == "C":
                            bd.setMaj(paste)



    notice(time.time() - a)
    if visu:
        pDialog2.close()
    #ajoutSerie, ajoutFilm = True, True

    cnx = sqlite3.connect(BDREPONEW)
    cur = cnx.cursor()

    sql = "SELECT poster FROM filmsPub ORDER BY id DESC LIMIT 7 OFFSET 0"
    cur.execute(sql)
    listeTest = [x[0] for x in cur.fetchall()]

    sql = "SELECT poster FROM seriesPub ORDER BY id DESC LIMIT 7 OFFSET 0"
    cur.execute(sql)
    listeTest1 = [x[0] for x in cur.fetchall()]

    cur.close()
    cnx.close()

    if  ajoutSerie or ajoutFilm:
        if ADDON.getSetting("rskin") != "false":
            if not xbmc.Player().isPlaying():
                xbmc.executebuiltin('ReloadSkin')
                time.sleep(0.5)
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"back"},"id":1}')
            else:
                with open(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/rskin.txt'), "w") as f:
                    f.write("reload")
        #window = PopupWindowNew(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/icon.png'), list(set(newListeFilm)), list(set(newListeSerie)))
        if ADDON.getSetting("affmaj") != "false":
            window = PopupWindowNew(xbmcvfs.translatePath('special://home/addons/plugin.video.sendtokodiU2P/icon.png'), listeTest, listeTest1)
            window.show()
            xbmc.sleep(15000)
            window.close()
            del window


def joinBlocker():
    bd = BDMedia(BDREPONEW)
    bd.joinBD()
