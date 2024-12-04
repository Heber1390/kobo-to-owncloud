import requests
import os
import owncloud

# Configuración de KoboToolbox
KOBO_TOKEN = "b6c5e2ea0d8ec5e5db07bf2fc9b54b1908ce0769"
KOBO_API_URL = "https://kf.kobotoolbox.org/api/v2/assets/aACAht8Q9hWjDBBL6yGZcw/data/?format=json"

# Configuración de OwnCloud
OWNCLOUD_URL = "http://archivogeneral.redsolidaria.gob.hn/owncloud"
OWNCLOUD_USERNAME = "hrivera"
OWNCLOUD_PASSWORD = "@Admin123"
OWNCLOUD_FOLDER = "/Contraloria/6. Actas Huelladas/"

# Carpeta para guardar las imágenes temporalmente
TEMP_FOLDER = "temp_images"
os.makedirs(TEMP_FOLDER, exist_ok=True)

def descargar_imagenes():
    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    response = requests.get(KOBO_API_URL, headers=headers)

    # Verificar respuesta de la API
    print(f"Código de estado: {response.status_code}")
    if response.status_code != 200:
        print("Error al acceder a la API. Verifica el token o la URL.")
        print(f"Respuesta: {response.text}")
        return

    try:
        data = response.json()
    except ValueError as e:
        print("Error al interpretar la respuesta como JSON:")
        print(e)
        print("Contenido completo de la respuesta:")
        print(response.text)
        return

    # Procesar resultados e intentar descargar imágenes
    for record in data.get("results", []):
        identidad = record.get("Identidad")  # Obtener el valor de 'Identidad'
        if not identidad:
            print("El campo 'Identidad' no está presente en el registro. Se omite este registro.")
            continue

        if "_attachments" in record:
            for attachment in record["_attachments"]:
                download_url = attachment.get("download_url")
                if not download_url:
                    print("URL de descarga no encontrada en el adjunto.")
                    continue

                # Construir el nombre del archivo con el campo 'Identidad'
                filename = f"{identidad}.jpg"
                file_path = os.path.join(TEMP_FOLDER, filename)

                # Quitar "?format=json" de la URL si está presente
                if "?format=json" in download_url:
                    download_url = download_url.replace("?format=json", "")

                print(f"Descargando {filename} desde {download_url}...")
                try:
                    img_response = requests.get(download_url, headers=headers)
                    if img_response.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"Imagen guardada en {file_path}")
                    else:
                        print(f"Error al descargar {filename}: {img_response.status_code}")
                        print(f"Respuesta: {img_response.text}")
                except requests.RequestException as e:
                    print(f"Error de red al intentar descargar {filename}: {e}")

def subir_a_owncloud():
    try:
        oc = owncloud.Client(OWNCLOUD_URL)
        oc.login(OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD)

        for filename in os.listdir(TEMP_FOLDER):
            # Validar que el nombre del archivo sea numérico (es un número de identidad)
            if filename.split(".")[0].isdigit():
                file_path = os.path.join(TEMP_FOLDER, filename)
                print(f"Subiendo {file_path} a OwnCloud...")
                oc.put_file(OWNCLOUD_FOLDER + filename, file_path)
                print(f"Archivo {filename} subido con éxito.")
            else:
                print(f"Omitiendo {filename} porque no corresponde a un número de identidad.")

        oc.logout()
    except Exception as e:
        print(f"Error al subir archivos a OwnCloud: {e}")

# Ejecutar todo el proceso
descargar_imagenes()
subir_a_owncloud()
