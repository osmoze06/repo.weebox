# -*- coding: utf-8 -*-
import os
import sqlite3
import re
import requests
import sys


class Media:
    def __init__(self, typeMedia="film", *argvs):
        self.typeMedia = typeMedia

        if self.typeMedia == "movie":
          #title, overview, year, poster, numId, genre, popu
          self.year = argvs[2]
          self.duration = ""
          self.popu = argvs[6]
          self.backdrop = "http://image.tmdb.org/t/p/w780%s"
          self.poster = "http://image.tmdb.org/t/p/w185%s" %argvs[3]
          self.genre = argvs[5]
          self.title= argvs[0]
          self.overview = argvs[1]
          self.numId = argvs[4]
          self.link = argvs[7]
          
        elif self.typeMedia == "tvshow":
          self.year = argvs[2]
          self.duration = ""
          self.popu = argvs[6]
          self.backdrop = "http://image.tmdb.org/t/p/w780%s"
          self.poster = "http://image.tmdb.org/t/p/w185%s" %argvs[3]
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
          self.backdrop = "http://image.tmdb.org/t/p/w780%s"
          self.poster = "http://image.tmdb.org/t/p/w185%s" %argvs[3]
          self.genre = ""
          self.title= argvs[1]
          self.overview = argvs[2]
          self.numId = argvs[0]
          
        elif self.typeMedia == "episode":
          #[35339, 'Saison 01', 'S01E01', 'C9PxOAB66@nRlEQs5IiKHK#SD*C9PxOAB66@xClOGtaqotVH#1080P*xMZPoCbT0@8VJMS21ZpReE#*zi6kvPg63@FM63Jev8MtqA#1080P', 'Jack Sylvane', overview", '2012-01-16', '/A97bfgXNHR97WUTn52B4e8zsmn2.jpg', 7.6, 1, 1]
          self.year = argvs[6]
          self.duration = ""
          self.popu = argvs[-2]
          self.backdrop = "http://image.tmdb.org/t/p/w780%s" %argvs[7]
          self.poster = "http://image.tmdb.org/t/p/w185%s" 
          self.genre = ""
          self.title= argvs[4]
          self.overview = argvs[5]
          self.numId = argvs[0]
          self.link = argvs[3]
          self.episode = argvs[-1]
          self.saison = argvs[-2]

        elif self.typeMedia == "cast":
          #('Artemis Pebdani', 'Additional Voices (voice)', '/ctwVQYbcOuTIQJ866fi3AhzqKBM.jpg', numId)
          self.year = ""
          self.duration = ""
          self.popu = ""
          self.backdrop = "http://image.tmdb.org/t/p/w780%s"
          self.poster = "http://image.tmdb.org/t/p/w185%s" %argvs[2]
          self.genre = ""
          self.title= argvs[0]
          self.overview = argvs[1]
          self.numId = argvs[3]
          self.link = ""

        elif self.typeMedia == "lien":
          #('Artemis Pebdani', 'Additional Voices (voice)', '/ctwVQYbcOuTIQJ866fi3AhzqKBM.jpg', numId)
          self.year = ""
          self.duration = ""
          self.popu = ""
          self.backdrop = "http://image.tmdb.org/t/p/w780%s"
          self.poster = "http://image.tmdb.org/t/p/w185%s"
          self.genre = ""
          self.title= argvs[0]
          self.overview = "\n\n\nRelease: %s" %argvs[2]
          self.numId = ''
          self.link = argvs[1]

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

if __name__ == '__main__':
  mdb = TMDB("96139384ce46fd4ffac13e1ad770db7a")
  #mdb.getGenre()
  #mdb.getNumIdBA(529203)
  #print(mdb.suggReco(529203))
  #mdb.movieNumId(529203)
  #print(mdb.castFilm(529203))
  print(mdb.getNumIdBA(1405, "tvshow"))
  #print(mdb.person(16483))
  #print(mdb.person(1245))
  print(mdb.saison(1405, "01"))
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