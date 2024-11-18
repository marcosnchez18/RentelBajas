document.getElementById("searchForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const searchType = document.getElementById("searchType").value;
    const searchValue = document.getElementById("searchValue").value;
    const errorDiv = document.getElementById("error");
    const clienteDataDiv = document.getElementById("clienteData");

    errorDiv.classList.add("hidden");
    clienteDataDiv.classList.add("hidden");

    try {
        const response = await fetch("http://10.58.6.89:8082/get_data_client_name_dni", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ [searchType]: searchValue }),
        });

        if (!response.ok) throw new Error("Error en la respuesta del servidor");

        const data = await response.json();

        if (!data.datas_clientes || data.datas_clientes.length === 0) {
            errorDiv.textContent = "No se encontraron datos para la búsqueda proporcionada.";
            errorDiv.classList.remove("hidden");
        } else {
            clienteDataDiv.classList.remove("hidden");
            mostrarClientes(data.datas_clientes);
        }
    } catch (error) {
        errorDiv.textContent = "Error al conectar con la API.";
        errorDiv.classList.remove("hidden");
    }
});

function mostrarClientes(clientes) {
    const clienteTableBody = document.getElementById("clienteTableBody");
    clienteTableBody.innerHTML = "";

    const fragment = document.createDocumentFragment();

    clientes.forEach((cliente) => {
        const row = document.createElement("tr");
        row.className = "cursor-pointer hover:bg-gray-100 cliente-row";
        row.dataset.id = cliente.idcliente;

        row.innerHTML = `
            <td class="border px-4 py-2">${cliente.idcliente}</td>
            <td class="border px-4 py-2">${cliente.dni}</td>
            <td class="border px-4 py-2">${cliente.nombre}</td>
            <td class="border px-4 py-2">${cliente.email || "No disponible"}</td>
            <td class="border px-4 py-2">${cliente.telefonomovil || "No disponible"}</td>
            <td class="border px-4 py-2">${cliente.direccion}, ${cliente.poblacion}, ${cliente.codpostal}</td>
        `;

        row.addEventListener("click", function () {
            const clienteId = this.getAttribute("data-id");
            if (clienteId) {
                // Guardar datos del cliente en localStorage
                const clienteSeleccionado = clientes.find((c) => c.idcliente === parseInt(clienteId));
                if (clienteSeleccionado) {
                    localStorage.setItem("clienteSeleccionado", JSON.stringify(clienteSeleccionado));
                    // Redirigir a la página de promociones
                    window.location.href = `/cliente_promociones?id=${clienteId}`;
                } else {
                    console.error("Datos del cliente no encontrados.");
                }
            } else {
                console.error("ID del cliente no encontrado.");
            }
        });

        fragment.appendChild(row);
    });

    clienteTableBody.appendChild(fragment);
}
