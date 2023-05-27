# -*- coding: utf-8 -*-
import json
import os
import sys
import requests
import io
import unicodedata
import re
import ast
import sqlite3
import shutil
import time
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin

try:
    # Python 3
    from urllib.parse import parse_qsl
except ImportError:
    from urlparse import parse_qsl
try:
    # Python 3
    from urllib.parse import unquote, urlencode
    unichr = chr
except ImportError:
    # Python 2
    from urllib import unquote, urlencode
try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser

pyVersion = sys.version_info.major
pyVersionM = sys.version_info.minor
if pyVersionM == 11:
    import cryptPaste11 as cryptage
elif pyVersionM == 8:
    import cryptPaste8 as cryptage
elif pyVersionM == 9:
    import cryptPaste9 as cryptage
else:
    import cryptPaste10 as cryptage
    
class Pastebin:
    CAT, TMDB , TITLE, SAISON, GROUPES , YEAR, GENRES , RES , URLS = -1, -1, -1, -1, -1, -1, -1, -1, -1

    def __init__(self, **kwargs):
        for attr_name, attr_value in kwargs.items():
            setattr(self, attr_name, attr_value)
        self.adrPbi = "http://pastebin.com/raw/"
        self.fournisseur = ""
        self.dictFilmsPaste = {}
        self.dictSeriesPaste = {}
        self.dictAnimesPaste = {}
        self.dictDiversPaste = {}
        self.dictGroupeFilms = {}
        self.dictGroupeSeries = {}
        self.dictGroupeAnimes = {}
        self.dictGroupeDivers = {}
        self.dictBa = {}
        self.tabIdPbi = list(set(self.tabIdPbi))
        self.cr = cryptage.Crypt()
        [self.loadPaste(x) for x in self.tabIdPbi]


    def loadPaste(self, num):
        """import liste media via un pastebin"""
        self.numPaste = num
        #r = requests.get(self.adrPbi + num, timeout=2)#, verify=False, allow_redirects=True)
        #rr = r.text
        #lignes = rr.splitlines()

        lignes = self.cr.loadFile(self.numPaste)
        for ligne in lignes[:1]:
            l = ligne.split(";")
            for j, v in enumerate(l):
                if "GROUPES" in v:
                    v = v.split("=")[0]
                elif "URLS" in v:
                    v, self.fournisseur = v.split("=")
                    self.fournisseur = self.fournisseur.replace(" ", "")
                setattr(self, v, j)

        tabFilms = [l.split(";") for l in lignes if l.split(";")[self.CAT] == "film"]
        tabSeries = [l.split(";") for l in lignes if l.split(";")[self.CAT] == "serie"]
        tabAnimes = [l.split(";") for l in lignes if l.split(";")[self.CAT] == "anime"]
        tabDivers = [l.split(";") for l in lignes if l.split(";")[self.CAT] == "divers"]
        if tabFilms:
            self.loadFilm(tabFilms)
        if tabSeries:
            self.loadSerie(tabSeries)
        if tabAnimes:
            self.loadAnime(tabAnimes)
        if tabDivers:
            self.loadDivers(tabDivers)

    def loadDivers(self, films):
        for j, film in enumerate(films):
            try:
                if len(film) > 12:
                    tmp  = film.pop(3)
                    film[2] = film[2] + " : " + tmp
                groupes = ast.literal_eval(film[self.GROUPES])
                title = film[self.TITLE]
                if pyVersion == 2:
                    title = unicode(title, "utf8", "replace")
                for groupe in groupes:
                    if groupe in self.dictGroupeDivers.keys():
                        self.dictGroupeDivers[groupe].append(title)
                    else:
                        self.dictGroupeDivers[groupe] = [title]
                tabFormat = ast.literal_eval(film[self.RES])
                if film[self.TITLE] in self.dictDiversPaste.keys():
                    self.dictDiversPaste[title][2] = self.dictDiversPaste[title][2] + "," + ",".join(["%s@%s#%s" %(self.numPaste, x, tabFormat[i]) for i, x in  enumerate(ast.literal_eval(film[self.URLS]))])
                else:
                    self.dictDiversPaste[title] = [film[self.TITLE] + "-" + film[self.YEAR], film[self.TMDB], ",".join(["%s@%s#%s" %(self.numPaste, x, tabFormat[i]) for i, x in  enumerate(ast.literal_eval(film[self.URLS]))])]
            except:
                #notice("erreur: %s" %film)
                pass
        #notice("nb Divers : %d" %len(self.dictDiversPaste.keys()))

    def makeDiversNFO(self, liste, sendToKodi=1, clear=0, progress=None, nomRep=""):

        try:
            if self.name in self.repKodiName:
                os.mkdir(self.repKodiName)
        except: pass

        if nomRep:
            repFilm = os.path.join(self.repKodiName, nomRep + "/")
            try:
                os.mkdir(repFilm)
            except: pass
        else:
            repFilm = self.repKodiName

        repFilm = os.path.join(repFilm, "divers/")
        repFilm = os.path.normpath(repFilm)

        """
        try:
            if self.name in self.repKodiName:
                os.mkdir(self.repKodiName)
        except: pass
        repFilm = self.repKodiName + "divers/"
        """

        if clear == 1:
            try:
                shutil.rmtree(repFilm, ignore_errors=True)
            except: pass
        for i in range(15):
            try:
                if not os.path.isdir(repFilm):
                    os.mkdir(repFilm)
                break
            except: pass
            time.sleep(2)

        nb = len(liste)
        for i, movie in enumerate(liste):
            i += 1
            numId = movie[1]
            title = movie[0]
            #notice(title)
            titreStrm = self.makeNameRep(title)
            urlFilm = "*".join(movie[2].split(","))
            textStream = u"plugin://plugin.video.sendtokodiU2P/?action=play&lien={}".format(urlFilm)

            if progress:
                try:
                    if i % round(float(nb) / 100.0, 0) == 0:
                        nbStrms = int((i / float(nb)) * 100.0)
                        progress.update(nbStrms, 'Films %d/%d' %(i, nb))
                except: pass

            strm = "%s.strm" %titreStrm
            repStream = os.path.join(repFilm , titreStrm)
            repMovie = os.path.join(repStream, strm)
            repMovie = os.path.normpath(repMovie)
            repNFO = os.path.join(repStream, "%s.nfo" %titreStrm)
            repNFO = os.path.normpath(repNFO)
            try:
                os.mkdir(repStream)
            except Exception as e:
                #notice("erreur rep: %s" %(unicodedata.normalize('NFD', repStream).encode('ascii','ignore').decode("latin-1")))
                pass

            self.saveFile(repMovie, textStream)
            textNFO = u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <movie>
    <genre>Sport</genre>
    <title>{0}</title>
    </movie>""".format(titreStrm)
            self.saveFile(repNFO, textNFO)


    def loadFilm(self, films):
        for j, film in enumerate(films):
            try:
                if len(film) > 12:
                    tmp  = film.pop(3)
                    film[2] = film[2] + " : " + tmp
                groupes = ast.literal_eval(film[self.GROUPES])
                title = film[self.TITLE]
                if pyVersion == 2:
                    title = unicode(title, "utf8", "replace")
                for groupe in groupes:
                    if groupe in self.dictGroupeFilms.keys():
                        self.dictGroupeFilms[groupe].append(title)
                    else:
                        self.dictGroupeFilms[groupe] = [title]
                tabFormat = ast.literal_eval(film[self.RES])
                if film[self.TMDB] in self.dictFilmsPaste.keys():
                    self.dictFilmsPaste[film[self.TMDB]][2] = self.dictFilmsPaste[film[self.TMDB]][2] + "," + ",".join(["%s@%s#%s" %(self.numPaste, x, tabFormat[i]) for i, x in  enumerate(ast.literal_eval(film[self.URLS]))])
                else:
                    self.dictFilmsPaste[film[self.TMDB]] = [film[self.TITLE] + "-" + film[self.YEAR], film[self.TMDB], ",".join(["%s@%s#%s" %(self.numPaste, x, tabFormat[i]) for i, x in  enumerate(ast.literal_eval(film[self.URLS]))])]
            except:
                pass
                #notice("erreur: %s" %film)
        #notice("nb Film : %d" %len(self.dictFilmsPaste.keys()))

    def makeNameRep(self, title):
        title = unquote(title)#, encoding='latin-1', errors='replace')
        if pyVersion == 2:
            title = unicode(title, "utf8", "replace")
        title = unicodedata.normalize('NFD', title).encode('ascii','ignore').decode("latin-1")
        tab_remp = [r'''\\|/|:|\*|\?|"|<|>|\|| {2,}''', ' ']
        title = re.sub(tab_remp[0], tab_remp[1], title)
        title = title[:64].strip()
        return title

    def makeMovieNFO(self, liste, sendToKodi=1, clear=0, progress=None, nomRep=""):

        try:
            if self.name in self.repKodiName:
                os.mkdir(self.repKodiName)
        except: pass

        if nomRep:
            repFilm = os.path.join(self.repKodiName, nomRep + "/")
            try:
                os.mkdir(repFilm)
            except: pass
        else:
            repFilm = self.repKodiName

        repFilm = os.path.join(repFilm, "films/")
        repFilm = os.path.normpath(repFilm)
        #notice(repFilm)
        if clear == 1:
            try:
                shutil.rmtree(repFilm, ignore_errors=True)
            except: pass
        try:
            os.mkdir(repFilm)
        except Exception as e:
            pass
            #notice("erreur rep: %s" %(str(e)))
        nb = len(liste)
        for i, movie in enumerate(liste):
            i += 1
            numId = movie[1]
            title = movie[0]
            #notice(title)
            titreStrm = self.makeNameRep(title)
            urlFilm = "*".join(movie[2].split(","))
            textStream = u"plugin://plugin.video.sendtokodiU2P/?action=play&lien={}".format(urlFilm)

            if progress:
                try:
                    if i % round(float(nb) / 100.0, 0) == 0:
                        nbStrms = int((i / float(nb)) * 100.0)
                        progress.update(nbStrms, 'Films %d/%d' %(i, nb))
                except: pass

            strm = "%s.strm" %numId
            repStream = os.path.join(repFilm , "%s(%s)" %(titreStrm, numId))
            repMovie = os.path.join(repStream, strm)
            repMovie = os.path.normpath(repMovie)
            repNFO = os.path.join(repStream, "%s.nfo" %numId)
            repNFO = os.path.normpath(repNFO)
            try:
                os.mkdir(repStream)
            except Exception as e:
                #notice("erreur rep: %s" %(unicodedata.normalize('NFD', repStream).encode('ascii','ignore').decode("latin-1")))
                pass

            self.saveFile(repMovie, textStream)
            textNFO = u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<movie>
<tmdbid>{0}</tmdbid>
</movie>
http://www.themoviedb.org/movie/{0}""".format(numId)
            self.saveFile(repNFO, textNFO)

    def loadSerie(self, series):

        for j, serie in enumerate(series):
            try:
                if len(serie) > 12:
                    tmp  = serie.pop(3)
                    serie[2] = serie[2] + " : " + tmp

                groupes = ast.literal_eval(serie[self.GROUPES])
                title = serie[self.TITLE]
                if pyVersion == 2:
                    title = unicode(title, "utf8", "replace")
                for groupe in groupes:
                    if groupe in self.dictGroupeSeries.keys():
                        self.dictGroupeSeries[groupe].append(title)
                    else:
                        self.dictGroupeSeries[groupe] = [title]


                dictSaison = {}
                saison = ast.literal_eval(serie[self.URLS])
                reso = ast.literal_eval(serie[self.RES])
                for k, v in saison.items():
                    dictSaison["S%sE%s%s" %(serie[self.SAISON], "0" * (2 - len(str(k))), k)] = [self.numPaste + '@' + v + "#" + reso[0]]

                if (serie[self.TMDB] + serie[self.SAISON]) in self.dictSeriesPaste.keys():
                    #print("double", self.dictSeriesPaste[serie[self.TMDB]], "in", dictSaison)
                    for k, v in self.dictSeriesPaste[serie[self.TMDB] + serie[self.SAISON]][3].items():
                        try:
                            v += dictSaison[k]
                            self.dictSeriesPaste[serie[self.TMDB]][3][k] = v
                        except: pass
                else:
                    self.dictSeriesPaste[serie[self.TMDB] + serie[self.SAISON]] = [serie[self.TITLE] + "-" + serie[self.YEAR], serie[self.TMDB], "Saison %s" %serie[self.SAISON], dictSaison]
            except: pass
        for k, v in self.dictGroupeSeries.items():
            self.dictGroupeSeries[k] = list(set(v))

    def saveFile(self, fileIn, textOut):
        if os.path.isfile(fileIn):
                try:
                    with io.open(fileIn, "r", encoding="utf-8") as f:
                        textIn = f.read()
                except:
                    with io.open(fileIn, "r", encoding="latin-1") as f:
                        textIn = f.read()
        else:
            textIn = ""
        if textIn != textOut:
            with open(fileIn, "w") as f:
                f.write(textOut)

    def makeSerieNFO(self, liste, sendToKodi=1, clear=0, progress=None, nomRep=""):
        try:
            if self.name in self.repKodiName:
                os.mkdir(self.repKodiName)
        except: pass

        if nomRep:
            repSerie = os.path.join(self.repKodiName, nomRep + "/")
            try:
                os.mkdir(repSerie)
            except: pass
        else:
            repSerie = self.repKodiName

        repSerie = os.path.join(repSerie, "series/")
        repSerie = os.path.normpath(repSerie)

        """
        try:
            if self.name in self.repKodiName:
                os.mkdir(self.repKodiName)
        except: pass

        repSerie = self.repKodiName + "series/"
        """
        if clear == 1:
            try:
                shutil.rmtree(repSerie, ignore_errors=True)
            except: pass
        for i in range(15):
            try:
                if not os.path.isdir(repSerie):
                    os.mkdir(repSerie)
                break
            except: pass
            time.sleep(2)
        dictSerie  = {}
        for i, movie in enumerate(liste):
            if movie[1] not in dictSerie.keys():
                dictSerie[movie[1]] = [(movie[2], ast.literal_eval(str(movie[3])), movie[0])]
            else:
                dictSerie[movie[1]].append((movie[2], ast.literal_eval(str(movie[3])), movie[0]))
        i = 0

        nb = len(dictSerie.keys())

        for serie in sorted(dictSerie.keys()):
            i += 1
            numId, value, titreStrm = serie, dictSerie[serie] , dictSerie[serie][0][2]
            titreStrm = self.makeNameRep(titreStrm)
            repStream = os.path.join(repSerie , "%s(%s)" %(titreStrm, numId))
            if progress:
                if i % 10 == 0:
                    nbStrms = int((i / float(nb)) * 100.0)
                    progress.update(nbStrms, 'Series %d/%d' %(i, nb))

            try:
                os.mkdir(repStream)
            except Exception as e:
                pass
            repNFO = os.path.join(repStream, "tvshow.nfo")
            repNFO = os.path.normpath(repNFO)
            textNFO = u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<tvshow>
