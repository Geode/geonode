from django.db import models

from chardet.universaldetector import UniversalDetector
import itertools
import os.path
import sys
from osgeo import osr
from urllib import urlencode
from urllib2 import urlopen
import json
import subprocess
from bs4 import BeautifulSoup

class Prj2Epsg (models.Model):

    @staticmethod
    def detect_epsg(file_prj):
        epsg = 4326
        if os.path.isfile(file_prj):
            prj_filef = open(file_prj, 'r')
            prj_txt = prj_filef.read()
            prj_filef.close()
            srs = osr.SpatialReference()
            srs.ImportFromESRI([prj_txt])
            srs.AutoIdentifyEPSG()
            code = srs.GetAuthorityCode(None)
            if code:
                epsg = code
            else:
                query = urlencode({
                    'exact' : True,
                    'error' : True,
                    'mode' : 'wkt',
                    'terms' : prj_txt})
                webres = urlopen('http://prj2epsg.org/search.json', query)
                jres = json.loads(webres.read())
                if jres['codes']:
                    epsg = int(jres['codes'][0]['code'])

        return epsg

    @staticmethod
    def replace_epsg(file_prj):
        epsg = Prj2Epsg.detect_epsg(file_prj)
        #recuper les metadata du bon epsg et le metre dans le prj
        url_get_epsg = "http://prj2epsg.org/epsg/" + str(epsg)
        webget = urlopen(url_get_epsg).read()

        xml_webget = BeautifulSoup(webget)
        result = xml_webget.textarea.string.replace('\n','')
        return True, result, epsg

