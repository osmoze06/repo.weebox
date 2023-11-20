#!/usr/bin/python
# -*- coding:Utf-8 -*-
import requests
import ast
import re
import random, sys
import io
import time
import sqlite3
import os
import json
from json import JSONDecodeError
try:
    # Python 3

    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser
try:
    # Python 3
    from urllib.parse import unquote, urlencode, quote
    unichr = chr
except ImportError:
    # Python 2
    from urllib import unquote, urlencode, quote
import urllib.request
from bs4 import BeautifulSoup
from util import *


class Crypt:

    def __init__(self):
        self.url = "https://1fichier.com"
        self.urlBase = "https://darkibox.com/"
        self.host = "darkibox.com"


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
        for j, t in enumerate(tx):
            try:
                tab0 = self._swapKey(tab0, j)
                d = {x: tab1[i] for i, x in enumerate(tab0)}
                texCrypt += d[t]
            except: pass
        return texCrypt

    def decrypt(self, tx, tab0, tab1):
        texCrypt = ""
        for j, t in enumerate(tx):
            tab0 = self._swapKey(tab0, j)
            d = {x: tab0[i] for i, x in enumerate(tab1)}
            texCrypt += d[t]
        return texCrypt

    def _swapKey(self, key, swap):
        key = "".join([key[(i + swap) % len(key)]  for i in range(len(key))])
        return key

    def extractReso(self, tabLinkCrypte):
        tabLinkDecrypt = [self.url + "/?" + self.cryptFile(x, cr=0) for x in tabLinkCrypte]
        tabResos, tabSizes, tabRelease = self.searchReso(tabLinkDecrypt)
        print(tabLinkDecrypt, tabResos, tabSizes, tabRelease)
        dictResos = {x: (tabResos[i], tabSizes[i], tabRelease[i]) for i, x in enumerate(tabLinkCrypte)}
        return dictResos

    def searchReso(self, tabFilesCode):
        tabResos = []
        tabSizes = []
        tabRelease = []
        filesInfo = self.extractLinks(tabFilesCode)
        for cr in tabFilesCode:
            try:
                tabSizes.append(filesInfo[cr][2])
                tabRelease.append(filesInfo[cr][1])
                argv = self.extractResoName(filesInfo[cr][1])
                ext = argv.pop(-2)
                if not argv[4]:
                    if "avi" in ext:
                        argv[4] = ['480']
                resoRelease = "%s" %".".join(["-".join(x) for x in argv[1:] if x])
                tabResos.append(resoRelease)

            except Exception as e:
                tabResos.append("ind")
                tabSizes.append(0)
                tabRelease.append("")

                print("Erreur search reso", e)
        return tabResos, tabSizes, tabRelease

    def extractResoName(self, name):
        reso = {"1080": False, "720": False, "2160": False, "480": False, "4K": False, '360': False, "3D": False, "xvid":False}
        typeReso = {"HDlight": False, "Light": False, "ultraHDlight": False, "fullhd": False, "REMUX": False, "4KLight": False}
        source = {"BLURAY": False, "WEB": False, "WEBRIP": False, "DVDRiP": False, "BDRIP": False, "HDTV": False, "BRRip": False, "HDrip": False, "Cam": False, "RZP": False}
        audio = {".VO.": False, "VOSTFR": False, "VFF": False, "VFI": False, 'VFQ': False, "VF": False, "FR.JP": False, "FR.EN": False, "FR": False, "VOA.": False, "TRUEFRENCH": False, "French": False, "Multi": False, "VOF.": False}
        extension = {"avi": False, "divx": False, "mkv": False, "mp4": False, "ts": False, "mpg": False}
        name = unquote(name)
        #print(name)
        for m in ["_", " ", "[", "]", "-", "(", ")"]:
            name = name.replace(m, ".")
        masque = r'(.*)([\.\(]19\d\d|[\.\(]20\d\d)(?P<release>[\.\)].*)'
        r = re.match(masque, name)
        try:
            release = r.group("release")
        except:
            release = name
            #print("erreur reso name:", name)
        #print(release)
        for tab in [reso, typeReso, audio, source]:
            for motif in tab.keys():
                r = re.search(r'%s' %motif.replace(".", r"\."), release, re.I)
                if r:
                    tab[motif] = True
        for ext in extension.keys():
            if ext == release[-3:]:
                extension[ext] = True

        return [name, [k for k, v in reso.items() if v], [k for k, v in typeReso.items() if v], [k for k, v in audio.items() if v], [k for k, v in extension.items() if v], [k for k, v in source.items() if v]]


    def extractLinks(self, tabFile):
        dictLien = {}
        tabFile = list(set(tabFile))
        url = self.url + "/check_links.pl"
        data = "&".join(["links[]=" + quote(self.url + "/?" + self.cryptFile(x, 0)) for x in tabFile])
        #notice(data)
        data = data.replace("/", "%2f")
        x = len(data)
        headers = {"Host": "1fichier.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "LG=en",
            "Accept-Encoding": "gzip, deflate",
            "Content-Length": str(x)
            }
        r = requests.post(url, data=data.encode("utf-8"), headers=headers)
        for l in r.content.decode("latin-1").splitlines():
            tab = l.split(";")
            #print(tab)
            link = self.cryptFile(tab[0].split("/?")[-1])
            try:
                taille = int(tab[-1])
                release = tab[-2]
                dictLien[link] = [link, release, taille]
            except:
                print("lien out")
                dictLien[link] = []
        return dictLien

    def validLinkDark(self, tabFile):
        tabFile = ["https://darkibox.com/" + self.cryptFile(x, 0) for x in tabFile]
        masqueOk = r'(\w{12})\%? found'
        url = "https://darkibox.com/?op=checkfiles"
        data = "op=checkfiles&process=Check+URLs&list=%s%%0A" % "%%0A".join([x.replace("://", "%%3A%%2F%%2F").replace("/", "%%2F") for x in tabFile])
        headers = {"Host": "darkibox.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "LG=en",
            "Accept-Encoding": "gzip, deflate",
            }
        r = requests.post(url, data=data.encode("utf-8"), headers=headers)
        #print(url)
        soup = BeautifulSoup(r.content, "html.parser")
        links = soup.findAll("div", {"class": "mb-3"})
        tx = [x.text for x in links if "darkibox" in x.text][0]
        linkOk = ["https://darkibox.com/" + x for x in re.findall(masqueOk, tx)]
        linkOut = [ x for x in tabFile if x not in linkOk]
        return [self.cryptFile(x.split("/")[-1]) for x in linkOk], [self.cryptFile(x.split("/")[-1]) for x in linkOut]

    def extractLinksDarkibox(self, tabFile):
        #'https://1fichier.com/?c5e3ohrmfj': ['https://1fichier.com/?c5e3ohrmfj', 'Chisum._John.Wayne.1970.Western_.DVDRIP.FR.avi', 735217676]
        dictLien = {}
        linkOk, linkOut = self.validLinkDark(tabFile)
        #print(linkOk, linkOut)
        for link in linkOk:
            url = link.replace("https://darkibox.com/", "https://darkibox.com/d/")
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            titre = soup.find("h3", {"class": "mb-5"})
            release = titre.text.replace("Download ", "").replace("\n", "").replace("\r", "").strip()
            taille = soup.find("span",  {"class": "small"})
            taille = int(float(taille.text.replace("Download ", "").replace("\n", "").replace("\r", "").strip().split(",")[1].replace("GB", "").replace("MB", "")) * 1000000000)
            dictLien[link] = [link, release, taille]
        for link in linkOut:
            dictLien[link] = []
        return dictLien

    def debridFree(self, link):
        lDebrid = ""
        try:
            url =  os.path.join(self.urlBase, "d/", link + "_o")
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            data = ""
            for ch in ["op", "id", "mode", "hash"]:
                data += ch + "=" + soup.find('input', {'name': ch}).get('value') + "&"
            data = data[:-1]
            x = len(data)

            headers = {"Host": self.host,
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:76.0) Gecko/20100101 Firefox/76.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-gb, en;q=0.8",
                "Cache-Control": "no-cache",
                "Referer": url,
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": "lang=english",
                "Accept-Encoding": "gzip, deflate",
                "Content-Length": str(x)
                }
            time.sleep(0.5)
            r = requests.post(url, data=data.encode("utf-8"), headers=headers, verify=False)
            soup = BeautifulSoup(r.content, "html.parser")
            lDebrid = soup.find("a", {"class": "btn btn-gradient submit-btn"})
            lDebrid = lDebrid["href"]
        except: pass
        return lDebrid

    def upload1fichier(self, file_path, key):
        #curl -H "Authorization: Bearer API_KEY" -v -F "file[]=@local_filename.txt;filename=Filename.txt" https://upload.1fichier.com/upload.cgi?id=UPLOAD_ID
        r = requests.get('https://api.1fichier.com/v1/upload/get_upload_server.cgi', headers={'Authorization':'Bearer {}'.format(key),'Content-Type':'application/json'})
        if r.ok:
            o = r.json()
            up_srv = o['url']
            id = o['id']

            multiple_files = [('file[]', (file_path, open(file_path, 'rb'), 'application/octet-stream'))]

            up_u = 'https://{}/upload.cgi?id={}'.format(up_srv, id)
            r = requests.post(up_u, files = multiple_files, headers={'Authorization':'Bearer {}'.format(key)}, allow_redirects=False)
            if 'Location' in r.headers:
                loc = r.headers['Location']

                r = requests.get('https://{}{}'.format(up_srv, loc))
                x = re.search('<td class="normal"><a href="(.+)"', r.text)
                if x:
                    return x.group(1)
                else:
                    return ""
            else:
                return ""
        else:
            return ""

    def uploadDarkibox(self, file_path, key):
        url = self.urlBase + "api/upload/server?key=" + key
        r = requests.get(url)
        if r.ok:
            resp = r.json()
            urlServ = resp["result"]
        else:
            urlServ = ""

        if urlServ:
            chemin, nom = os.path.split(file_path)
            f = {"file" : (nom, open(file_path, 'rb'))}
            data = {"key": key}
            r = requests.post(urlServ, data=data, files=f, allow_redirects=True)
            if r.ok:
                resp = r.json()
                return resp["files"][0]["filecode"]
            else:
                return ""
        else:
            return ""

    def infoCompteDarkibox(self, key):
        url = self.urlBase + "api/account/info?key={}".format(self.key)
        r = requests.get(url)
        try:
            infos = r.json()
            return infos["result"]["premium"]
        except:
            return 0

    def debridDarkibox(self, filecode, key):
        url = self.urlBase + "api/file/direct_link?key={}&file_code={}".format(key, filecode)
        r = requests.get(url)
        notice(url)
        if r.ok:
            infos = r.json()
            notice(infos)
            dictLiens = {x["name"]: (x["url"], x["filename"], x["size"]) for x in infos["result"]["versions"]}
            return dictLiens
        else:
            return {}

    def resolveLink(self, linkUrl, key):
        notice(linkUrl)

        if len(key) == 32:
            notice("Key 1fichier")

            if "darkibox" in linkUrl:
                return self.debridFree(linkUrl.split("/")[-1]), "darkibox"
            else:
                params = {
                    'url' : linkUrl,
                    'inline' : 0,
                    'cdn' : 0,
                    'restrict_ip':  0,
                    'no_ssl' : 0,
                    }

                url = 'https://api.1fichier.com/v1/download/get_token.cgi'
                r = requests.post(url, json=params, headers={'Authorization':'Bearer {}'.format(key.strip()),'Content-Type':'application/json'})
                try:
                    o = r.json()
                except JSONDecodeError:
                    o = ""
                notice(o)
                message = ""
                if 'status' in o:
                    if o['status'] != 'OK':
                        message = r.json()['message']
                        o['url'] = ""
                    return o["url"], message

                else:
                    return "", "err"
                #else:
                    #~ No status available, assume response is okay
                    #return o
        else:
            notice("Key Alldeb")
            dlLink = ""
            statut = "ok"
            url1 = "http://api.alldebrid.com/v4/link/unlock?agent=u2p&apikey=%s&link=%s" % (key.strip() , linkUrl)
            #notice(url1)
            req = requests.get(url1)
            dict_liens = req.json()
            #notice(dict_liens)
            try:
                if dict_liens["status"] == "success":
                    dlLink = dict_liens['data']['link']
                else:
                    statut = dict_liens["error"]["code"]
            except: pass
            return dlLink, statut

            #realdeb
            """
            #52
            key = "JUP7JPSRU6RET2L7G4IHFF7VUBRXKD5QJXNP75H2WZ5XC2QZBZMQ"
            headers = {'Authorization': 'Bearer %s' %key}
            data = {'link': linkUrl, 'password':''}
            r = requests.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', data=data, headers=headers)
            dictData = r.json()
            if 'error' in dictData.keys():
                link, status = "", 'err'
            else:
                link, status = dictData['download'], "ok"

            return link, status
            """


if __name__ == '__main__':
    #
    #movie 14161 https://1fichier.com/?mzxcyjwkvj52xengqnpf mzxcyjwkvj52xengqnpf 4bBDfpZe74BT2upFZ13U mzxcyjwkvj52xengqnpf
    v = "0.2"

    tab = ["R0aWfwjPAIL2XyVlZXmh",
"3K5XIEgutXudXCjPc39M",
"ZApX1cgNMLxfgsGdg9Bl",
"mU84MpZpgLuHx1Fo8igf",
"b4py3GqrTp8G7ZCRiLiC",
"xYtuKDa9zvwQiYAI7AFD",]
    cr = Crypt()
    for k, v in cr.extractReso(tab).items():
        print(k, v)
    #print(cr.resolveLink("https://1fichier.com/?eyiok1mtptwfowxdrzm9", '_2=aTM3LYLxX8CQjMxX4Mpx2Ms6oxtVE'))