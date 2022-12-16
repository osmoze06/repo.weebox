# -*- coding: utf-8 -*-
import os
import sqlite3
import re
import requests
import sys
try:
  import xbmcaddon
  import xbmcgui
except: pass
from urllib.parse import quote, unquote
import ast
from util import notice
import ast
import threading
import time
import datetime

keywords = {'80s action parody':269633,
'action adventure':253675,
'action comedy':247799,
'action hero':219404,
'action heroine':208314,
'action thriller':255973,
'adventure':258331,
'adventure comedy':269709,
'alien attack':192962,
'alien contact':160515,
'alien creature':230857,
'alien infection':15250,
'alien invasion':14909,
'alien life-form':4862,
'alien monster':183787,
'alien organism':245733,
'alien parasites':220392,
'alternative timeline':212049,
'alternative universe':208507,
'animal human friendship':258197,
'animal protagonist':269765,
'animals':265712,
'arachnids':262430,
'back in time':186717,
'based on television series':269767,
'based on tv series':269769,
'bio attack':238499,
'bio terrorism':225136,
'biological weapon':1865,
'blockbuster':268433,
'bodyguard':3088,
'bodys':242952,
'bomb attack':206544,
'bugs':208736,
'cartel':206594,
'catastrophe':188351,
'chaos':4630,
'climate breakdown':254028,
'clone':402,
'coincidence':10901,
'cops':258289,
'corrupt system':187293,
'corruption':417,
'cosmonaut':198136,
"coup d'etat":6285,
'crime':268275,
'crime serial':245632,
'crime solving':223067,
'criminal organization':206928,
'criminal profiler':187329,
'cult comedy':9808,
'cult horror':156324,
'cyber terrorism':218122,
'cyberspace':15256,
'damned':242521,
'deadly creature':206835,
'deadly disease':224394,
'deadly game':220572,
'death game':239068,
'death of superhero':174016,
'demon':15001,
'demon hunter':186425,
'demonic':241827,
'demonic possession':161261,
'demonic spirit':243003,
'desaster':268768,
'detectives':258417,
'disaster':10617,
'disaster movie':189411,
'dracula':261274,
'dragon':12554,
'drug':251961,
'drug cartel':10175,
'drug gang':208236,
'drug traffic':2149,
'drugs':14964,
'dual identity':851,
'dual life':196521,
'dual personality':227947,
'edited from video game':268681,
'enigmatic':193294,
'enigme':240420,
'epidemia':214716,
'epidemic':17995,
'epidemiologist':259267,
'escape plan':220650,
'escape room':240252,
'espionage':11134,
'espionnage':264172,
'espions':268893,
'exorcism':2626,
'exorcisme':263575,
'exorcist':159940,
'fake identity':167808,
'fantastic world':33633,
'flu':6681,
'fugitive':10718,
'galactic war':163295,
'gangster':3149,
'ghost':162846,
'ghosts':256394,
'ghouls':219990,
'great white shark':15098,
'guerre':269000,
'hack':214921,
'hacker':2157,
'hacking':12361,
'haunted':230191,
'haunting':10224,
'historic':202043,
'historique':269038,
'horror':8087,
'horror anthology':250593,
'horror comedy':224636,
'horror host':208012,
'horror icon':246608,
'horror mystery':231172,
'horror parody':249969,
'human versus alien':269630,
'human vs alien':186497,
'human vs computer':221045,
'human vs nature':2763,
'humor':265309,
'humour':268372,
'jeux vidAo':265674,
'killer':15127,
'knight':10466,
'kung fu':780,
'kung fu master':185466,
'lost in space':197015,
'lost in time':189144,
'lost island':198364,
'loup garou':255582,
'lycanthrope':228001,
'mafia':10391,
'mafia boss':6220,
'magic':2343,
'magical creature':195269,
'magician':236458,
'maigret':248660,
'maleficent':269718,
'martial arts':779,
'martian':10539,
'meteor':5404,
'meteorite':10221,
'middle age':176793,
'mindfuck':267591,
'monster':1299,
'monster movie':210614,
'motor racing':268011,
'multiple personality':169411,
'multiverse':221309,
'mummy':2904,
'murder':9826,
'mutant':1852,
'mutant creature':231345,
'mutants':234268,
'mutation':2766,
'mysterious':197582,
'mystery':10092,
'mystery film':268724,
'ninja':10278,
'ninjas':250060,
'other dimension':223914,
'pademic':268409,
'paranormal':9853,
'parasite':157634,
'parasites':242619,
'parodies':257244,
'parody':9755,
'pest':2867,
'phantom':3284,
'phantoms':222232,
'piranha':158045,
'pirate':12988,
'pirate gang':4418,
'pirate ship':185200,
'pirates':263457,
'police comedy':269754,
'possession':9712,
'post-apocalyptic future':4458,
'post-cataclysmic':250927,
'prehistoric':10506,
'prehistory':201947,
'prison escape':9777,
'professional thief':191604,
'prophecy':530,
'quest':207372,
'revenant':221910,
'revenge':9748,
'roadtrip':240484,
'robot':14544,
'robots':266658,
'runescape':244095,
'science fiction':261850,
'serial killer':10714,
'sexy comedy':263590,
'shark':15097,
'shark attack':2988,
'sinister':269049,
'sorcerer':10821,
'space':9882,
'space adventure':195114,
'space travel':3801,
'space war':3386,
'special agent':206958,
'spider':3986,
'sport':269260,
'strange':215191,
'street racing':266725,
'superhero':9715,
'superhero comedy':266005,
'superheroes':247784,
'superstition':6156,
'supervillain':194404,
'survivor':5385,
'temporal travel':190344,
'thief':9727,
'thriller':9950,
'time machine':5455,
'time paradox':208757,
'time travel':4379,
'time traveler':176056,
'transylvania':272,
'treasure chest':222856,
'treasure hunt':6956,
'treasure hunter':215470,
'treasure hunting':266154,
'treasure map':11088,
'twilight':2640,
'ufo':9738,
'vampir':264793,
'vampire':3133,
'vampire hunter':9259,
'vampire slayer':166720,
'victim revenge':268852,
'virus':188957,
'volcano':3347,
'voodoo':3392,
'western':10511,
'witch':616,
'witch hunter':177900,
'wolf':1994,
'wolves':232116,
'world war':258077,
'yakuza':1794,
'zombie':12377,
'zombie apocalypse':186565,
'zombie horde':258613,
'zombification':167085,
}

