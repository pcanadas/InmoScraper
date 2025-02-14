"""
Este script verifica si las URLs almacenadas en archivos CSV pueden ser rastreadas según las reglas 
definidas en el archivo robots.txt de un sitio web.

FUNCIONAMIENTO:
1. Carga y analiza el archivo robots.txt de Fotocasa utilizando urllib.robotparser.
2. Lee dos archivos CSV:
   - 'start_urls.csv' (columna 0): Contiene URLs iniciales.
   - 'links_anuncios.csv' (columna 2): Contiene URLs de anuncios.
3. Para cada URL en ambos archivos, verifica si su rastreo está permitido según robots.txt.
4. Muestra un mensaje indicando si la URL puede ser rastreada o no.

USO:
Este script es útil para desarrolladores de web scraping, ya que permite comprobar automáticamente 
si un sitio web permite el rastreo de determinadas páginas antes de ejecutar un crawler.
"""


from urllib.robotparser import RobotFileParser
import pandas as pd

def es_url_permitida(url, robots_url):
    # Cargar el archivo robots.txt
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.read()
    # Verificar si la URL está permitida
    return parser.can_fetch("*", url)

robots_txt_url = "https://www.fotocasa.es/robots.txt" # URL del archivo robots.txt
# Leer los archivo de csv
pd.set_option('display.max_colwidth', None)
df = pd.read_csv('datos/start_urls.csv', header=None)[0]
df_anuncios = pd.read_csv('datos/links_anuncios.csv', header=None)[2]
# Verificar si las URLs están permitidas para rastrear
for url in df:
    if es_url_permitida(url, robots_txt_url):
        print(f"La URL {url} está permitida para rastrear.")
    else:
        print(f"La URL {url} NO está permitida para rastrear.")

for url in df_anuncios:
    if es_url_permitida(url, robots_txt_url):
        print(f"La URL {url} está permitida para rastrear.")
    else:
        print(f"La URL {url} NO está permitida para rastrear.")
