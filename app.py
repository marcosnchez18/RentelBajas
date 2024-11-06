import requests

# URL de la API
url = "http://10.58.6.89:8082/cliente/103728/products"

try:
    # Realiza la solicitud GET a la API
    response = requests.get(url)
    
    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        # Procesa la respuesta JSON
        data = response.json()
        print("Datos recibidos de la API:")
        print(data)
    else:
        print(f"Error en la solicitud: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Error al conectar con la API: {e}")
