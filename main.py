from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from correo import enviar_correo_confirmacion

app = FastAPI()

# Diccionario para almacenar datos temporalmente
datos_seleccionados = {}

# Configuración de rutas
app.mount("/static", StaticFiles(directory="static"), name="static")
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

    # Datos adicionales del cliente
    nombre_cliente = data.get("nombre")
    direccion_cliente = data.get("direccion")
    telefono_cliente = data.get("telefono")

    if not email_cliente or not productos or not cuenta_id:
        raise HTTPException(status_code=400, detail="Datos incompletos")

    enlace_confirmacion = f"http://localhost:8000/confirmacion?id={cuenta_id}"
    enviar_correo_confirmacion(email_cliente, enlace_confirmacion)

    # Guardar todos los datos del cliente y productos seleccionados
    datos_seleccionados[cuenta_id] = {
        "email": email_cliente,
        "productos": productos,
        "nombre": nombre_cliente,
        "direccion": direccion_cliente,
        "telefono": telefono_cliente
    }

    print("Datos seleccionados guardados:", datos_seleccionados)  # Debug
    return {"message": "Correo de confirmación enviado"}

@app.get("/confirmacion", response_class=HTMLResponse)
async def confirmar_seleccion(request: Request, id: str):
    datos_cliente = datos_seleccionados.get(id)
    if not datos_cliente:
        raise HTTPException(status_code=404, detail="Datos no encontrados")

    return templates.TemplateResponse("confirmacion.html", {
        "request": request,
        "id": id,
        "email": datos_cliente["email"],
        "nombre": datos_cliente["nombre"],
        "direccion": datos_cliente["direccion"],
        "telefono": datos_cliente["telefono"],
        "productos": datos_cliente["productos"]
    })
