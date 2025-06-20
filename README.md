# SAT Downloader

Esta herramienta proporciona un ejemplo sencillo para automatizar la descarga masiva de facturas CFDI desde los servicios web del SAT. Incluye una interfaz gráfica muy básica desarrollada en Python para usuarios que no tienen conocimientos de programación.

**Aviso**: Los endpoints reales del SAT no se incluyen en este código. Deberás reemplazar las URL de `sat_api.py` con las direcciones correctas proporcionadas por el SAT. Además, este repositorio se ofrece con fines educativos y podría requerir ajustes adicionales para funcionar en producción.

## Requisitos

- Python 3.12 o superior
- Paquetes indicados en `requirements.txt`
- Certificados vigentes (.cer y .key) y contraseña de la FIEL

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## Uso rápido

Ejecuta la interfaz gráfica con:

```bash
python -m sat_downloader.gui
```

1. Ingresa tu RFC.
2. Selecciona los archivos `.cer` y `.key`.
3. Ingresa la contraseña de la llave.
4. Especifica el rango de fechas (por ejemplo, 2019-01-01 a 2025-12-31).
5. Elige el directorio de salida para guardar las facturas.
6. Presiona **Iniciar descarga**.

La aplicación intentará autenticarte y descargar los paquetes disponibles de manera secuencial, mostrando el progreso.

## Advertencia

Debido a las restricciones de acceso a los dominios del SAT en este entorno, no fue posible realizar pruebas de conexión con los servicios reales. Asegúrate de contar con acceso a internet y con las URLs oficiales antes de ejecutar en un entorno de producción.
