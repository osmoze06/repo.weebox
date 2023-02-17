# -*- coding: utf-8 -*-
import os
import re
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import time
try:
  from medias import Media, TMDB
except: pass
import sqlite3
import requests
import ast


BDBOOKMARK = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db')
ADDON = xbmcaddon.Addon("plugin.video.sendtokodiU2P")

def initBookmark():
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS listeTrakt(
      nameTrakt TEXT,
      listeTrakt TEXT,
      type TEXT,
      groupe TEXT,
      groupeFille TEXT,
      UNIQUE (nameTrakt, listeTrakt))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS listesV(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      type TEXT,
      UNIQUE (nom, type))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS listesVdetail(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      numId INTEGER,
      type TEXT,
      UNIQUE (nom, numId, type))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS movie(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      UNIQUE (numId))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS tvshow2(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      saison INTEGER,
      episode INTEGER,
      UNIQUE (numId, saison, episode))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS vuEpisode(
      numId INTEGER,
      saison INTEGER,
      episode INTEGER,
      vu INTEGER,
      UNIQUE (numId, saison, episode))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS listes(
      `id`    INTEGER PRIMARY KEY,
      title TEXT,
      sql TEXT,
      type TEXT,
      UNIQUE (title))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      pass TEXT,
      UNIQUE (pass))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS certification(
      pass TEXT,
      certification INTEGER,
      sans INTEGER,
      UNIQUE (pass))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS favs(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      type TEXT,
      UNIQUE (numId))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS paste(
      nom TEXT,
      numPaste TEXT,
      pos INTEGER,
      type TEXT,
      UNIQUE (nom, numPaste))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS tmdb(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      type TEXT,
      numId  INTEGER,
      UNIQUE (nom, numId))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS ccertif(
        numId  INTEGER,
        type TEXT,
        certification INTEGER,
        UNIQUE (numId, type))
          """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS repUp(
        nom TEXT,
        rep TEXT,
        type TEXT,
        UNIQUE (rep))
          """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS onContinue(
        numId  INTEGER,
        UNIQUE (numId))
          """)
    cnx.commit()

    cur.close()
    cnx.close()

def createRepUpto(*argv):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS repUp(
        nom TEXT,
        rep TEXT,
        type TEXT,
        UNIQUE (rep))
          """)
  cnx.commit()
  cur.execute("REPLACE INTO repUp (nom, rep, type) VALUES (?, ?, ?)", argv)
  cnx.commit()
  cur.close()
  cnx.close()

def createRepUptoPublic(*argv):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS repUpP(
        nom TEXT,
        hash TEXT,
        folder INTEGER,
        type TEXT,
        UNIQUE (hash, folder))
          """)
  cnx.commit()
  cur.execute("REPLACE INTO repUpP (nom, hash, folder, type) VALUES (?, ?, ?, ?)", argv)
  cnx.commit()
  cur.close()
  cnx.close()

def extractRepUptoPublic():
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS repUpP(
        nom TEXT,
        hash TEXT,
        folder INTEGER,
        type TEXT,
        UNIQUE (hash, folder))
          """)
  cnx.commit()
  cur.execute("SELECT nom, hash, folder, type FROM repUpP")
  liste = cur.fetchall()
  cnx.commit()
  cur.close()
  cnx.close()
  return liste

def extractRepUpto():
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS repUp(
        nom TEXT,
        rep TEXT,
        type TEXT,
        UNIQUE (rep))
          """)
  cnx.commit()
  cur.execute("SELECT nom, rep, type FROM repUp")
  liste = cur.fetchall()
  cnx.commit()
  cur.close()
  cnx.close()
  return liste

def correctCertif(numId, typM):
  dictCertification = {"Familial":1, "10 ans": 12, "12 ans": 14, "16 ans": 17, "18 ans": 25}
  choix = list(dictCertification.keys())
  dialog = xbmcgui.Dialog()
  selected = dialog.select("Certification", choix)
  if selected != -1:
    certification = dictCertification[choix[selected]]
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS ccertif(
        numId  INTEGER,
        type TEXT,
        certification INTEGER,
        UNIQUE (numId, type))
          """)
    cnx.commit()
    cur.execute("REPLACE INTO ccertif (numId, type, certification) VALUES (?, ?, ?)", (numId, typM, certification, ))
    cnx.commit()
    cur.close()
    cnx.close()

