# InmoScraper

## Descripción
Este proyecto proporciona un **scraper automatizado** para extraer información detallada de anuncios inmobiliarios desde sitios web. Utiliza **Selenium** para navegar por las páginas de los anuncios, recopilar datos clave y guardarlos en un archivo CSV. El scraper está diseñado para trabajar de manera eficiente y evitar bloqueos mediante el uso de agentes de usuario rotativos, tiempos de espera aleatorios y un manejo robusto de errores.

### Información extraída
El scraper obtiene la siguiente información de cada anuncio inmobiliario:
- Fecha de captura
- Referencia del anuncio
- Nombre de la promotora
- Zonas comunes
- Certificado energético
- Código postal
- Dirección
- Número de dormitorios
- Área de la propiedad
- Planta
- Características adicionales
- Fecha de actualización
- URL
- Imagen de la propiedad
- Tipo de propiedad (e.g., apartamento, casa)
- Precio

## Mejoras en la versión v2
Esta versión del scraper ha sido mejorada con respecto a la anterior para optimizar su rendimiento y robustez. Algunas de las principales mejoras son:

- **Manejo avanzado de excepciones** con logging detallado para una mejor trazabilidad de errores.
- **Optimización de tiempos de espera** utilizando `WebDriverWait`, lo que mejora la eficiencia y reduce los tiempos de espera innecesarios.
- **Prevención de bloqueos** mediante la rotación de agentes de usuario y la implementación de tiempos de espera aleatorios entre solicitudes.
- **Código más modular** y estructurado en funciones reutilizables para facilitar el mantenimiento y la extensión del script.
- **Mejor gestión del ciclo de vida del WebDriver** mediante el uso de un context manager, lo que asegura una inicialización y cierre adecuados del navegador.

## Requisitos
- Python 3.x
- Selenium
- Pandas
- ChromeDriver

### Instalación
1. Clona este repositorio en tu máquina local:
        git clone https://github.com/pcanadas/InmoScraper.git

2. Instala las dependencias necesarias:
        pip install -r requirements.txt

3. Descarga ChromeDriver y asegúrate de que sea compatible con la versión de Chrome que tienes instalada.

### Mecanismos anti-bloqueo
Este scraper implementa varias estrategias para evitar ser detectado como un bot:

- Rotación de agentes de usuario: Utiliza diferentes agentes de usuario para simular múltiples navegadores.
- Tiempos de espera aleatorios: Introduce un retraso aleatorio entre las solicitudes para reducir la probabilidad de bloqueo.
- Scroll automático: Realiza un desplazamiento (scroll) por la página para cargar contenido dinámico.



