import requests


url = "http://10.58.6.92:8082/get_data_client_baja_for_dni"


dni = "52322185z"  


data = {
    "dni": dni
}


response = requests.post(url, json=data)


if response.status_code == 200:
    
    datos_cliente = response.json()
    print(datos_cliente)
else:
    print(f"Error en la petición: {response.status_code}")
