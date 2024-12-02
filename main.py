from fastapi import FastAPI, Request, Form,  HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from correo import enviar_correo_confirmacion, generar_enlace, verificar_token
import mariadb
import json
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import pytz
from datetime import datetime
import httpx

# Configuración de la base de datos
DB_CONFIG = {
    "user": "bajas",
    "password": "bajas",
    "host": "localhost",
    "port": 3306,
    "database": "bajas"
}

app = FastAPI()

# Almacena los datos seleccionados por el cliente en un diccionario temporal
datos_seleccionados = {}

# Carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Plantillas
templates = Jinja2Templates(directory="templates")




def insertar_en_bbdd(datos):
    """Inserta los datos del cliente en la tabla `bajas`."""
    try:
        connection = mariadb.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        INSERT INTO bajas (id_cliente, email, lineas_moviles, servicios_adicionales, fecha_baja) 
        VALUES (?, ?, ?, ?, NOW())
        """
        cursor.execute(
            query,
            (
                datos["id_cliente"],
                datos["email"],
                datos.get("lineas_moviles", ""),
                datos.get("servicios_adicionales", "")
            ),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except mariadb.Error as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
async def mostrar_busqueda(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})



@app.get("/cliente_formulario", response_class=HTMLResponse)
async def mostrar_cliente_formulario(request: Request, id: int):
    return templates.TemplateResponse("cliente_formulario.html", {"request": request, "id": id})


@app.post("/confirmar_baja")
async def confirmar_baja(request: Request):
    data = await request.json()
    email_cliente = data.get("email")
    productos = data.get("productos", [])  # Lista de objetos JSON
    cuenta_id = str(data.get("cuenta_id"))
    nombre_cliente = data.get("nombre")
    direccion_cliente = data.get("direccion")
    telefono_cliente = data.get("telefono")

    if not email_cliente or not productos or not cuenta_id:
        raise HTTPException(status_code=400, detail="Datos incompletos")

    if email_cliente == "No disponible":
        raise HTTPException(status_code=400, detail="Correo no disponible, proporcione el DNI.")

    enlace_confirmacion = generar_enlace(email_cliente, cuenta_id)
    enviar_correo_confirmacion(email_cliente, enlace_confirmacion)

    # Almacenar datos completos en el diccionario temporal
    datos_seleccionados[cuenta_id] = {
        "id_cliente": cuenta_id,
        "email": email_cliente,
        "productos": productos,  # Datos completos
        "nombre": nombre_cliente,
        "direccion": direccion_cliente,
        "telefono": telefono_cliente
    }

    print("Datos seleccionados guardados:", datos_seleccionados)
    return {"message": "Correo de confirmación enviado"}


@app.get("/confirmacion", response_class=HTMLResponse)
async def confirmar_seleccion(request: Request, token: str = Query(...)):
    data = verificar_token(token)
    if not data:
        raise HTTPException(status_code=400, detail="El enlace es inválido o ha expirado.")

    cuenta_id = data.get("cuenta_id")
    datos_cliente = datos_seleccionados.get(cuenta_id)
    if not datos_cliente:
        raise HTTPException(status_code=404, detail="Datos no encontrados")

    # Separar productos en líneas móviles y servicios adicionales
    lineas_moviles = []
    servicios_adicionales = []

    for producto in datos_cliente["productos"]:
        if "DDI" in producto:
            lineas_moviles.append({
                "mostrar": f"Número: {producto['DDI']}\nTarifa: {producto['NomTarifa']}\nPrecio: {producto['PvpCuotaTarifa']}€",
                "original": {"DDI": producto["DDI"], "ID": producto["ID"]}
            })
        else:
            servicios_adicionales.append({
                "mostrar": f"Descripción: {producto['Descripcion']}\nPrecio: {producto.get('Precio', 0)}€",
                "original": {"ID": producto["ID"], "Descripcion": producto["Descripcion"], "Referencia": producto.get("Referencia", "")}
            })

    # Mostrar datos formateados al usuario
    lineas_moviles_formateadas = [item["mostrar"] for item in lineas_moviles]
    servicios_adicionales_formateados = [item["mostrar"] for item in servicios_adicionales]

    return templates.TemplateResponse("confirmacion.html", {
        "request": request,
        "id": cuenta_id,
        "email": datos_cliente["email"],
        "nombre": datos_cliente["nombre"],
        "direccion": datos_cliente["direccion"],
        "telefono": datos_cliente["telefono"],
        "lineas_moviles": lineas_moviles_formateadas,
        "servicios_adicionales": servicios_adicionales_formateados
    })


def verificar_duplicados(id_cliente, lineas_moviles, servicios_adicionales):
    """Verifica si las líneas móviles o servicios adicionales ya existen en la base de datos."""
    try:
        connection = mariadb.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Consultar las líneas móviles existentes
        cursor.execute("""
            SELECT JSON_EXTRACT(lineas_moviles, '$[*].ID') AS ids
            FROM bajas
            WHERE id_cliente = ?
        """, (id_cliente,))
        lineas_existentes = cursor.fetchall()

        # Procesar los resultados de las líneas móviles
        lineas_existentes_ids = set()
        for ids in lineas_existentes:
            if ids[0]:  # Verificar si el resultado no es None
                lineas_existentes_ids.update(json.loads(ids[0]))

        # Consultar los servicios adicionales existentes
        cursor.execute("""
            SELECT JSON_EXTRACT(servicios_adicionales, '$[*].ID') AS ids
            FROM bajas
            WHERE id_cliente = ?
        """, (id_cliente,))
        servicios_existentes = cursor.fetchall()

        # Procesar los resultados de los servicios adicionales
        servicios_existentes_ids = set()
        for ids in servicios_existentes:
            if ids[0]:  # Verificar si el resultado no es None
                servicios_existentes_ids.update(json.loads(ids[0]))

        cursor.close()
        connection.close()

        # Filtrar las nuevas líneas móviles y servicios adicionales
        nuevas_lineas = [linea for linea in lineas_moviles if linea["ID"] not in lineas_existentes_ids]
        nuevos_servicios = [servicio for servicio in servicios_adicionales if servicio["ID"] not in servicios_existentes_ids]

        return nuevas_lineas, nuevos_servicios
    except mariadb.Error as e:
        print(f"Error al verificar duplicados en la base de datos: {e}")
        return lineas_moviles, servicios_adicionales  # En caso de error, continuar sin filtrar



@app.post("/firma_baja")
async def firma_baja(request: Request):
    try:
        # Obtener el payload enviado desde el cliente
        data = await request.json()
        cuenta_id = data.get("id_cliente")

        # Verificar si existen datos previamente seleccionados para la cuenta
        if not cuenta_id or cuenta_id not in datos_seleccionados:
            raise HTTPException(status_code=400, detail="No se encontraron datos seleccionados para esta cuenta.")

        datos_cliente = datos_seleccionados[cuenta_id]

        # Separar y formatear los datos para la base de datos
        lineas_moviles = [
            {"DDI": producto["DDI"], "ID": producto["ID"]}
            for producto in datos_cliente["productos"] if "DDI" in producto
        ]
        servicios_adicionales = [
            {"ID": producto["ID"], "Descripcion": producto["Descripcion"], "Referencia": producto.get("Referencia", "")}
            for producto in datos_cliente["productos"] if "DDI" not in producto
        ]

        # Verificar duplicados
        nuevas_lineas, nuevos_servicios = verificar_duplicados(cuenta_id, lineas_moviles, servicios_adicionales)

        if not nuevas_lineas and not nuevos_servicios:
            return {"message": "Ya has confirmado la baja de tus productos."}

        # Preparar los datos para insertar en la base de datos
        datos_a_insertar = {
            "id_cliente": cuenta_id,
            "email": datos_cliente["email"],
            "lineas_moviles": json.dumps(nuevas_lineas),  # Convertir a JSON para almacenar
            "servicios_adicionales": json.dumps(nuevos_servicios),  # Convertir a JSON para almacenar
            "estado": "pendiente"

            
        }
        
        #CUANDO CREEMOS LA BBDD SE INSERTA ESTO:
        #ALTER TABLE bajas
        #ADD COLUMN estado ENUM('pendiente', 'completada') NOT NULL DEFAULT 'pendiente';


        # Insertar en la base de datos
        if insertar_en_bbdd(datos_a_insertar):
            return {"message": "Baja confirmada correctamente."}
        else:
            raise HTTPException(status_code=500, detail="Error al guardar los datos en la base de datos.")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Faltan datos clave: {str(e)}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar datos JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")




def convertir_a_hora_espana(fecha_utc):
    zona_horaria_espana = pytz.timezone('Europe/Madrid')
    fecha_utc = fecha_utc.replace(tzinfo=pytz.utc)  # Asegurarse de que la fecha está en UTC
    fecha_espana = fecha_utc.astimezone(zona_horaria_espana)  # Convertir a hora española
    return fecha_espana

import requests
from fastapi import HTTPException

def obtener_datos_cliente(id_cliente: int):
    # URL de la API externa
    api_url = "http://10.58.6.92:8082/get_data_client_baja_for_dni"
    
    # Datos que se envían en la solicitud POST
    payload = {"id_cliente": id_cliente}
    
    try:
        # Realizamos la solicitud POST a la API externa
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Esto lanzará un error si la respuesta no es 200 OK
        return response.json()[0]  # Asumimos que la API devuelve un solo objeto dentro de una lista
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los datos del cliente: {e}")
        return None

# Ruta para obtener las bajas
@app.get("/bajas", response_class=HTMLResponse)
async def obtener_bajas(
    request: Request,
    fecha_inicio: str = Query(None), 
    fecha_fin: str = Query(None),  
    estado: str = Query(None)
):
    try:
        # Conectar a la base de datos
        connection = mariadb.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Construcción de la consulta base
        query = "SELECT * FROM bajas WHERE 1=1"
        params = []

        # Filtrar por fecha de baja
        if fecha_inicio:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_inicio_dt_espana = pytz.timezone('Europe/Madrid').localize(fecha_inicio_dt)
            query += " AND fecha_baja >= ?"
            params.append(fecha_inicio_dt_espana)

        if fecha_fin:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            fecha_fin_dt_espana = pytz.timezone('Europe/Madrid').localize(fecha_fin_dt)
            query += " AND fecha_baja <= ?"
            params.append(fecha_fin_dt_espana)

        # Filtrar por estado
        if estado:
            query += " AND estado = ?"
            params.append(estado)

        # Ejecutar la consulta SQL
        cursor.execute(query, params)
        bajas = cursor.fetchall()

        # Obtener los datos del cliente de la API externa para cada baja
        bajas_con_info_cliente = []
        for baja in bajas:
            id_cliente = baja[1]  # Asumiendo que el ID del cliente está en la columna 1
            datos_cliente = obtener_datos_cliente(id_cliente)
            if datos_cliente:
                baja_con_info = {
                    "id": baja[0],
                    "id_cliente": baja[1],
                    "lineas_moviles": baja[2],
                    "servicios_adicionales": baja[3],
                    "fecha_baja": baja[4],
                    "email": baja[5],
                    "estado": baja[6],
                    "nombre_cliente": datos_cliente["nombre"],
                    "dni_cliente": datos_cliente["dni"],
                    "telefono_movil": datos_cliente["telefonomovil"],
                    "direccion": datos_cliente["direccion"]
                }
                bajas_con_info_cliente.append(baja_con_info)

        # Cerrar la conexión a la base de datos
        cursor.close()
        connection.close()

        # Renderizar la plantilla HTML con los datos de las bajas y los clientes
        return templates.TemplateResponse("bajas.html", {
            "request": request,
            "bajas": bajas_con_info_cliente
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las bajas: {str(e)}")
 
        
@app.post("/actualizar_estado/")
async def actualizar_estado(id_baja: str = Form(...), estado: str = Form(...)):
    try:
        # Conectar a la base de datos
        connection = mariadb.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Consulta SQL para actualizar el estado
        query = "UPDATE bajas SET estado = ? WHERE id = ?"
        cursor.execute(query, (estado, id_baja))

        # Confirmar los cambios
        connection.commit()

        # Cerrar la conexión
        cursor.close()
        connection.close()

        # Redirigir con un parámetro de éxito
        return RedirectResponse(url="/bajas?actualizado=true", status_code=303)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el estado: {str(e)}")





