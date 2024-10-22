import requests

# URL de la API
url = "http://10.58.6.89:8082/get_data_client_for_name"  # Asegúrate de que esta ruta sea la correcta para buscar por nombre

# Nombre del cliente que quieres buscar
nombre = "Manuel Jesus Vazquez Gonzalez"  # Reemplaza esto con el nombre del cliente que deseas buscar

# Datos a enviar en el cuerpo de la petición POST
data = {
    "nombre": nombre  # Cambiamos "dni" por "nombre"
}

# Haciendo la petición POST a la API
response = requests.post(url, json=data)

# Comprobando si la petición fue exitosa
if response.status_code == 200:
    # Procesar la respuesta JSON
    datos_cliente = response.json()
    print(datos_cliente)
else:
    print(f"Error en la petición: {response.status_code}")
