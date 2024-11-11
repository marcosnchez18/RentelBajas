import requests


url = "http://10.58.6.89:8082/cliente/111171/products"

try:
  
    response = requests.get(url)
    
   
    if response.status_code == 200:
      
        data = response.json()
        print("Datos recibidos de la API:")
        print(data)
    else:
        print(f"Error en la solicitud: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Error al conectar con la API: {e}")
