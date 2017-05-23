# connect to the API
from datetime import date
from sentinelsat.sentinel import SentinelAPI, get_coordinates
api = SentinelAPI('dims', 'vekmnbrekmnehfkmysq', 'https://scihub.copernicus.eu/dhus')


# search by polygon, time, and SciHub query keywords
products = api.query(get_coordinates('map.geojson'), \
                     '20151219', date(2015, 12, 29), \
                     platformname = 'Sentinel-2', \
                     cloudcoverpercentage = '[0 TO 30]')

# download all results from the search
api.download_all(products)


# GeoJSON FeatureCollection containing footprints and metadata of the scenes
api.get_footprints(products)

