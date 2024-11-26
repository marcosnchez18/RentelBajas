const urlParams = new URLSearchParams(window.location.search);
const cuentaID = urlParams.get('id');

// Cargar datos para mostrar al cliente
async function cargarDatosConfirmacion() {
    try {
        const response = await fetch(`/api/confirmacion_datos?id=${cuentaID}`);
        const data = await response.json();

        if (data.error) {
            document.getElementById("clienteInfo").innerHTML = "<p class='text-red-500'>Error: No se encontraron los datos del cliente.</p>";
            return;
        }

        document.getElementById("nombre").textContent = data.nombre;
        document.getElementById("dni").textContent = data.dni;
        document.getElementById("email").textContent = data.email;
        document.getElementById("telefonofijo").textContent = data.telefonofijo;
        document.getElementById("telefonomovil").textContent = data.telefonomovil;
        document.getElementById("direccion").textContent = `${data.direccion}, ${data.poblacion}, ${data.codpostal}`;
        document.getElementById("confirmarBajaBtn").addEventListener("click", confirmarBaja)

        // Mostrar productos seleccionados
        const productosList = document.getElementById("productosList");
        data.productos.forEach((producto) => {
            const li = document.createElement("li");
            li.textContent = producto;
            productosList.appendChild(li);
        });

    } catch (error) {
        console.error("Error al cargar datos:", error);
    }
}

// Función para confirmar baja e insertar en la tabla `bajas`
async function confirmarBaja() {
    const email = document.getElementById("email").textContent;
    const nombre = document.getElementById("nombre").textContent;

    // Simular datos seleccionados por el cliente
    const productosSeleccionados = [
        { tipo: "lineas_moviles", items: ["Movil 1", "Movil 2"] },
        { tipo: "servicios_adicionales", items: ["Servicio 1"] },
        { tipo: "internet", items: ["Fibra"] },
        { tipo: "fijos", items: ["Fijo 1"] }
    ];

    const payload = {
        id_cliente: cuentaID,
        lineas_moviles: productosSeleccionados.find(p => p.tipo === "lineas_moviles")?.items || [],
        servicios_adicionales: productosSeleccionados.find(p => p.tipo === "servicios_adicionales")?.items || [],
        internet: productosSeleccionados.find(p => p.tipo === "internet")?.items || [],
        fijos: productosSeleccionados.find(p => p.tipo === "fijos")?.items || [],
        fecha_baja: new Date().toISOString()
    };

    try {
        const response = await fetch('/api/registrar_baja', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Baja confirmada y registrada con éxito.");
        } else {
            const errorData = await response.json();
            alert(`Error al registrar la baja: ${errorData.detail}`);
        }
    } catch (error) {
        console.error("Error al confirmar baja:", error);
    }
}

// Función para rechazar baja
function rechazarBaja() {
    alert("Baja rechazada (en desarrollo)");
}

// Inicializar carga de datos
cargarDatosConfirmacion();