def recupCertif(numId, typM):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS ccertif(
      numId  INTEGER,
      type TEXT,
      certification INTEGER,
      UNIQUE (numId, type))
        """)
  cnx.commit()
  cur.execute("SELECT certification FROM  ccertif WHERE numId=? AND type=?", (numId, typM, ))
  certification = cur.fetchone()
  cur.close()
  cnx.close()
  if certification:
    return certification[0]
  else:
    return 0

def createListTMDB(argv):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS tmdb(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      type TEXT,
      numId  INTEGER,
      UNIQUE (nom, numId))
        """)
  cnx.commit()
  cur.executemany("REPLACE INTO tmdb (nom, type, numId) VALUES (?, ?, ?)", argv)
  cnx.commit()
  cur.close()
  cnx.close()


def insertTrakt(*argv):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS listeTrakt(
      nameTrakt TEXT,
      listeTrakt TEXT,
      type TEXT,
      groupe TEXT,
      groupeFille TEXT,
      UNIQUE (nameTrakt, listeTrakt))
        """)
  cnx.commit()
  cur.execute("REPLACE INTO listeTrakt (nameTrakt, listeTrakt, type, groupe, groupeFille) VALUES (?, ?, ?, ?, ?)", argv)
  cnx.commit()
  cur.close()
  cnx.close()

def insertPaste(argv):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS paste(
      nom TEXT,
      numPaste TEXT,
      pos INTEGER,
      type TEXT,
      UNIQUE (nom, numPaste))
        """)
  cnx.commit()
  cur.executemany("REPLACE INTO paste (nom, numPaste, pos, type) VALUES (?, ?, ?, ?)", argv)
  cnx.commit()
  cur.close()
  cnx.close()

def recupPaste(nom, typM):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("SELECT numPaste FROM paste WHERE nom=? AND type=?ORDER BY pos asc", (nom, typM, ))
  liste = [x[0] for x in cur.fetchall()]
  cur.close()
  cnx.close()
  return liste

def recupTMDB(nom, typM):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("SELECT numId FROM tmdb WHERE nom=? AND type=? ORDER BY id asc", (nom, typM, ))
  liste = [x[0] for x in cur.fetchall()]
  cur.close()
  cnx.close()
  return liste

def extractListPaste():
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("SELECT nom, type FROM paste GROUP BY nom, type")
  liste = cur.fetchall()
  cur.close()
  cnx.close()
  return liste

def extractListTMDB():
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("SELECT nom, type FROM tmdb GROUP BY nom, type")
  liste = cur.fetchall()
  cur.close()
  cnx.close()
  return liste

def getListesT(typM="movie"):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS listeTrakt(
      nameTrakt TEXT,
      listeTrakt TEXT,
      type TEXT,
      groupe TEXT,
      groupeFille TEXT,
      UNIQUE (nameTrakt, listeTrakt))
        """)
  cnx.commit()
  cur.execute("SELECT * FROM listeTrakt WHERE type=?", (typM,))
  liste = cur.fetchall()
  cur.close()
  cnx.close()
  return liste


def createListeV(nom, media):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS listesV(
    `id`    INTEGER PRIMARY KEY,
    nom TEXT,
    type TEXT,
    UNIQUE (nom, type))
      """)
  cnx.commit()
  cur.execute("""CREATE TABLE IF NOT EXISTS listesVdetail(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      numId INTEGER,
      type TEXT,
      UNIQUE (nom, numId, type))
        """)
  cnx.commit()
  cur.execute("REPLACE INTO listesV (nom, type) VALUES (?, ?)", (nom, media, ))
  cnx.commit()
  cur.close()
  cnx.close()

def getListesV(t):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS listesV(
    `id`    INTEGER PRIMARY KEY,
    nom TEXT,
    type TEXT,
    UNIQUE (nom, type))
      """)
  cnx.commit()
  cur.execute("SELECT nom FROM listesV WHERE type=?", (t,))
  liste = [x[0] for x in cur.fetchall()]
  cnx.commit()
  cur.close()
  cnx.close()
  return liste

def getListesVdetail(nom, t):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS listesVdetail(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      numId INTEGER,
      type TEXT,
      UNIQUE (nom, numId, type))
        """)
  cnx.commit()
  cur.execute("SELECT numId FROM listesVdetail WHERE type=? and nom=?", (t, nom,))
  liste = [x[0] for x in cur.fetchall()]
  cnx.commit()
  cur.close()
  cnx.close()
  return liste

