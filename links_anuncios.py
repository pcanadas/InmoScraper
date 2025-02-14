"""
Este script utiliza Selenium para automatizar la navegación en Fotocasa y extraer enlaces de anuncios.

FUNCIONAMIENTO:
1. Lee un archivo CSV ('start_urls.csv') que contiene las URLs de búsqueda.
2. Para cada URL:
   - Inicializa un navegador Chrome en modo incógnito y, opcionalmente, en modo sin interfaz gráfica (headless).
   - Usa agentes de usuario aleatorios y técnicas para evitar detección.
   - Accede a la página y espera aleatoriamente para simular comportamiento humano.
   - Verifica si la página está bloqueada y detiene el proceso si es necesario.
   - Espera a que la página cargue completamente y cierra pop-ups si aparecen.
   - Obtiene el número total de anuncios disponibles en la página.
   - Si hay anuncios:
     - Hace scroll hasta el final de la página para cargar todos los anuncios.
     - Extrae los enlaces de cada anuncio y los almacena en una lista.
     - Guarda los enlaces en un archivo CSV ('links_anuncios.csv'), junto con la fecha y el código postal extraído de la URL.
3. Espera un tiempo aleatorio entre iteraciones para reducir el riesgo de bloqueo.
4. Cierra el navegador al finalizar.

USO:
Este script es útil para realizar web scraping en Fotocasa de manera automatizada, recopilando enlaces de anuncios de viviendas sin ser detectado fácilmente.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import random
import datetime
import pandas as pd

# Función para evitar bloqueos
def esperar_aleatoriamente(min_seg=5, max_seg=15):
    tiempo = random.randint(min_seg, max_seg)
    sleep(tiempo)

# Leer el archivo de csv
pd.set_option('display.max_colwidth', None)
df = pd.read_csv('datos/start_urls.csv', header=None)[0]
for website in df:
    print(website)
    # Inicializar el driver
    options = Options()
    options.add_argument('--incognito')
    options.add_argument('--headless')  # Opcional: Ejecutar sin interfaz gráfica
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service('chromedriver/chromedriver.exe')
    # Rotar agentes de usuario para evitar detección
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    # Inicializar el driver
    driver = webdriver.Chrome(service=service, options=options)
    esperar_aleatoriamente()  # Esperar antes de interactuar

    # Ingresar a la pagina
    driver.get(str(website))
    esperar_aleatoriamente()  # Esperar antes de interactuar
    driver.maximize_window() # Maximizar la ventana
    

    # Verificar si la pagina esta bloqueada
    bloqueo = driver.find_elements(By.XPATH, '//html/body/div/h1') if driver.find_elements(By.XPATH, '//html/body/div/h1') else 0
    if bloqueo != 0:
        print("Pagina bloqueada")
        driver.quit()
        break

    # Esperar a que cargue la pagina
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="App"]')))
    
    # Espera a que el popup sea visible y cierra el popup
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="didomi-notice-agree-button"]'))
        )
        close_button.click()
    except Exception as e:
        print("No se pudo cerrar el popup:", e)
    
    # Obtener el numero de anuncios     
    nauncios = driver.find_elements(By.XPATH, '//h2[@class="re-SearchPage-counterTitle"]') if driver.find_elements(By.XPATH, '//h2[@class="re-SearchPage-counterTitle"]') else 0
    if nauncios == 0:
        counter = 0
    else:
        for n in nauncios:
            counter = n.text.split(" ")[0]
    print(counter)

    # Obtener los links de los anuncios
    links = []
    if int(counter) == 0: # Si no hay anuncios
        print("No se encontraron anuncios")
        esperar_aleatoriamente(1, 5)  # Esperar antes de seguir
        driver.quit()
        continue # Continuar con el siguiente website
        
    else:    
        # Hacer scroll hasta el final de la pagina
        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
        for e in range(0, height, 700):
            driver.execute_script('window.scrollTo(0, {});'.format(e))
            esperar_aleatoriamente(1, 5)  # Esperar antes de seguir
        
        for i in range(1, int(counter)+1): # Obtener los links de los anuncios
            try:
                link = driver.find_element(By.XPATH, '//section[@class="re-SearchResult"]/article[{}]/a'.format(i)) # Obtener el link
                links.append(link.get_attribute('href'))
                esperar_aleatoriamente()  # Esperar antes de seguir
            except:
                print("No se pudo obtener el link")

            print(links)
        
        cd_postal = website.split("zipCode=")[1] # Obtener el codigo postal
        fecha = datetime.datetime.now().strftime("%Y-%m-%d") # Obtener la fecha actual

        # Guardar los links en un archivo csv
        links_df = pd.DataFrame(links, columns=['links'])
        links_df.insert(0, 'fecha', fecha)
        links_df.insert(1, 'codigo_postal', cd_postal)
        links_df.to_csv('datos/links_anuncios.csv', mode='a', index=False, header=False)
        print("Links guardados")

        esperar_aleatoriamente(60, 90)  # Esperar antes de seguir
    
    # Cerrar el driver
    driver.quit()