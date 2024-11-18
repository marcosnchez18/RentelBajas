// Función para cargar datos del cliente desde localStorage
function cargarDatosCliente() {
    const clienteSeleccionado = JSON.parse(localStorage.getItem("clienteSeleccionado"));

    if (clienteSeleccionado) {
        // Asignar datos del cliente a los campos del formulario
        document.getElementById("nombre").value = clienteSeleccionado.nombre || "No disponible";
        document.getElementById("dni").value = clienteSeleccionado.dni || "No disponible";
        document.getElementById("email").value = clienteSeleccionado.email || "No disponible";
        document.getElementById("telefonofijo").value = clienteSeleccionado.telefonofijo || "No disponible";
        document.getElementById("telefonomovil").value = clienteSeleccionado.telefonomovil || "No disponible";
        document.getElementById("direccion").value = `${clienteSeleccionado.direccion || "No disponible"}, ${clienteSeleccionado.poblacion || ""}, ${clienteSeleccionado.codpostal || ""}`;
    } else {
        // Redirigir a la página de búsqueda si no hay datos en localStorage
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se encontró información del cliente. Redirigiendo a la búsqueda.",
            confirmButtonText: "Aceptar",
        }).then(() => {
            window.location.href = "/buscar_cliente";
        });
    }
}

// Función para obtener promociones y llenar la lista desplegable
async function obtenerPromociones() {
    try {
        const response = await fetch("http://10.58.6.89:8082/get_mobile_phones_promotions", {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Error al obtener promociones");
        }

        const data = await response.json();
        const promocionesList = document.getElementById("promocionesList");

        // Vaciar la lista antes de llenarla
        promocionesList.innerHTML = "<option value=''>Selecciona una promoción</option>";

        if (data.datas_article && data.datas_article.length > 0) {
            data.datas_article.forEach((articulo) => {
                const option = document.createElement("option");
                option.value = articulo.descripcion;
                option.textContent = articulo.descripcion;
                promocionesList.appendChild(option);
            });
        } else {
            promocionesList.innerHTML = "<option value=''>No hay promociones disponibles</option>";
        }
    } catch (error) {
        console.error("Error al cargar promociones:", error);
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se pudieron cargar las promociones.",
            confirmButtonText: "Aceptar",
        });
    }
}

// Evento inicial: cargar datos del cliente y las promociones al cargar la página
document.addEventListener("DOMContentLoaded", () => {
    cargarDatosCliente();
    obtenerPromociones();
});