def gestionListeVdetail(nom, numId, t, mode):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS listesVdetail(
      `id`    INTEGER PRIMARY KEY,
      nom TEXT,
      numId INTEGER,
      type TEXT,
      UNIQUE (nom, numId, type))
        """)
  cnx.commit()
  if mode == "ajout":
    cur.execute("REPLACE INTO listesVdetail (nom, numId, type) VALUES (?, ?, ?)", (nom, numId, t))
  else:
    cur.execute("DELETE FROM listesVdetail  WHERE nom=? AND numId=? AND type=?", (nom, numId, t))
  cnx.commit()
  cur.close()
  cnx.close()


def getCertification(passwd):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS certification(
        pass TEXT,
        certification INTEGER,
        sans INTEGER,
        UNIQUE (pass))
          """)
    cnx.commit()
    cur.execute("SELECT certification, sans FROM certification WHERE pass=?", (passwd, ))
    data = cur.fetchall()
    cur.close()
    cnx.close()
    try:
      return data[0]
    except:
      return [25, 1]


def showInfoNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message, xbmcgui.NOTIFICATION_INFO, 5000)

def testSite(url):
  site = ADDON.getSetting("bookonline_site")
  if site not in url:
    url = "http://%s/requete.php?%s" %(site.strip(), url.split("?")[1])
  return url

def responseSite(url):
    if "lesalkodiques.com" in  ADDON.getSetting("bookonline_site"):
      url = "https://lesalkodiques.com/u2pplay/requete.php?%s"  %(url.split("?")[1].strip())
    resp = requests.get(url)
    data = resp.json()
    return data

def pushSite(url):
    url = testSite(url)
    url = "/".join([x.strip() for x in url.split("/")])
    try:
      resp = requests.get(url)
    except:
      try:
        url = url.replace("http:", "https:")
        resp = requests.get(url)
      except: pass

def getVu(typM="movie"):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    if typM == "movie":
        pass
    else:
        sql = "SELECT numId, saison, episode FROM vuEpisode WHERE vu>0"
        cur.execute(sql)
        vus = ["%d-%d-%d" %x for x in cur.fetchall()]

    cur.close()
    cnx.close()
    return vus

def usersBookmark():
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
          `id`    INTEGER PRIMARY KEY,
          nom TEXT,
          pass TEXT,
          UNIQUE (pass))
            """)
    cnx.commit()
    sql = "SELECT nom, pass FROM users"
    cur.execute(sql)
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    return liste

def setVu(numId, saison, episode, vu, typM="movie"):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    if typM == "movie":
        pass
    else:
        sql = "REPLACE INTO vuEpisode (numId, saison, episode, vu) VALUES ({}, {}, {}, {})".format(numId, saison, episode, vu)
        cur.execute(sql)
        cnx.commit()

    cur.close()
    cnx.close()

def getProfil(passwd):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
          `id`    INTEGER PRIMARY KEY,
          nom TEXT,
          pass TEXT,
          UNIQUE (pass))
            """)
    cnx.commit()
    sql = "SELECT nom FROM users WHERE pass=?"
    try:
        cur.execute(sql, (passwd,))
        nom = cur.fetchone()[0]
    except:
        showInfoNotification("Creer in profil .....")
        nom = "inconnu"
    cur.close()
    cnx.close()
    return nom


def bdHK(sauve=1, pos=0, tt=0, numId=0, extract=0, typM="movie", saison=0, episode=0):
    rPos = 0
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS movie(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      UNIQUE (numId))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS tvshow2(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      saison INTEGER,
      episode INTEGER,
      UNIQUE (numId, saison, episode))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS vuEpisode(
      numId INTEGER,
      saison INTEGER,
      episode INTEGER,
      vu INTEGER,
      UNIQUE (numId, saison, episode))
        """)
    cnx.commit()
    if extract:
        if typM == "movie":
            cur.execute("SELECT numId FROM movie ORDER BY id DESC")
        else:
            cur.execute("SELECT DISTINCT numId FROM tvshow2 ORDER BY id DESC")
        rPos = [x[0] for x in cur.fetchall()]
    elif sauve:
        if typM == "movie":
            cur.execute("REPLACE iNTO movie (numId, pos, tt) VALUES ({}, {}, {})".format(numId, pos, tt))
        else:
            cur.execute("REPLACE iNTO tvshow2 (numId, pos, tt, saison, episode) VALUES ({}, {}, {}, {}, {})".format(numId, pos, tt, saison, episode))
        cnx.commit()
        if tt and ((pos / tt) * 100) > 90 :
            sql = "REPLACE INTO vuEpisode (numId, saison, episode, vu) VALUES ({}, {}, {}, 1)".format(numId, saison, episode)
            cur.execute(sql)
            cnx.commit()
            # push into on continue
            gestOC(numId, "ajout")

    else:
        if typM == "movie":
            cur.execute("SELECT pos FROM movie WHERE numId={}".format(numId))
        else:
            cur.execute("SELECT pos FROM tvshow2 WHERE numId={} AND saison='{}' AND episode='{}'".format(numId, saison, episode))
        try:
            rPos = cur.fetchone()[0]
        except: pass
    cur.close()
    cnx.close()
    return rPos

def extractIdInVu(t="movies"):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS movie(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      UNIQUE (numId))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS tvshow2(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      saison INTEGER,
      episode INTEGER,
      UNIQUE (numId, saison, episode))
        """)
    cnx.commit()
    if t == "movies":
        sql = "SELECT numId FROM movie"
    else:
        sql = "SELECT numId FROM tvshow2"
    cur.execute(sql)
    listes = [x[0] for x in cur.fetchall() if x]
    cur.close()
    cnx.close()
    return listes

