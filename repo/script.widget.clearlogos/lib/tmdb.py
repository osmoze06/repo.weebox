import requests
import urllib

class TMDB:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_clearlogo(self, title):
        # Recherche de la série ou du film dans l'API de TMDB
        response = requests.get('https://api.themoviedb.org/3/search/multi?api_key=' + self.api_key + '&language=en-US&query=' + urllib.parse.quote(title) + '&page=1&include_adult=false')

        # Vérification de la réponse HTTP
        if response.status_code != 200:
            return None

        # Récupération de la première série ou du premier film correspondant à la recherche
        results = response.json().get('results')
        if results:
            result = results[0]

            # Vérification si c'est une série ou un film
            media_type = result.get('media_type')
            if media_type == 'tv':
                return self.get_tv_clearlogo(result.get('id'))
            elif media_type == 'movie':
                return self.get_movie_clearlogo(result.get('id'))

        return None

    def get_tv_clearlogo(self, tv_id):
        # Récupération des informations de la série depuis l'API
        response = requests.get('https://api.themoviedb.org/3/tv/' + str(tv_id) + '?api_key=' + self.api_key + '&language=en-US')

        # Vérification de la réponse HTTP
        if response.status_code != 200:
            return None

        # Récupération de l'URL du clearlogo
        result = response.json()
        clearlogo_path = result.get('images', {}).get('clearlogo', [])[0].get('file_path')
        if clearlogo_path:
            return 'https://image.tmdb.org/t/p/original' + clearlogo_path

        return None

    def get_movie_clearlogo(self, movie_id):
        # Récupération des informations du film depuis l'API
        response = requests.get('https://api.themoviedb.org/3/movie/' + str(movie_id) + '?api_key=' + self.api_key + '&language=en-US')

        # Vérification de la réponse HTTP
        if response.status_code != 200:
            return None

        # Récupération de l'URL du clearlogo
        result = response.json()
        clearlogo_path = result.get('images', {}).get('clearlogo', [])[0].get('file_path')
        if clearlogo_path:
            return 'https://image.tmdb.org/t/p/original' + clearlogo_path

        return None