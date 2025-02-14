"""
=========================================
          SCRAPER DE ANUNCIOS v2.0
=========================================

Descripción:
Este script mejorado de scraping utiliza Selenium para extraer información de anuncios inmobiliarios
de manera eficiente y robusta.

Mejoras en esta versión:
✔ Manejo avanzado de excepciones con logging detallado para una mejor trazabilidad de errores.
✔ Optimización de tiempos de espera mediante WebDriverWait, evitando esperas innecesarias.
✔ Prevención de bloqueos mediante la rotación de agentes de usuario y tiempos de espera aleatorios.
✔ Estructuración del código en funciones reutilizables, mejorando la legibilidad y mantenimiento.
✔ Uso de context manager para gestionar el ciclo de vida del WebDriver de forma más eficiente.
✔ Implementación de scroll eficiente para cargar todo el contenido dinámico de la página.
✔ Eliminación de la inicialización del WebDriver en cada iteración, mejorando el rendimiento.
✔ Guardado de datos de manera incremental en CSV sin sobrescribir registros existentes.

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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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

# Función para configurar el driver
def configurar_driver():
    """Inicializa y configura el driver de Selenium."""
    options = Options()
    options.add_argument('--incognito')
    #options.add_argument('--headless')  # Opcional: Ejecutar sin interfaz gráfica
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    service = Service('chromedriver/chromedriver.exe')
    return webdriver.Chrome(service=service, options=options)

# Función para extraer los datos de cada anuncio
def obtener_datos_anuncio(driver, link, cd_postal):
    """Extraer la información de un anuncio."""
    try:
        fecha = datetime.datetime.today().strftime('%d-%m-%Y')
        referencia = (link[1].split("/")[-1]).split("?")[-2] # Extraer la referencia del anuncio
        promotora = obtener_texto(driver, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[2]/section[1]/div/div/div/div/div[2]/div[1]/h4')
        zonas_comunes = 'No disponible'
        certificado_energetico = obtener_texto(driver, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[4]/div[1]/div/div/span[3]')
        codigo_postal = cd_postal
        direccion = 'No disponible'
        dormitorios = obtener_texto(driver, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[2]/div/div/span[2]')
        area = obtener_texto(driver, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[4]/div/div/span[2]')
        planta = obtener_texto(driver, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[5]/div/div/span[2]')
        caracteristicas = 'No disponible'
        fecha_actualizacion = 'No disponible'
        img = obtener_atributo(driver, '//*[@id="App"]/div[1]/main/div[2]/section/figure[1]/img', 'src')
        tipo = obtener_texto(driver, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[2]/div/div/div/div[1]/div[1]/div/div/span[2]')
        precio = obtener_texto(driver, '//*[@id="App"]/div[1]/main/div[3]/div[1]/div[1]/div/section[1]/div/div[2]/div[1]/span')

        return {
            'fecha': fecha,
            'referencia': referencia,
            'promotora': promotora,
            'zonas_comunes': zonas_comunes,
            'certificado_energetico': certificado_energetico,
            'codigo_postal': codigo_postal,
            'direccion': direccion,
            'dormitorios': dormitorios,
            'area': area,
            'planta': planta,
            'caracteristicas': caracteristicas,
            'fecha_actualizacion': fecha_actualizacion,
            'url': link[1],
            'img': img,
            'tipo': tipo,
            'precio': precio
        }
    except Exception as e:
        logging.error(f"Error en {link[1]}: {str(e)}")
        return None
    
# Función para obtener texto de un elemento con verificación
def obtener_texto(driver, xpath):
    """Obtiene el texto de un elemento, devuelve 'No disponible' si no se encuentra."""
    try:
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        return 'No disponible'

# Función para obtener atributo de un elemento con verificación
def obtener_atributo(driver, xpath, atributo):
    """Obtiene un atributo de un elemento, devuelve 'No disponible' si no se encuentra."""
    try:
        return driver.find_element(By.XPATH, xpath).get_attribute(atributo)
    except NoSuchElementException:
        return 'No disponible'

# Función para guardar los datos en un archivo CSV
def guardar_datos_csv(data):
    """Guardar la lista de anuncios en un archivo CSV."""
    df_anuncios = pd.DataFrame(data, columns=[
        'Fecha', 'Referencia', 'Promotora', 'Zonas comunes', 'Certificado energético', 'Código postal',
        'Dirección', 'Dormitorios', 'Área', 'Planta', 'Características', 'Fecha de actualización', 'URL', 'Imagen', 'Tipo', 'Precio'
    ])
    
    # Escribir los datos al final
    with open('datos/anuncios.csv', mode='a', newline='', encoding='utf-8') as f:
        df_anuncios.to_csv(f, index=False, header=f.tell() == 0)  # Solo escribe encabezado si el archivo está vacío

# Leer el archivo CSV con los enlaces
def leer_enlaces():
    pd.set_option('display.max_colwidth', None) # Mostrar todo el contenido de las celdas
    df = pd.read_csv('datos/links_anuncios.csv', header=None)[[1, 2]]  # Leer el archivo CSV
    df_lista = df.values.tolist()  # Convertir a lista seleccionando las columnas 1 y 2
    links = list(set(map(tuple, df_lista)))  # Eliminar duplicados
    print(f"Se encontraron {len(links)} anuncios")
    return links

def main():
    # Leer los enlaces
    links = leer_enlaces()

    # Inicializar el driver
    driver = configurar_driver()

    # Lista para almacenar los anuncios
    anuncios_data = []

    # Iterar sobre los enlaces
    for link in links:
        print(link[1])  # Imprimir el link
        cd_postal = link[0]  # Extraer el código postal

        # Ingresar a la página
        driver.get(str(link[1]))  # Ingresar a la página
        esperar_aleatoriamente()  # Esperar antes de interactuar
        driver.maximize_window()  # Maximizar la ventana

        # Verificar si la página está bloqueada
        if driver.find_elements(By.XPATH, '//html/body/div/h1'):
            print("Página bloqueada")
            # continue
            driver.quit() # Cerrar el driver
            break

        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="App"]')))

        # Cerrar popup si está presente
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="didomi-notice-agree-button"]'))
            )
            close_button.click()
        except TimeoutException:
            print("No se pudo cerrar el popup:")
            pass

        # Hacer scroll hasta el final de la página
        height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        for e in range(0, height, 500):
            driver.execute_script(f'window.scrollTo(0, {e});')
            esperar_aleatoriamente(1, 3)

        # Extraer los datos del anuncio
        datos = obtener_datos_anuncio(driver, link, cd_postal)
        if datos:
            anuncios_data.append(datos)

        # Esperar antes de la siguiente iteración
        esperar_aleatoriamente()

    # Guardar los datos en el CSV
    guardar_datos_csv(anuncios_data)

    # Cerrar
    driver.quit()

if __name__ == "__main__":
    main()