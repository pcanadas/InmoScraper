"""
=========================================
          SCRAPER DE ANUNCIOS
=========================================

Descripción:
Este script utiliza Selenium para realizar web scraping en una página de anuncios inmobiliarios.  
Extrae información relevante sobre cada anuncio y la guarda en un archivo CSV.

Flujo de trabajo:
1. Carga una lista de enlaces de anuncios desde un archivo CSV.
2. Para cada enlace:
   - Abre el navegador en modo incógnito con un agente de usuario aleatorio.
   - Accede a la página del anuncio y espera su carga.
   - Verifica si la página está bloqueada y, de ser así, detiene la ejecución.
   - Extrae datos clave del anuncio (promotora, precio, superficie, número de habitaciones, etc.).
   - Almacena los datos extraídos en un archivo CSV.
   - Cierra el navegador y pasa al siguiente anuncio.

Mecanismos anti-bloqueo:
✔ Uso de un tiempo de espera aleatorio entre solicitudes.
✔ Rotación de agentes de usuario.
✔ Scroll automático para cargar contenido dinámico.

Salida:
Los datos extraídos se guardan en 'datos/anuncios.csv', agregando nuevos registros sin sobrescribir los existentes.

Uso:
Este script es útil para recopilar información detallada de los anuncios de Fotocasa de manera automatizada, asegurando una navegación más segura y evitando bloqueos.
=========================================
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import datetime
import random
import pandas as pd
import logging

# Configurar logging
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para evitar bloqueos
def esperar_aleatoriamente(min_seg=5, max_seg=15):
    tiempo = random.uniform(min_seg, max_seg) # Tiempo aleatorio entre min_seg y max_seg segundos, utilizamos uniform que permite intervalos con decimales
    sleep(tiempo)

# Leer el archivo csv
pd.set_option('display.max_colwidth', None)
df = pd.read_csv('datos/links_anuncios.csv', header=None)[[1, 2]] # Leer el archivo csv
df_lista = df.values.tolist() # Convertir a lista seleccionando las columnas 1 y 2
links = [] # Lista de links
for item in df_lista: # Recorrer la lista
    if item not in links: # Si el item no está en la lista de links
        links.append(item) # Agregar a la lista de links

print(f"Se encontraron {len(links)} anuncios")
print(links)

for link in links:
    print(link[1]) # Imprimir el link
    cd_postal = link[0] # Extraer el código postal
    print(cd_postal) # Imprimir el código postal
    
    # Inicializar el driver
    options = Options()
    options.add_argument('--incognito')
    #options.add_argument('--headless')  # Opcional: Ejecutar sin interfaz gráfica
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
    esperar_aleatoriamente(1, 5)  # Esperar antes de interactuar

    # Ingresar a la pagina
    driver.get(str(link[1])) # Ingresar a la pagina
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


    # Hacer scroll hasta el final de la pagina
    height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
    for e in range(0, height, 700):
        driver.execute_script('window.scrollTo(0, {});'.format(e))
        esperar_aleatoriamente(1, 5)  # Esperar antes de seguir

    try:
        fecha = datetime.datetime.today().strftime('%d-%m-%Y')
        referencia = (link[1].split("/")[-1]).split("?")[-2] # Extraemos la referencia
        promotora = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[2]/section[1]/div/div/div/div/div[2]/div[1]/h4').text if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[2]/section[1]/div/div/div/div/div[2]/div[1]/h4') else 'No disponible'
        zonas_comunes = 'No disponible'
        certificado_energetico = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[4]/div[1]/div/div/span[3]').text if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[4]/div[1]/div/div/span[3]') else 'No disponible'
        codigo_postal = cd_postal
        direccion = 'No disponible'
        dormitorios = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[2]/div/div/span[2]').text if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[2]/div/div/span[2]') else 'No disponible'
        area = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[4]/div/div/span[2]').text if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[4]/div/div/span[2]') else 'No disponible'
        planta = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[5]/div/div/span[2]').text if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[5]/div/div/span[2]') else 'No disponible'
        caracteristicas = 'No disponible'
        fecha_actualizacion = 'No disponible'
        url = link
        img = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[2]/section/figure[1]/img').get_attribute('src') if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[2]/section/figure[1]/img') else 'No disponible'
        tipo = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[1]/div/div/span[2]').text if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[1]/div/div/span[2]') else 'No disponible'
        precio = driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[1]/div/div[2]/div[1]/span').text if driver.find_element(By.XPATH, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[1]/div/div[2]/div[1]/span') else 'No disponible'
        print(fecha, referencia, promotora, zonas_comunes, certificado_energetico, codigo_postal, direccion, dormitorios, area, planta, caracteristicas, fecha_actualizacion, url, img, tipo, precio)
    except Exception as e:
        logging.error(f"Error en {link[1]}: {str(e)}")
        print("No se pudo obtener la información:", e)

    esperar_aleatoriamente()  # Esperar antes de interactuar

    # Guardar los datos en un archivo csv
    anuncios = pd.DataFrame([[
        fecha, referencia, promotora, zonas_comunes, certificado_energetico, codigo_postal, direccion, dormitorios, area, planta, caracteristicas, fecha_actualizacion, url, img, tipo, precio]], 
        columns=['Fecha', 'Referencia', 'Promotora', 'Zonas comunes', 'Certificado energético', 'Código postal', 'Dirección', 'Dormitorios', 'Área', 'Planta', 'Características', 'Fecha de actualización', 'URL', 'Imagen', 'Tipo', 'Precio'])
    
    with open('datos/anuncios.csv', mode='a', newline='', encoding='utf-8') as f:
        anuncios.to_csv(f, index=False, header=f.tell()==0)  # Solo escribe encabezado si el archivo está vacío

    # Cerrar el driver
    driver.quit()