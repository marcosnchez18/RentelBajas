import requests

# URL de la API
url = "http://10.58.6.89:8082/get_data_client_for_dni"

# DNI que quieres buscar
dni = "49035874N"  # Reemplaza esto con el DNI que deseas buscar

# Datos a enviar en el cuerpo de la petición POST
data = {
    "dni": dni
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
