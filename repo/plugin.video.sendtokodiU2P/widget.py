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
from medias import Media, TMDB
import sqlite3
import requests
import ast

def initBookmark():
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cur.execute("""CREATE TABLE IF NOT EXISTS favs(
      `id`    INTEGER PRIMARY KEY,
      numId INTEGER,
      type TEXT,
      UNIQUE (numId))
        """)
    cnx.commit()
    cur.close()
    cnx.close()


def showInfoNotification(message):
    xbmcgui.Dialog().notification("U2Pplay", message, xbmcgui.NOTIFICATION_INFO, 5000)

def responseSite(url):
    resp = requests.get(url)
    data = resp.json()
    return data

def pushSite(url):
    resp = requests.get(url)
    
def getVu(typM="movie"):
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
    cur = cnx.cursor()
    sql = "SELECT nom, pass FROM users"
    cur.execute(sql)
    liste = cur.fetchall()
    cur.close()
    cnx.close()
    return liste

def setVu(numId, saison, episode, vu, typM="movie"):
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
    cur = cnx.cursor()
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
        if tt and ((pos / tt) * 100) > 95 :
            sql = "REPLACE INTO vuEpisode (numId, saison, episode, vu) VALUES ({}, {}, {}, 1)".format(numId, saison, episode)
            cur.execute(sql)
            cnx.commit()

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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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

def extractFavs(t="movies"):
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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
    cnx = sqlite3.connect(xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.video.sendtokodiU2P/bookmark.db'))
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