def getFavs():
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS favs(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      type TEXT,
      UNIQUE (numId))
        """)
    cnx.commit()
    sql = "SELECT numId, type FROM favs ORDER BY id DESC"
    cur.execute(sql)
    listes = cur.fetchall()
    cur.close()
    cnx.close()
    return listes

def extractOC():
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS onContinue(
      numId INTEGER,
      UNIQUE (numId))
        """)
    cnx.commit()
    sql = "SELECT numId FROM onContinue"
    cur.execute(sql)
    listes = [x[0] for x in cur.fetchall()]
    cur.close()
    cnx.close()
    return listes

def gestOC(numId, typ):
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS onContinue(
    numId INTEGER,
    UNIQUE (numId))
      """)
  cnx.commit()
  if typ == "ajout":
    sql = "REPLACE INTO onContinue (numId) VALUES ({})".format(numId)
  else:
    sql = "DELETE FROM onContinue WHERE numId={}".format(numId)
  cur.execute(sql)
  cnx.commit()
  cur.close()
  cnx.close()


def extractFavs(t="movies"):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS favs(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      type TEXT,
      UNIQUE (numId))
        """)
    cnx.commit()
    sql = "SELECT numId FROM favs WHERE type=?"
    cur.execute(sql, (t, ))
    listes = [x[0] for x in cur.fetchall() if x]
    cur.close()
    cnx.close()
    return listes

def ajoutFavs(numId, t):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS favs(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      type TEXT,
      UNIQUE (numId))
        """)
    cnx.commit()
    sql = "REPLACE INTO favs (numId, type) VALUES (?, ?)"
    cur.execute(sql, (numId, t, ))
    cnx.commit()
    cur.close()
    cnx.close()

def supFavs(numId, t):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS favs(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      type TEXT,
      UNIQUE (numId))
        """)
    cnx.commit()
    sql = "DELETE FROM favs WHERE numId=? AND type=?"
    cur.execute(sql, (numId, t, ))
    cnx.commit()
    cur.close()
    cnx.close()

def supView(numId, t):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS movie(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      UNIQUE (numId))
        """)
    cnx.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS tvshow2(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      pos REAL,
      tt REAL,
      saison INTEGER,
      episode INTEGER,
      UNIQUE (numId, saison, episode))
        """)
    cnx.commit()
    if t == "movies":
        sql = "DELETE FROM movie WHERE numId=?"
    else:
        sql = "DELETE FROM tvshow2 WHERE numId=?"
    cur.execute(sql, (numId, ))
    cnx.commit()
    cur.close()
    cnx.close()

def extractListe(t="film"):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS listes(
      `id`    INTEGER PRIMARY KEY,
      title TEXT,
      sql TEXT,
      type TEXT,
      UNIQUE (title))
        """)
    cnx.commit()
    if t == "all":
        sql = "SELECT title FROM listes"
        cur.execute(sql)
    else:
        sql = "SELECT title FROM listes WHERE type=?"
        cur.execute(sql, (t, ))
    listes = [x[0] for x in cur.fetchall() if x]
    cur.close()
    cnx.close()
    return listes

def supListe(liste):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS listes(
      `id`    INTEGER PRIMARY KEY,
      title TEXT,
      sql TEXT,
      type TEXT,
      UNIQUE (title))
        """)
    cnx.commit()
    for l in liste:
        sql = "DELETE FROM listes WHERE title=?"
        cur.execute(sql, (l, ))
    cnx.commit()
    cur.close()
    cnx.close()

