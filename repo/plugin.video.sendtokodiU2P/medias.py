# -*- coding: utf-8 -*-
import os
import sqlite3
import re
import requests
import sys
try:
  import xbmcaddon
except: pass






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

    def getGenre(self, typM="movie"):
      """movie or tv"""
      url1 = self.urlBase + "genre/{}/list?api_key={}&language={}".format(typM, self.key, self.lang) 
      req = requests.get(url1)
      dictInfos = req.json()
      genres = [x["name"] for x in dictInfos["genres"]]
      return genres

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

    def movieNumId(self, numId):
      """infos film via numID"""
      url1 = self.urlBase + "movie/{}?api_key={}&language={}".format(numId, self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      print(str(dictInfos).encode(sys.stdout.encoding, errors='replace'))

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

    def person(self, numId):
      url1 = self.urlBase + "person/{}/movie_credits?api_key={}&language={}".format(numId, self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      tabFilm = [x["id"] for x in dictInfos["cast"]]
      tabFilm += [x["id"] for x in dictInfos["crew"]]
      return tabFilm

    def saison(self, numId, saison):
      url1 = self.urlBase + "tv/{}/season/{}?api_key={}&language={}".format(numId, saison, self.key, self.lang)
      req = requests.get(url1)
      dictInfos = req.json()
      tabEpisodes = []
      for episode in dictInfos["episodes"]:
          try:
            name = episode["name"]
          except:
            name = ""
          try:
            overview = episode["overview"]
            if not overview:
              overview = "Pas de Synopsis...."  
          except:
            overview = "Pas de Synopsis...."
          try:
            dateRelease = episode["air_date"]
          except:
            dateRelease = ""
          try:
            backdrop = episode["still_path"]
          except:
            backdrop = ""
          try:
            popu = episode["vote_average"]
          except:
            popu = 0.0
          try:
            numSaison = episode["season_number"]
          except:
            numSaison = int(saison)
          numEpisode = episode["episode_number"]    
          tabEpisodes.append([name, overview, dateRelease, backdrop, popu, numSaison, numEpisode])
      return tabEpisodes 

    def verifSynop(self, tx):
      if not tx:
        tx = "Pas de Synopsis...."
      return tx


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
      
        
        
if __name__ == '__main__':
  mdb = TMDB("96139384ce46fd4ffac13e1ad770db7a")
  #mdb.getGenre()
  #mdb.getNumIdBA(529203)
  #print(mdb.suggReco(529203))
  #mdb.movieNumId(529203)
  #print(mdb.castFilm(529203))
  #print(mdb.getNumIdBA(1405, "tvshow"))
  #print(mdb.person(16483))
  #print(mdb.person(1245))
  #print(mdb.saison(1405, "01"))
  print(mdb.imageMovie(603))
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