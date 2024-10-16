# funciones.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

# Ruta para buscar clientes por DNI
@app.get("/buscar_cliente")
async def buscar_cliente(dni: str):
    # URL de la API externa
    api_url = "http://10.58.6.92:8082/get_data_client_for_dni"

    try:
        # Hacer la petición a la API externa
        response = requests.get(api_url, params={"dni": dni})
        response.raise_for_status()

        # Convertir la respuesta en JSON y manejar errores de formato
        try:
            data = response.json()
            
        except ValueError:
            raise HTTPException(status_code=500, detail="La respuesta de la API externa no es JSON válido")

        # Retornar los datos al frontend
        return JSONResponse(content=data)

    except requests.exceptions.RequestException as e:
        # Opcional: registra el error en la consola
        print(f"Error al comunicarse con la API externa: {e}")
        raise HTTPException(status_code=500, detail="Error al comunicarse con la API externa")
