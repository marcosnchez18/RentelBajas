from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from correo import enviar_correo_confirmacion, generar_enlace, verificar_token

app = FastAPI()

# Almacena los datos seleccionados por el cliente en un diccionario temporal
datos_seleccionados = {}

# Carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Plantillas
templates = Jinja2Templates(directory="templates")

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
    productos = data.get("productos", [])
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

    # Guardar datos del cliente y productos seleccionados
    datos_seleccionados[cuenta_id] = {
        "email": email_cliente,
        "productos": productos,
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

    return templates.TemplateResponse("confirmacion.html", {
        "request": request,
        "id": cuenta_id,
        "email": datos_cliente["email"],
        "nombre": datos_cliente["nombre"],
        "direccion": datos_cliente["direccion"],
        "telefono": datos_cliente["telefono"],
        "productos": datos_cliente["productos"]
    })


@app.get("/promociones", response_class=HTMLResponse)
async def mostrar_promociones(request: Request):
    return templates.TemplateResponse("search_datos.html", {"request": request})

@app.get("/cliente_promociones", response_class=HTMLResponse)
async def cliente_promociones(request: Request, id: int):
    return templates.TemplateResponse("cliente_promociones.html", {"request": request, "id": id})


@app.get("/get_mobile_phones_promotions")
async def obtener_promociones():
    # Simulación de datos de ejemplo
    promociones = {
        "datas_article": [
            {"descripcion": "Equipo USB SMC con Conector"},
            {"descripcion": "Antena"},
            {"descripcion": "Cambio USB por AP integrado"},
            {"descripcion": "AP Conceptronic integrado + POE"},
            {"descripcion": "Concepto Fianza equipo (smc+antena)"}
        ]
    }
    return promociones