class Media:
    def __init__(self, typeMedia="film", *argvs):
        self.typeMedia = typeMedia
        size = self.getTaille()
        self.poster = "http://image.tmdb.org/t/p/" + size[0]
        self.backdrop = "http://image.tmdb.org/t/p/" + size[1]
        self.clearlogo = ""
        self.clearart = ""

        if self.typeMedia == "movie":
          #title, overview, year, poster, numId, genre, popu
          self.year = argvs[2]
          try:
            self.duration = int(argvs[9])
          except:
            self.duration = 0
          self.popu = argvs[6]
          if argvs[8]:
            self.backdrop += argvs[8]
          if argvs[3]:
            self.poster += argvs[3]
          self.genre = argvs[5]
          self.title= argvs[0]
          self.overview = argvs[1]
          self.numId = argvs[4]
          self.link = argvs[7]

        elif self.typeMedia == "fankai":
          #title, overview, year, poster, numId, genre, popu
          self.year = argvs[2]
          try:
            self.duration = int(argvs[9])
          except:
            self.duration = 0
          self.popu = argvs[6]
          self.backdrop = argvs[8]
          self.poster = argvs[3]
          self.genre = argvs[5]
          self.title= argvs[0]
          self.overview = argvs[1]
          self.numId = argvs[4]
          self.link = argvs[7]

        elif self.typeMedia == "vod":
          ##"id", "name", "description", "time", "tmdb_id", 'screenshot_uri', "age", 'year', "added", actors", "director", path", 'rating_kinopoisk'
          self.year = argvs[7]
          if argvs[3]:
            self.duration = argvs[3]
          else:
            self.duration = "0"
          self.popu = argvs[12]
          self.backdrop = ""
          self.poster = argvs[5]
          self.genre = argvs[13]
          self.title= argvs[1]
          self.overview = argvs[2]
          self.numId = argvs[4]
          self.age = argvs[6]
          self.added = argvs[8]
          self.actors = argvs[9]
          self.director = argvs[10]
          self.id = argvs[0]
          self.link = argvs[14]
          self.episodes = argvs[15]

        elif self.typeMedia == "menu":
          #[Title, overview, year, genre, backdrop, popu]
          self.year = argvs[2]
          self.duration = ""
          self.popu = argvs[5]
          if argvs[4]:
            self.backdrop += argvs[4]
          if argvs[7]:
            self.poster += argvs[7]
          self.genre = argvs[3]
          self.title= argvs[0]
          self.overview = argvs[1]
          self.numId = argvs[6]
          self.link = ""


        elif self.typeMedia == "tvshow":
          self.year = argvs[2]
          try:
            self.duration = int(argvs[8])
          except:
            self.duration = 0
          self.popu = argvs[6]
          if argvs[7]:
            self.backdrop += argvs[7]
          if argvs[3]:
            self.poster += argvs[3]
          self.genre = argvs[5]
          self.title= argvs[0]
          self.overview = argvs[1]
          self.numId = argvs[4]
          self.link = ""

        elif self.typeMedia == "saga":
          #numId, title, overview, poster
          self.year = ""
          self.duration = ""
          self.popu = ""
          self.backdrop += ""
          if argvs[3]:
            self.poster += argvs[3]
          self.genre = ""
          self.title= argvs[1]
          self.overview = argvs[2]
          self.numId = argvs[0]

        elif self.typeMedia == "audiobook":
          #auteur, titre, numId, description, poster, link
          self.year = ""
          self.duration = ""
          self.popu = ""
          self.backdrop += ""
          if argvs[4]:
            self.poster = argvs[4]
          self.genre = ""
          self.title= argvs[0] + ' - ' + argvs[1]
          self.overview = argvs[3]
          self.numId = argvs[2]
          self.link = argvs[5]

        elif self.typeMedia == "episode":
          #[35339, 'Saison 01', 'S01E01', 'C9PxOAB66@nRlEQs5IiKHK#SD*C9PxOAB66@xClOGtaqotVH#1080P*xMZPoCbT0@8VJMS21ZpReE#*zi6kvPg63@FM63Jev8MtqA#1080P', 'Jack Sylvane', overview", '2012-01-16', '/A97bfgXNHR97WUTn52B4e8zsmn2.jpg', 7.6, 1, 1]
          self.year = argvs[6]
          self.duration = ""
          self.popu = argvs[8]
          if argvs[7]:
            self.backdrop += argvs[7]
          self.poster += ""
          self.genre = ""
          self.title= argvs[4]
          self.overview = argvs[5]
          self.numId = argvs[0]
          self.link = argvs[3]
          self.episode = argvs[-2]
          self.saison = argvs[-3]
          self.vu = argvs[-1]

        elif self.typeMedia == "cast":
          #('Artemis Pebdani', 'Additional Voices (voice)', '/ctwVQYbcOuTIQJ866fi3AhzqKBM.jpg', numId)
          self.year = ""
          self.duration = ""
          self.popu = ""
          self.backdrop += ""
          if argvs[2]:
            self.poster += argvs[2]
          self.genre = ""
          self.title= argvs[0]
          self.overview = argvs[1]
          self.numId = argvs[3]
          self.link = ""

        elif self.typeMedia == "lien":
          #m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, m.backdrop, m.runtime, m.id
          self.year = argvs[5]
          self.duration = argvs[11]
          self.popu = argvs[9]
          if argvs[10]:
            self.backdrop += argvs[10]
          if argvs[6]:
            self.poster += argvs[6]
          self.genre = argvs[8]
          self.title= argvs[3]
          self.overview = "\n\n\nRelease: %s\n---------------------\n%s" %(argvs[2].replace('.', ' '), argvs[4])
          self.numId = argvs[7]
          self.link = argvs[1]

    def getTaille(self):
      dictSize = {"Basse": ("w185", "w780"),
                "Moyenne": ("w342", "w1280"),
                "Haute": ("w500", "original")}
      addon = xbmcaddon.Addon("plugin.video.sendtokodiU2P")
      v = addon.getSetting("images_sizes")
      return dictSize[v]

