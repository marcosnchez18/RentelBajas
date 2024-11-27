from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from correo import enviar_correo_confirmacion, generar_enlace, verificar_token
import mariadb
import json

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
            "servicios_adicionales": json.dumps(nuevos_servicios)  # Convertir a JSON para almacenar
        }

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
