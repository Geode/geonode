from chardet.universaldetector import UniversalDetector
import os.path
import sys
import sys
from osgeo import osr
from urllib import urlencode
from urllib2 import urlopen
import json
from bs4 import BeautifulSoup

shp_file = sys.argv[1]
dbf_file = shp_file[0:-4] + '.dbf'
prj_file = shp_file[0:-4] + '.prj'

#Try detecting the SRID, by default we set to 4326 and hope the best
srid=4326
if os.path.isfile(prj_file):
    #Etape 1 recuper le epsg
    prj_filef = open(prj_file, 'r')
    prj_txt = prj_filef.read()
    prj_filef.close()
    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj_txt])
    srs.AutoIdentifyEPSG()
    code = srs.GetAuthorityCode(None)
    if code:
        srid= code
    else:
        #Ok, no luck, lets try with the OpenGeo service
        query = urlencode({
            'exact' : True,
            'error' : True,
            'mode' : 'wkt',
            'terms' : prj_txt})
        webres = urlopen('http://prj2epsg.org/search.json', query)
        jres = json.loads(webres.read())
        if jres['codes']:
            srid = int(jres['codes'][0]['code'])

    #Etape 2 recuper les metadata du bon epsg et le metre dans le prj
    url_get_epsg = "http://prj2epsg.org/epsg/" + str(srid)
    webget = urlopen(url_get_epsg).read()

    xml_webget = BeautifulSoup(webget)
    print xml_webget.textarea.string.replace('\n','')

print "EPSG = %s " %(srid)