def getListe(title, t="film"):
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS listes(
      `id`    INTEGER PRIMARY KEY,
      title TEXT,
      sql TEXT,
      type TEXT,
      UNIQUE (title))
        """)
    cnx.commit()
    sql = "SELECT sql FROM listes WHERE title=? AND type=?"
    cur.execute(sql, (title, t, ))
    requete  = cur.fetchone()[0]
    cur.close()
    cnx.close()
    return requete

def langue(tab):
    dialog = xbmcgui.Dialog()
    d = dialog.select("Selectionner langue\n(fr=francais, ja=japonais, en=anglais etc..", tab)
    if d:
        return " m.lang='{}'".format(tab[d])
    else:
        return ""

def genre(key, typM="movie"):
    mdb = TMDB(key)
    tabGenre = mdb.getGenre(typM=typM)
    dialog = xbmcgui.Dialog()
    genres = dialog.multiselect("Selectionner le/les genre(s)", tabGenre, preselect=[])
    if genres:
        genresOk = " or ".join(["m.genre LIKE '%%%s%%'" %tabGenre[x] for x in genres])
        return "(" + genresOk + ")"
    else:
        return ""

def year():
    dialog = xbmcgui.Dialog()
    d = dialog.input("Entrer Année => 2010 / Groupe d'années => 2010:2014", type=xbmcgui.INPUT_ALPHANUM)
    if d:
        an = d.split(":")
    if len(an) == 1:
        anOk = " m.year={}".format(an[0])
    else:
        anOk = " m.year>={} and m.year<={}".format(an[0], an[1])

    return anOk

def popu():
    dialog = xbmcgui.Dialog()
    d = dialog.input("Note inférieur à 9 => <9 \nNotes entre 7.5 et 9 => 7.5:9", type=xbmcgui.INPUT_ALPHANUM)
    if d:
        an = d.split(":")
    if len(an) == 1:
        anOk = " m.popu{}".format(an[0])
    else:
        anOk = " (m.popu>{} and m.popu<{})".format(an[0], an[1])

    return anOk

def votes():
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(0, 'Nombre de votes sup à')
    if d:
        nbVotes = " m.votes>{}".format(d)
        return nbVotes
    else:
        return ""

def contenuFilm():
    typContenu = "m.numId NOT IN (SELECT sp.numId FROM movieFamille as sp WHERE sp.famille == '#Spectacles') AND genre NOT LIKE '%%Documentaire%%' AND genre NOT LIKE '%%Animation%%' AND genre != 'Musique' AND "
    return typContenu

def contenuSerie():
    typContenu = "genre NOT LIKE '%%Documentaire%%' AND genre NOT LIKE '%%Animation%%' AND genre != 'Musique' AND "
    return typContenu

def _swapKey(key, swap):
        key = "".join([key[(i + swap) % len(key)]  for i in range(len(key))])
        return key

def decrypt(tx, tab0, tab1):
    texCrypt = ""
    for j, t in enumerate(tx):
        tab0 = _swapKey(tab0, j)
        d = {x: tab0[i] for i, x in enumerate(tab1)}
        texCrypt += d[t]
    return texCrypt

def decryptKey(key, pos, numTable):
    tables = ['VaU8utB2lSwpNq0yHhF7RMTJncDbIZYXs9dAiCzmj613QxOEW4PgfGL5oKvrek', 'zOFWr7JetVh0yN6vslDxn24fwHukXmEUj5qCSTRbgiYQPIZAM1aGL9dB8oKc3p', 'kM1AUuqnNfrKWRj0tOzm7C9lYShZGcQBL5J4DyF3wXT2aEd8VvoPHpbiexgsI6',
        '9HYjEcLTutQpI0rO3M75ZvwA4GFK2koqzhUiCny6xNSdmRfJegDaVBXbs1PW8l', '0UScdanhjeNVLrFXpx3wOD7ikZ4PBsmzJM8QI5RoyqWAtfEvY1l926TuHKCgGb', 'Bb3cNFeDkW5fwvVJm2QzgPiUL9nTZE4apdMSIqHhlxYrjC0AoK81uXRsOtGy76',
        'n4tmQckyLRd13vPebl9EzhBa0MKXGj7NUf26CH8r5AFYWOopuxSDZwsiVIqJgT', 'ceQ68PDBs4huny23trq7ClvFWiAKHzZ1bgURwo9pXIOxdLNYVSkEfa0GJ5jmMT', 'jxMyhCUpStFgzs81lBvrXEOHAK6PbwiRDNd4ZTJ2oI03Lk9mucaY5V7WnQefGq',
        'j4vcoE9lfpNwTsiDRQCdUbYu5k28JBWH7SeZrqyh3L6PxKGAXVOnm1tFIMazg0']
    table = tables[numTable]
    table = table[pos:] + table[:pos]
    key = decrypt(key, table, tables[numTable - 1])
    return key

def suppListeTV():
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Listes', 'Quel type de liste ?', nolabel="Films", yeslabel="Series")
    if not ret:
        typM = "movie"
    else:
        typM = "tvshow"
    sql = "SELECT nom FROM listesV WHERE type=?"
    cur.execute(sql, (typM,))
    liste = [x[0] for x in cur.fetchall()]
    d = dialog.select("Que veux tu supprimer ?", liste)
    if d != -1:
       cur.execute("DELETE FROM listesV WHERE nom=? AND type=?", (liste[d], typM,))
       cur.execute("DELETE FROM listesVdetail WHERE nom=? AND type=?", (liste[d], typM,))
       cnx.commit()
    cur.close()
    cnx.close()

def suppListeT():
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Listes', 'Quel type de liste ?', nolabel="Films", yeslabel="Series")
    if not ret:
        #films
        typM = "movie"
        liste = getListesT("movie")
    else:
        typM = "show"
        liste = getListesT("show")
    choix = ["liste", "groupe"]
    dialog = xbmcgui.Dialog()
    d = dialog.select("Que veux tu supprimer ?", choix)
    if d != -1:
      dictL = {0: (4, "DELETE FROM listeTrakt WHERE groupeFille=? AND type=?"), 1: (3, "DELETE FROM listeTrakt WHERE groupe=? AND type=?")}
      listeSup = sorted(list(set([x[dictL[d][0]] for x in liste])))
      dialog = xbmcgui.Dialog()
      d2 = dialog.select("Que veux tu supprimer ?", listeSup)
      if d2 != -1:
          cnx = sqlite3.connect(BDBOOKMARK)
          cur = cnx.cursor()
          cur.execute(dictL[d][1], (listeSup[d2], typM, ))
          cnx.commit()
          cur.close()
          cnx.close()

def suppListeLP():
    cnx = sqlite3.connect(BDBOOKMARK)
    cur = cnx.cursor()
    cur.execute("SELECT DISTINCT nom FROM paste")
    choix = [x[0] for x in cur.fetchall()]
    dialog = xbmcgui.Dialog()
    d = dialog.select("Que veux tu supprimer ?", choix)
    if d != -1:
          cur.execute("DELETE FROM paste WHERE nom=?", (choix[d], ))
          cnx.commit()
    cur.close()
    cnx.close()

def suppLTMDB():
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("SELECT DISTINCT nom FROM tmdb")
  choix = [x[0] for x in cur.fetchall()]
  dialog = xbmcgui.Dialog()
  d = dialog.select("Que veux tu supprimer ?", choix)
  if d != -1:
        cur.execute("DELETE FROM tmdb WHERE nom=?", (choix[d], ))
        cnx.commit()
  cur.close()
  cnx.close()


def suppLUPTO():
  cnx = sqlite3.connect(BDBOOKMARK)
  cur = cnx.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS repUp(
        nom TEXT,
        rep TEXT,
        type TEXT,
        UNIQUE (rep))
          """)
  cnx.commit()
  cur.execute("""CREATE TABLE IF NOT EXISTS repUpP(
        nom TEXT,
        hash TEXT,
        folder INTEGER,
        type TEXT,
        UNIQUE (hash, folder))
          """)
  cnx.commit()
  dialog = xbmcgui.Dialog()
  ret = dialog.yesno('Listes', 'Quel type de liste ?', nolabel="Rep", yeslabel="Rep Publique")
  if not ret:
    #rep
    cur.execute("SELECT DISTINCT nom FROM repUp")
    sql ="DELETE FROM repUp WHERE nom=?"
  else:
    #rep publique
    cur.execute("SELECT DISTINCT nom FROM repUpP")
    sql = "DELETE FROM repUpP WHERE nom=?"
  choix = [x[0] for x in cur.fetchall()]
  dialog = xbmcgui.Dialog()
  d = dialog.select("Que veux tu supprimer ?", choix)
  if d != -1:
        cur.execute(sql, (choix[d], ))
        cnx.commit()
  cur.close()
  cnx.close()


