import requests

# Cambia esto al endpoint real de la API
url = 'https://ejemploapi.com/endpoint'

# Ruta local de tu imagen
image_path = 'ruta/a/tu/imagen.jpg'

# Leer y enviar la imagen
with open(image_path, 'rb') as image_file:
    files = {'file': image_file}
    response = requests.post(url, files=files)

# Mostrar la respuesta de la API
print('Código de estado:', response.status_code)
print('Respuesta:', response.text)