class TMDB:
    def __init__(self, key):
      self.key = key
      self.urlBase = "https://api.themoviedb.org/3/"
      self.lang = "fr"
      self.tabMedia = []
      self.tabMediaFinal = []
      self.tabNumIdDiff = []

    def getGenre(self, typM="movie"):
      """movie or tv"""
      url1 = self.urlBase + "genre/{}/list?api_key={}&language={}".format(typM, self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      genres = [x["name"] for x in dictInfos["genres"]]
      return genres

    def dateRealeaseMovie(self, numId):
      url1 = self.urlBase + "movie/{}/release_dates?api_key={}&language={}".format(numId, self.key, self.lang)
      url1 = self.urlBase + "movie/upcoming?api_key={}&append_to_response=release_dates&language={}".format(self.key, self.lang)
      print(url1)

    def getNumIdBA(self, numId, typM="movie"):
      """infos suivant numID + trailers movie ou tv"""
      t = {"movie": "movie", "tvshow": "tv"}
      url1 = self.urlBase + "{}/{}?api_key={}&append_to_response=videos&language=fr".format(t[typM], numId, self.key)
      req = requests.request("GET", url1, data=None)
      dictInfos = req.json()
      #lectBa = "plugin://plugin.video.youtube/?action=play_video&videoid={}"
      return [(bas["name"], bas["size"], bas["key"]) for bas in dictInfos['videos']['results']]

    def suggReco(self, numId, typM="movie", rech="recommendations"):
      """recommendations ou similar"""
      tabId = []
      for i in range(1, 3, 1):
        url1 = self.urlBase + "{}/{}/{}?api_key={}&language={}&page={}".format(typM, numId, rech, self.key, self.lang, i)
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()
        tabId += [result['id'] for result in dictInfos["results"]]
      return tabId

    def movieNumId(self, filecode, pos, numId):
      """infos film via numID"""
      url1 = self.urlBase + "movie/{}?api_key={}&language={}".format(numId, self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      dictMovies = {u'total_results': 1, u'total_pages': 1, u'page': 1, u'results': [{u'poster_path': dictInfos.get("poster_path", ""), u'title': dictInfos.get("title", u"Inconnu"), u'overview': dictInfos.get("overview", ""),
            u'release_date': dictInfos.get("release_date", 0), u'popularity': dictInfos.get("vote_average", 0.0), u'original_title': dictInfos.get("original_title", ""), u'backdrop_path': dictInfos.get("backdrop_path", ""),
            u'vote_count': dictInfos.get("vote_count", 0), u'video': False, u'adult': False, u'vote_average': dictInfos.get("vote_average", 0.0), u'genre_ids': [], u'id': dictInfos.get("id", 0),
            u'original_language': dictInfos.get("original_language", "")}]}
      try:
        dictMovies["results"][0]["genre_ids"] = ", ".join([z for y in dictInfos["genres"] for x, z in y.items() if x == "name"])
      except:
        dictMovies["results"][0]["genre_ids"] = ""
      if not dictMovies["results"][0]["id"]:
        dictMovies["results"][0]["id"] = numId
      self.tabMedia.append((pos, filecode, dictMovies))

    def getSaga(self, numId):
      url1 = self.urlBase + "collection/{}?api_key={}&language={}".format(numId, self.key, self.lang)
      req = requests.get(url1)
      try:
        return [(x["release_date"], x["id"]) for x in req.json()['parts']]
      except:
        return []

    def getListeFilm(self, nom):
        self.tabIdListe = []
        dateJ = datetime.date.today()
        dictWids = {'Tendances du jour': "trending/movie/day?api_key={}".format(self.key),
              'Tendances de la semaine': "trending/movie/week?api_key={}".format(self.key),
              'Nouveautés': "discover/movie?release_date.lte={}&vote_count.gte=5&without_genres=99|10402&sort_by=release_date.desc&with_release_type=4|5|6&api_key={}".format(dateJ, self.key),
              'Les plus populaires': "discover/movie?sort_by=vote_count.desc&api_key={}".format(self.key),
              'Films français récents': "discover/movie?with_original_language=fr&vote_count.gte=1&without_genres=99|10402&release_date.lte={}&sort_by=primary_release_date.desc&with_release_type=4|5|6&api_key={}".format(dateJ, self.key),
              'Films français populaires': "discover/movie?with_original_language=fr&sort_by=popularity.desc&without_genres=99&with_release_type=4|5|6&api_key={}".format(self.key),
              "Films d'animation récents": "discover/movie?with_genres=16,10751&primary_release_date.lte={}&vote_count.gte=5&sort_by=primary_release_date.desc&with_release_type=4|5|6&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              "Films d'animation populaires": "discover/movie?with_genres=16,10751&primary_release_date.lte={}&sort_by=popularity.desc&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              'Films famille récents': "discover/movie?with_genres=10751&without_genres=16&primary_release_date.lte={}&vote_count.gte=5&sort_by=primary_release_date.desc&with_release_type=4|5|6&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              'Films famille populaires': "discover/movie?with_genres=10751&without_genres=16&primary_release_date.lte={}&sort_by=popularity.desc&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              'Animes populaires': "discover/movie?with_genres=16&with_original_language=ja&vote_count.gte=500&sort_by=popularity.desc&api_key={}".format(self.key),
              'Animes récents': "discover/movie?with_genres=16&with_original_language=ja&vote_count.gte=10&release_date.lte={}&sort_by=primary_release_date.desc&api_key={}".format(dateJ, self.key)
              }
        url1 =self.urlBase + dictWids[nom]
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()
        self.tabIdListe = [result['id'] for result in dictInfos["results"]]
        nbPages = dictInfos["total_pages"]
        if nbPages > 4:
          nbPages = 4
        for i in range(2, nbPages, 1):
            url1 += "&page=%d" %i
            threading.Thread(name="ListeWid", target=self.getIdL, args=(url1,)).start()
            time.sleep(0.03)
        self.testThread("ListeWid")
        return self.tabIdListe

    def getListeSerie(self, nom):
        self.tabIdListe = []
        dateJ = datetime.date.today()
        dictWids = {'Tendances du jour': "trending/tv/day?api_key={}".format(self.key),
              'Tendances de la semaine': "trending/tv/week?api_key={}".format(self.key),
              'Nouveautés': "discover/tv?first_air_date.lte={}&vote_count.gte=5&sort_by=first_air_date.desc&without_genres=16&api_key={}".format(dateJ, self.key),
              'Les plus populaires': "discover/tv?sort_by=vote_count.desc&api_key={}".format(self.key),
              'Séries populaires': "discover/tv?with_genres=10762&without_genres=16&first_air_date.lte={}&vote_count.gte=5&sort_by=popularity.desc&with_release_type=4|5|6&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              'Séries récentes': "discover/tv?with_genres=10762&without_genres=16&first_air_date.lte={}&vote_count.gte=5&sort_by=first_air_date.desc&with_release_type=4|5|6&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              'Animes populaires': "discover/tv?with_genres=16&with_original_language=ja&vote_count.gte=500&sort_by=popularity.desc&api_key={}".format(self.key),
              'Animes récents': "discover/tv?with_genres=16&with_original_language=ja&vote_count.gte=10&release_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(dateJ, self.key),
              "Séries d'animation récentes": "discover/tv?with_genres=16,10762&first_air_date.lte={}&vote_count.gte=5&sort_by=first_air_date.desc&with_release_type=4|5|6&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              "Séries d'animation populaires": "discover/tv?with_genres=16,10762&first_air_date.lte={}&vote_count.gte=5&sort_by=popularity.desc&with_release_type=4|5|6&with_original_language=fr|en&api_key={}".format(dateJ, self.key),
              'Netflix : Populaires': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=popularity.desc&api_key={}".format(213, dateJ, self.key),
              'Netflix : Nouveautés': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(213, dateJ, self.key),
              'Prime Video : Populaires': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=popularity.desc&api_key={}".format(1024, dateJ, self.key),
              'Prime Video : Nouveautés': "discover/tv?with_networks={}&with_watch_providers=119&watch_region=FR&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(1024, dateJ, self.key),
              'Disney+ : Populaires': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=popularity.desc&api_key={}".format(2739, dateJ, self.key),
              'Disney+ : Nouveautés': "discover/tv?with_networks={}&with_watch_providers=337&watch_region=US&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(2739, dateJ, self.key),
              'Apple TV+ : Populaires': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=popularity.desc&api_key={}".format(2552, dateJ, self.key),
              'Apple TV+ : Nouveautés': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(2552, dateJ, self.key),
              'HBO Max : Populaires': "discover/tv?with_networks=49|3186&first_air_date.lte={}&sort_by=popularity.desc&api_key={}".format(dateJ, self.key),
              'HBO Max : Nouveautés': "discover/tv?with_networks=49|3186&with_watch_providers=8|119|9|337|2|381|56|345|61|234|194|58|564|685&watch_region=FR&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(dateJ, self.key),
              'CANAL+ : Populaires': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=popularity.desc&api_key={}".format(285, dateJ, self.key),
              'CANAL+ : Nouveautés': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(285, dateJ, self.key),
              'SALTO : Populaires': "discover/tv?with_networks=290|361|249|511|255|2984|712&with_watch_providers=564&watch_region=FR&first_air_date.lte={}&sort_by=popularity.descc&api_key={}".format(dateJ, self.key),
              'SALTO : Nouveautés': "discover/tv?with_networks=290|361|249|511|255|2984|712&with_watch_providers=564&watch_region=FR&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(dateJ, self.key),
              'ARTE : Populaires': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=popularity.desc&api_key={}".format(1628, dateJ, self.key),
              'ARTE : Nouveautés': "discover/tv?with_networks={}&first_air_date.lte={}&sort_by=first_air_date.desc&api_key={}".format(1628, dateJ, self.key),
              }

        url1 = self.urlBase + dictWids[nom]
        req = requests.request("GET", url1, data=None)
        dictInfos = req.json()
        self.tabIdListe = [result['id'] for result in dictInfos["results"]]
        nbPages = dictInfos["total_pages"]
        if nbPages > 4:
          nbPages = 4
        for i in range(2, nbPages, 1):
            url1 += "&page=%d" %i
            threading.Thread(name="ListeWid", target=self.getIdL, args=(url1,)).start()
            time.sleep(0.03)
        self.testThread("ListeWid")
        return self.tabIdListe

    def getIdL(self, url1):
      req = requests.request("GET", url1, data=None)
      dictInfos = req.json()
      self.tabIdListe += [result['id'] for result in dictInfos["results"]]


    def castFilm(self, numId):
      """infos realistaeur acteurs via numID"""
      dictCasts = {"crew": [], "cast": []}
      url1 = self.urlBase + "movie/{}/casts?api_key={}&language={}".format(numId, self.key, self.lang)
      req = requests.get(url1)
      dict_films_acteurs = req.json()

      #nom realisateur
      try:
          for d in dict_films_acteurs['crew']:
              #u'department': u'Directing', u'job': u'Director'
              if d['department']=='Directing' and d['job']=='Director':
                  dictCasts["crew"].append((d['name'], "Réalisateur", d["profile_path"], d["id"]))

      except: pass
      # acteurs
      try:
          acteurs = dict_films_acteurs['cast']
          tab_acteur = []
          for a in acteurs:
              tab_acteur.append((a['name'], a["character"], a["profile_path"], a["id"]))
          dictCasts["cast"] = tab_acteur
      except: pass
      return dictCasts["crew"] + dictCasts["cast"]

    def castSerie(self, numId):
        """infos realistaeur acteurs via numID"""
        dictCasts = {"crew": "", "cast": []}
        url = self.urlBase + "tv/{}/credits?api_key={}&language={}".format(numId, self.key, self.lang)
        req = requests.get(url)
        print(url)
        dict_films_acteurs = req.json()

        # acteurs
        try:
            acteurs = dict_films_acteurs['cast']
            tab_acteur = []
            for a in acteurs:
                tab_acteur.append((a['name'], a["character"], a["profile_path"], a["id"]))
            dictCasts["cast"] = tab_acteur
        except: pass
        return dictCasts["cast"]

    def person(self, numId, typM="movie"):
      if typM == "movie":
        url1 = self.urlBase + "person/{}/movie_credits?api_key={}&language={}".format(numId, self.key, self.lang)
      else:
        url1 = self.urlBase + "person/{}/tv_credits?api_key={}&language={}".format(numId, self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      tabFilm = [x["id"] for x in dictInfos["cast"]]
      tabFilm += [x["id"] for x in dictInfos["crew"]]
      return tabFilm

    def searchPerson(self, name):
      url1 = self.urlBase + "search/person?query={}&api_key={}&page=1&language={}".format(quote(name), self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      tab = [(x["name"], x["name"], x["profile_path"], x["id"]) for x in dictInfos["results"]]
      return tab

    def saison(self, numId, saison):
      url1 = self.urlBase + "tv/{}/season/{}?api_key={}&language={}".format(numId, saison, self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      tabEpisodes = []
      notice(dictInfos)
      try:
        for i, episode in enumerate(dictInfos["episodes"]):
          name = episode.get("name", "")
          overview = episode.get("overview", "")
          if not overview:
            overview = "Pas de Synopsis...."
          dateRelease = episode.get("air_date", "")
          backdrop = episode.get("still_path", "")
          popu = episode.get("vote_average", 0.0)
          numSaison = episode.get("season_number", int(saison))
          numEpisode = episode.get("episode_number", 1 + i)
          tabEpisodes.append([name, overview, dateRelease, backdrop, popu, numSaison, numEpisode])
      except: pass
      return tabEpisodes

    def verifSynop(self, tx):
      if not tx:
        tx = "Pas de Synopsis...."
      return tx

    def listKeywords(self, numId, typM="movie"):
      url1 = self.urlBase + "discover/{}?api_key={}&with_keywords={}&include_adult=true&page=1".format(typM, self.key, numId, self.lang)
      req = requests.get(url1)
      dict_infos = req.json()
      pages = dict_infos['total_pages']
      listId = [x["id"] for x in dict_infos["results"]]
      for i in range(2, pages, 1):
        url1 = self.urlBase + "discover/{}?api_key={}&with_keywords={}&include_adult=true&page={}".format(typM, self.key, numId, i)
        req = requests.get(url1)
        dict_infos = req.json()
        listId += [x["id"] for x in dict_infos["results"]]
        if i > 24:
          break
      return listId

    def getList(self, numId):
      url1 = self.urlBase + "list/{}?api_key={}&include_adult=true&page=1".format(numId, self.key)
      req = requests.get(url1)
      dict_infos = req.json()
      listId = [x["id"] for x in dict_infos["items"]]
      return listId


    def serieNumIdSaison(self, numId):
        """infos saisons suivant numID"""
        url1 = self.urlBase + "tv/{}?api_key={}&language={}".format(numId, self.key, self.lang)#, 4)
        req = requests.get(url1)
        dict_serie= req.json()
        try:
          dictAff = {saison["season_number"]:  (saison["name"], saison["poster_path"], self.verifSynop(saison["overview"])) for saison in  dict_serie["seasons"]}
        except:
          dictAff = {}
        return dictAff

    def imageMovie(self, numId):
        url1 = self.urlBase + "movie/{}/images?api_key={}".format(numId, self.key)
        req = requests.get(url1)
        dictImages = req.json()
        logos = [(logo["iso_639_1"], logo["file_path"]) for logo in dictImages["logos"] if logo["iso_639_1"] in ["fr", "en"]]
        if logos:
          logosFr  = [logo for logo in logos if logo[0] == "fr"]
          if logosFr:
            return logosFr[0]
          else:
            return logos[0]
        else:
          return ""

    def searchMovie(self, title, filecode, pos, year=0, release=""):
        """search film par nom et annee"""
        self.title = title
        sauveTitle = title
        self.sauveTitle = sauveTitle
        self.year = year
        title = title.replace(".", " ")
        title = title.replace(" ", "+")
        #title = unicodedata.normalize('NFD', title).encode('ascii','ignore').decode("utf-8")
        title = quote(title)
        dictMovies = {}
        if int(year) > 0:
            #Url = "search/movie?query={}&search_type=ngram&api_key={}&page=1&language={}&year={}".format(title, self.key, self.lang, year)
            Url = "search/movie?query={}&search_type=ngram&api_key={}&page=1&language={}&primary_release_year={}".format(title, self.key, self.lang, year)
        else:
            Url = "search/movie?query={}&api_key={}&page=1&language={}".format(title, self.key, self.lang)
        try:
            req = requests.get(self.urlBase + Url)
            dictMovies = req.json()
            if year > 0 and dictMovies["total_results"] == 0:
                Url = "search/movie?query={}&api_key={}&page=1&language={}".format(title, self.key, self.lang)
                req = requests.get(self.urlBase + Url)

                dictMovies = req.json()
        except Exception as e:
            pass
        try:
          genres = dictMovies["results"][0]["genre_ids"]
          dictMovies["results"][0]["genre_ids"] = self.formatGenre(genres)
        except: pass
        if "results" not in dictMovies.keys()  or not dictMovies["results"]:
            dictMovies = {u'total_results': 1, u'total_pages': 1, u'page': 1, u'results': [{u'poster_path': u'', u'title': unquote(sauveTitle), u'overview': u'', u'release_date': year, u'popularity': 0,\
             u'original_title': u'', u'backdrop_path': u'', u'vote_count': 0, u'video': False, u'adult': False, u'vote_average': 0, u'genre_ids': [], u'id': 0, u'original_language': u''}]}
        if "#" in filecode:
          if filecode.split("#")[1]:
            dictMovies["results"][0]["title"] = dictMovies["results"][0]["title"] + ' [%s]' %filecode.split("#")[1]
        if release:
            dictMovies["results"][0]["overview"] = "Release: %s\n" %release + dictMovies["results"][0]["overview"]

        self.tabMedia.append((pos, filecode, dictMovies))
        return dictMovies

    def formatGenre(self, tab):
      dictGenre={28:"Action", 12:"Aventure", 16:"Animation", 35:"Comedie", 80:"Crime", 99:"Documentaire", 18:"Drame", 10751:"Familial", 14:"Fantastique", 10769:"Etranger", 36:"Histoire", 27:"Horreur",
                  10402:"Musique", 9648:"Mystere", 10749:"Romance", 878:"Science-Fiction", 10770:"Telefilm", 53:"Thriller", 10752:"Guerre", 37:"Western",
                  10759:"Action & Adventure", 10762:"Kids", 9648:"Mystery", 10763:"News", 10764:"Reality", 10765:"Science-Fiction & Fantastique", 10766:"Soap", 10767:"Talk", 10768:"War & Politics",
                  28:"Action", 12:"Aventure",10751:"Familial"}
      return ", ".join([dictGenre[x] for x in tab])

    def searchEpisode(self, nom, saison, episode, filecode, pos, year=0, release=""):
        """rechercher serie par nom"""
        sauveTitle = "{} ({}".format(nom, episode)
        self.sauveTitle = sauveTitle
        self.year = year
        tabRemp = [("(", " "), (")", " "), (".", " "), ("2020", ""), ("2019", ""), ("2021", ""), ("2022", "")]
        for remp in tabRemp:
            nom = nom.replace(remp[0], remp[1])
        nom = nom.strip()
        nom = nom .replace(" ", "+")
        if int(year) > 0:
            url1 = self.urlBase + "search/tv?query={}&api_key={}&page=1&language={}&first_air_date_year={}".format(nom, self.key, self.lang, year)
        else:
            url1 = self.urlBase + "search/tv?query={}&api_key={}&page=1&language={}".format(nom, self.key, self.lang)
        dict_serie = {}
        try:
          req = requests.get(url1)
          dict_serie = req.json()
          try:
            dict_serie["results"][0]["genre_ids"] = self.formatGenre(dict_serie["results"][0]["genre_ids"])
          except: pass
          dict_serie["results"][0]["release_date"] = dict_serie["results"][0]['first_air_date']
          dict_serie["results"][0]["title"] = "%s (%sE%d)" %(dict_serie["results"][0]['name'], episode.split("E")[0], int(episode.split("E")[1]))
        except Exception as e:
          pass
        if "results" not in dict_serie.keys() or not dict_serie["results"]:
            dict_serie = {u'total_results': 1, u'total_pages': 1, u'page': 1, u'results': [{u'poster_path': u'', u'title': unquote(sauveTitle), u'overview': u'', u'release_date': year, u'popularity': 0, u'original_title': u'', u'backdrop_path': u'',\
                     u'vote_count': 0, u'video': False, u'adult': False, u'vote_average': 0, u'genre_ids': [], u'id': 0, u'original_language': u''}]}
        if "#" in filecode:
          dict_serie["results"][0]["title"] = dict_serie["results"][0]["title"] + ' [%s]' %filecode.split("#")[1]
        if release:
          dict_serie["results"][0]["overview"] = "Release: %s\n" %release + dict_serie["results"][0]["overview"]
        self.tabMedia.append((pos, filecode, dict_serie))
        return dict_serie

    def searchTVshow(self, nom, rep, pos, year=0):
        """rechercher serie par nom"""
        sauveTitle = nom
        self.year = year
        tabRemp = [("(", " "), (")", " "), (".", " "), ("2020", ""), ("2019", ""), ("2021", ""), ("2022", "")]
        for remp in tabRemp:
            nom = nom.replace(remp[0], remp[1])
        nom = nom.strip()
        nom = nom .replace(" ", "+")
        if int(year) > 0:
            url1 = self.urlBase + "search/tv?query={}&api_key={}&page=1&language={}&first_air_date_year={}".format(nom, self.key, self.lang, year)
        else:
            url1 = self.urlBase + "search/tv?query={}&api_key={}&page=1&language={}".format(nom, self.key, self.lang)
        dict_serie = {}
        try:
          req = requests.get(url1)
          dict_serie = req.json()
          try:
            dict_serie["results"][0]["genre_ids"] = self.formatGenre(dict_serie["results"][0]["genre_ids"])
          except: pass
          dict_serie["results"][0]["release_date"] = dict_serie["results"][0]['first_air_date']
          dict_serie["results"][0]["title"] = dict_serie["results"][0]['name']
        except Exception as e:
          pass
        if "results" not in dict_serie.keys() or not dict_serie["results"]:
            dict_serie = {u'total_results': 1, u'total_pages': 1, u'page': 1, u'results': [{u'poster_path': u'', u'title': unquote(sauveTitle), u'overview': u'', u'release_date': year, u'popularity': 0,
                u'original_title': u'', u'backdrop_path': u'', u'vote_count': 0, u'video': False, u'adult': False, u'vote_average': 0, u'genre_ids': [], u'id': 0, u'original_language': u''}]}
        self.tabMedia.append((pos, rep, dict_serie))
        return dict_serie

    def tvshowId(self, nom, rep, pos, numId, params=""):
        url1 = self.urlBase + "/tv/{}?&api_key={}&language={}&".format(numId, self.key, self.lang)
        dict_infos = {}
        try:
          req = requests.get(url1)
          dict_infos = req.json()
        except:
          pass
        try:
          if nom[:3] == " (S":
            title = dict_infos.get("name", "") + nom
          else:
            title = dict_infos.get("name", nom)
          dict_serie = {u'total_results': 1, u'total_pages': 1, u'page': 1, u'results': [{u'poster_path': dict_infos.get("poster_path", ""), u'title': title, u'overview': dict_infos.get("overview", "Pas de synop..."),
              u'release_date': dict_infos.get("first_air_date", 0), u'popularity': dict_infos.get("popularity", 0.0), u'original_title': u'', u'backdrop_path': dict_infos.get("backdrop_path", ""), u'vote_count': dict_infos.get("vote_count", 0),
              u'video': False, u'adult': False, u'vote_average': dict_infos.get("vote_average", 0.0), u'genre_ids': [], u'id': dict_infos.get("id", 0), u'original_language': dict_infos.get("original_language", "")}]}
          try:
            dict_serie["results"][0]["genre_ids"] = ", ".join([z for y in dict_infos["genres"] for x, z in y.items() if x == "name"])
          except:
            dict_serie["results"][0]["genre_ids"] = ""
        except:
          dict_serie = {u'total_results': 1, u'total_pages': 1, u'page': 1, u'results': [{u'poster_path': u'', u'title': nom, u'overview': u'', u'release_date': 0, u'popularity': 0,
                u'original_title': u'', u'backdrop_path': u'', u'vote_count': 0, u'video': False, u'adult': False, u'vote_average': 0, u'genre_ids': [], u'id': 0, u'original_language': u''}]}
        if params:
          self.tabMedia.append((pos, rep + "*" + params, dict_serie))
        else:
          self.tabMedia.append((pos, rep, dict_serie))
        return dict_serie


    @property
    def extractListe(self):
        #m.title, m.overview, m.year, m.poster, m.numId, m.genre, m.popu, link, m.backdrop, m.runtime, m.id
        for pos, filecode, infosT in sorted(self.tabMedia):
            #notice(infosT)
            try:
              infos = infosT["results"][0]
              try:
                year = int(infos["release_date"][:4])
              except:
                year = 0
              self.tabMediaFinal.append((pos, infos.get("title", ""), infos.get("overview", "pas de synop.."), year, infos.get("poster_path", ""), infos["id"], infos.get("genre_ids", "")\
                , infos.get("popularity", 0.0), filecode, infos.get("backdrop_path", ""), 0, 0))
            except Exception as e:
              #notice(e)
              self.tabMediaFinal.append((pos, self.sauveTitle, "", int(self.year), "", 0, "", "", filecode, "", 0, 0))
        return self.tabMediaFinal

    def seriesDiffuseur(self, numId, page=1):
      url1 = self.urlBase + "discover/tv?with_networks={}&sort_by=popularity.desc&api_key={}&language={}&page={}".format(numId, self.key, self.lang, page)
      dict_infos = {}
      try:
        req = requests.get(url1)
        dict_infos = req.json()
      except:
        pass
      try:
        self.tabNumIdDiff += [x["id"] for x in dict_infos["results"]]
      except:
        pass
      return dict_infos["total_pages"]

    def getIdDiffuseur(self, numId, page=1):
      self.tabNumIdDiff = []
      ttp = self.seriesDiffuseur(numId, page)
      for p in range(page + 1, ttp, 1):
        threading.Thread(name="diffuseur", target=self.seriesDiffuseur, args=(numId, p,)).start()
        time.sleep(0.03)
      self.testThread("diffuseur")
      return self.tabNumIdDiff

    def testThread(self, nom):
        a = 0
        tActif = True
        while tActif:
            tActif = False
            for t in threading.enumerate():
                if nom == t.getName():
                    tActif = True
            time.sleep(0.1)
            a += 1
            if a > 150:
                break
        return True


if __name__ == '__main__':
  #https://api.themoviedb.org/3/search/keyword?api_key=96139384ce46fd4ffac13e1ad770db7a&query=cat
  #https://api.themoviedb.org/3/keyword/2626?api_key=96139384ce46fd4ffac13e1ad770db7a
  #https://api.themoviedb.org/3/discover/tv?api_key=96139384ce46fd4ffac13e1ad770db7a&with_keywords=10714&include_adult=true
  #https://www.themoviedb.org/list/8195530
  mdb = TMDB("96139384ce46fd4ffac13e1ad770db7a")
  #https://api.themoviedb.org/3/network/213?api_key=96139384ce46fd4ffac13e1ad770db7a
  #https://api.themoviedb.org/3/discover/tv?with_networks=213&sort_by=popularity.desc&api_key=96139384ce46fd4ffac13e1ad770db7a&language=fr
  #La famille parfaite 2021
  #https://api.themoviedb.org/3/search/movie?query=La+famille+parfaite&api_key=96139384ce46fd4ffac13e1ad770db7a&page=1&language=fr&primary_release_year=2021&search_type=ngram
  #mdb.castSerie(1405)
  #mdb.listKeywords(10714)
  print(mdb.getList(8195530))
  #print(mdb.searchPerson("sylvester stallone"))
  #mdb.dateRealeaseMovie(338953)
  #mdb.getGenre()
  #mdb.getNumIdBA(529203)
  #print(mdb.suggReco(529203))
  #mdb.movieNumId(529203)
  #print(mdb.castFilm(529203))
  #print(mdb.getNumIdBA(1405, "tvshow"))
  #print(mdb.person(16483))
  #print(mdb.person(1245))
  #print(mdb.saison(1405, "01"))
  #print(mdb.imageMovie(603))
  #print(mdb.serieNumIdSaison(1405))
  #https://api.themoviedb.org/3/movie/603?api_key=96139384ce46fd4ffac13e1ad770db7a&append_to_response=images
  #https://api.themoviedb.org/3/movie/603/images?api_key=96139384ce46fd4ffac13e1ad770db7a&append_to_response=collection
  #https://api.themoviedb.org/3/movie/603?api_key=96139384ce46fd4ffac13e1ad770db7a&append_to_response=credits
  #https://api.themoviedb.org/3/discover/movie?certification_country=US&certification.lte=G&sort_by=popularity.desc&api_key=96139384ce46fd4ffac13e1ad770db7a&language=fr
  #https://api.themoviedb.org/3/discover/movie?with_companies=2|3&with_genres=16&api_key=96139384ce46fd4ffac13e1ad770db7a&language=fr
  #http://image.tmdb.org/t/p/w185/yjqRwxcbUlwWlIGO1PEnijkHAV.png
""""backdrop_sizes": [
  "w300",
  "w780",
  "w1280",
  "original"
],
"logo_sizes": [
  "w45",
  "w92",
  "w154",
  "w185",
  "w300",
  "w500",
  "original"
],
"poster_sizes": [
  "w92",
  "w154",
  "w185",
  "w342",
  "w500",
  "w780",
  "original"
],
#http://image.tmdb.org/t/p/w92/
"profile_sizes": [
  "w45",
  "w185",
  "h632",
  "original"
],
"still_sizes": [
  "w92",
  "w185",
  "w300",
  "original"
] """