<tmdbid>{0}</tmdbid>
</tvshow>
https://www.themoviedb.org/tv/{0}&islocal=True""".format(numId)
            self.saveFile(repNFO, textNFO)
            for saison in value:
                repSaison = os.path.join(repStream, "{}".format(saison[0]))
                try:
                    os.mkdir(repSaison)
                except Exception as e:
                    pass
                for k, v in saison[1].items():
                    #print(k, v)
                    if sendToKodi == 1:
                        textStream = u"plugin://plugin.video.sendtokodiU2P/?action=play&lien={}".format("*".join(v))
                    else:
                        title = numId
                        textStream = u"plugin://plugin.video.vstream/?site=cHosterGui&function=play&title=%s&sHosterIdentifier=uptobox&sTitle=%s&siteUrl=%s&sFav=play&sMediaUrl=%s&sCat=5&sId=cHosterGui&sFileName=%s&sTitleWatched=%s" \
                        %(title, title, urlFilm, urlFilm, title, title)
                    repEpisode = os.path.join(repSaison, "{}.strm".format(k))
                    repEpisode = os.path.normpath(repEpisode)
                    self.saveFile(repEpisode, textStream)

    def loadAnime(self, series):
        dictAnimeFull = {}
        for j, serie in enumerate(series):
            try:
                if len(serie) > 12:
                    tmp  = serie.pop(3)
                    serie[2] = serie[2] + " : " + tmp

                groupes = ast.literal_eval(serie[self.GROUPES])
                title = serie[self.TITLE]
                if pyVersion == 2:
                    title = unicode(title, "utf8", "replace")
                for groupe in groupes:
                    if groupe in self.dictGroupeAnimes.keys():
                        self.dictGroupeAnimes[groupe].append(title)
                    else:
                        self.dictGroupeAnimes[groupe] = [title]
                epSaison = ast.literal_eval(serie[self.URLS])
                nomSerie = serie[self.TITLE] + "-" + serie[self.YEAR] +  "#" + serie[self.TMDB]
                epSaison = {int(x[1:]):["%s@%s#" %(self.numPaste ,y)] for x, y in epSaison.items()}
                if nomSerie not in dictAnimeFull.keys():
                    dictAnimeFull[nomSerie] = epSaison
                else:
                    for k, v in epSaison.items():
                        #print(nomSerie, k, v)
                        if k in dictAnimeFull[nomSerie].keys():
                            dictAnimeFull[nomSerie][k] += v
                        else:
                            dictAnimeFull[nomSerie][k] = v
            except Exception as e:
                pass
                #notice(str(e))

        #self.dictBa = {}
        #self.dictAnimesPaste = {}
        for k, v in dictAnimeFull.items():
            ba = ""
            try:
                infoserie = self.serieNumId(k.split("#")[1])
                trailers = infoserie["videos"]["results"]


                self.dictBa[k] = ""
                if trailers:
                    for trailer in trailers:
                        if ("VF" in trailer["name"] or trailer["iso_639_1"] == 'fr' or trailer["iso_3166_1"] == 'FR') and trailer['type'] == 'Trailer':
                            ba = "plugin://plugin.video.youtube/?action=play_video&videoid=%s" %trailer["key"]
                            break
                        elif trailer['type'] == 'Trailer':
                            ba = "plugin://plugin.video.youtube/?action=play_video&videoid=%s" %trailer["key"]
                        else:
                            ba = "plugin://plugin.video.youtube/?action=play_video&videoid=%s" %trailer["key"]
                    self.dictBa[k] = ba

                numEpisode = 1
                dictSaison = {}
                for saison in infoserie['seasons']:
                    #print(saison["season_number"], saison["episode_count"])
                    if saison["season_number"] > 0:
                        nbEpisodes = saison["episode_count"]
                        for i in range(nbEpisodes):
                            try:
                                dictSaison[i + numEpisode] = 'S%dE' %saison["season_number"]
                            except: pass
                        numEpisode += nbEpisodes
                dictAnimeCorrige = {"%s%d" %(dictSaison[k],k) :v  for k, v in v.items() if k in dictSaison.keys()}

                self.dictAnimesPaste[k] = [k, k, "Episodes", dictAnimeCorrige]
            except: pass

        for k, v in self.dictGroupeAnimes.items():
            self.dictGroupeAnimes[k] = list(set(v))


    def serieNumId(self, numId, key="96139384ce46fd4ffac13e1ad770db7a"):
        """infos series suivant numID + trailers"""
        url1 = "https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=videos&language=fr".format(numId, key)
        req = requests.get(url1)
        dict_serie= req.json()
        return dict_serie


    def makeAnimeNFO(self, liste, sendToKodi=1, clear=0, progress=None, nomRep=""):
        try:
            if self.name in self.repKodiName:
                os.mkdir(self.repKodiName)
        except: pass

        if nomRep:
            repSerie = os.path.join(self.repKodiName, nomRep + "/")
            try:
                os.mkdir(repSerie)
            except: pass
        else:
            repSerie = self.repKodiName

        repSerie = os.path.join(repSerie, "anime/")
        repSerie = os.path.normpath(repSerie)

        """
        try:
            if self.name in self.repKodiName:
                os.mkdir(self.repKodiName)
        except: pass

        repSerie = self.repKodiName + "anime/"
        """

        if clear == 1:
            try:
                shutil.rmtree(repSerie, ignore_errors=True)
            except: pass

        for i in range(15):
            try:
                if not os.path.isdir(repSerie):
                    os.mkdir(repSerie)
                break
            except: pass
            time.sleep(2)

        dictSerie  = {}
        for i, movie in enumerate(liste):
            if movie[1] not in dictSerie.keys():
                dictSerie[movie[0]] = [(movie[2], ast.literal_eval(str(movie[3])), movie[0])]
            else:
                dictSerie[movie[0]].append((movie[2], ast.literal_eval(str(movie[3])), movie[0]))
        i = 0

        nb = len(dictSerie.keys())

        for serie in sorted(dictSerie.keys()):
            i += 1
            nb = len(dictSerie.keys())
            if progress:
                if i % 10 == 0:
                    nbStrms = int((i / float(nb)) * 100.0)
                    progress.update(nbStrms, 'Animes %d/%d' %(i, nb))


            numId, value, titreStrm = serie, dictSerie[serie] , dictSerie[serie][0][2]
            titreStrm = self.makeNameRep(titreStrm)
            repStream = os.path.join(repSerie , "%s" %(titreStrm))

            #if clear == 1 or not os.path.exists(repStream):
            try:
                os.mkdir(repStream)
            except Exception as e:
                pass
            #repNFO = repStream + "tvshow.nfo"
            repNFO = os.path.join(repStream, "tvshow.nfo")
            repNFO = os.path.normpath(repNFO)

            textNFO = """
<tvshow>
<trailer>%s</trailer>
<genre>Anime</genre>
</tvshow>\n""" %self.dictBa[serie]
            textNFO += u"https://www.themoviedb.org/tv/{}&islocal=True".format(numId.split("#")[1])
            self.saveFile(repNFO, textNFO)
            for saison in value:
                repSaison = os.path.join(repStream, "{}".format(saison[0]))
                #try:
                #    os.mkdir(repSaison)
                #except Exception as e:
                #    pass
                for k, v in saison[1].items():
                    #repEpisode = os.path.join(repSaison, "{}.strm".format(k))
                    repEpisode = os.path.join(repStream, "{}.strm".format(k))
                    repEpisode = os.path.normpath(repEpisode)
                    textStream = u"plugin://plugin.video.sendtokodiU2P/?action=play&lien={}".format("*".join(v))
                    self.saveFile(repEpisode, textStream)

    def delTag(self, dataBaseKodi):
        cnx = sqlite3.connect(dataBaseKodi)
        cur = cnx.cursor()
        cur.execute("DELETE FROM tag")
        cur.execute("DELETE FROM tag_link")
        cnx.commit()
        cur.close()
        cnx.close()


    def UpdateGroupe(self, groupes, dataBaseKodi, mediaType="movie", progress=None, gr=""):
        cnx = sqlite3.connect(dataBaseKodi)
        cur = cnx.cursor()
        sql = "SELECT MAX(tag_id) FROM tag"
        cur.execute(sql)
        for row in cur:
            try:
                posTag = int(row[0]) + 1
            except:
                posTag = 1
        i = 1
        nb = len(groupes)
        for k, v in groupes.items():
            if progress:
                nbGroupe = int((i / float(nb)) * 100.0)
                nbGroupe = int(str(nbGroupe).split(".")[0])
                progress.update(nbGroupe, 'Pbi2kodi', message=gr)
                i += 1
            try:
                sql = "INSERT  INTO tag (tag_id, name) VALUES(?, ?)"
                cur.execute(sql, (posTag, k, ))
                for media in v:
                    if mediaType == "movie":
                        sql = "SELECT idMovie FROM movie WHERE c00=?"
                    else:
                        sql = "SELECT idShow FROM tvshow WHERE c00=?"
                    cur.execute(sql, (media, ))
                    mediaId = ""
                    for row in cur:
                        mediaId = row[0]
                    if mediaId:
                        #print("insert tag_link", posTag, mediaId, mediaType)
                        try:
                            sql = "INSERT  INTO tag_link (tag_id, media_id, media_type) VALUES(?, ?, ?)"
                            cur.execute(sql, (posTag, mediaId, mediaType, ))
                        except:
                            pass
            except: pass
            cnx.commit()
            posTag += 1
        cur.close()
        cnx.close()