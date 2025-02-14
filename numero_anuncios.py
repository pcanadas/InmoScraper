"""
Este script utiliza Selenium para automatizar la navegación en sitios web y recopilar datos de anuncios en Fotocasa.

FUNCIONAMIENTO:
1. Lee un archivo CSV ('start_urls.csv') que contiene las URLs de inicio.
2. Para cada URL:
   - Inicializa un navegador Chrome en modo incógnito con opciones para evitar detección.
   - Usa agentes de usuario aleatorios para reducir el riesgo de bloqueo.
   - Accede a la página y espera aleatoriamente para imitar el comportamiento humano.
   - Verifica si la página está bloqueada y detiene el proceso si es necesario.
   - Espera a que la página cargue completamente y cierra pop-ups si aparecen.
   - Hace scroll hasta el final de la página para cargar todos los anuncios.
   - Extrae y cuenta el número de anuncios presentes en la página.
3. Al final, muestra el total de anuncios encontrados y cierra el navegador.

USO:
Este script es útil para realizar web scraping en Fotocasa de manera automatizada, minimizando la detección y bloqueos.
Finalmente nos proporciona el número de anuncios encontrados en cada una de las URLs de inicio.
"""


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import random
import pandas as pd

# Función para evitar bloqueos
def esperar_aleatoriamente(min_seg=5, max_seg=15):
    tiempo = random.randint(min_seg, max_seg)
    sleep(tiempo)

# Leer el archivo de csv
pd.set_option('display.max_colwidth', None)
df = pd.read_csv('datos/start_urls.csv', header=None)[0]
numero = 0
for website in df:
    print(website)
    # Inicializar el driver
    options = Options()
    options.add_argument('--incognito')
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

    # Ingresar a la pagina
    driver.get(str(website))
    esperar_aleatoriamente()
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

    # Hacer scroll hasta el final de la pagina
    height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
    for e in range(0, height, 700):
        driver.execute_script('window.scrollTo(0, {});'.format(e))
        esperar_aleatoriamente(1, 5) # Esperar a que cargue la pagina

    # Obtener el numero de anuncios en la pagina  
    nauncios = driver.find_elements(By.XPATH, '//*[@id="App"]/div[1]/div[3]/div/main/div/div[2]/div/h2') if driver.find_elements(By.XPATH, '//*[@id="App"]/div[1]/div[3]/div/main/div/div[2]/div/h2') else 0
    
    if nauncios == 0:
        counter = 0
    else:
        for n in nauncios:
            counter = n.text.split(" ")[0]
    print(counter)
    esperar_aleatoriamente()

    numero += counter

print("Total de anuncios en fotocasa:", numero)

# Cerar el driver
driver.quit()