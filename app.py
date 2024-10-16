from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    cliente_data = None
    error = None
    
    if request.method == 'POST':
        dni = request.form['dni']
        
        # URL de la API
        url = "http://10.58.6.89:8082/get_data_client_for_dni"
        
        # Datos a enviar en el cuerpo de la petición POST
        data = {
            "dni": dni
        }
        
        # Haciendo la petición POST a la API
        response = requests.post(url, json=data)
        
        # Comprobando si la petición fue exitosa
        if response.status_code == 200:
            cliente_data = response.json()
            if not cliente_data:
                error = "No se encontraron datos para el DNI proporcionado."
        else:
            error = f"Error en la petición: {response.status_code}"
    
    return render_template('search.html', cliente_data=cliente_data, error=error)

if __name__ == '__main__':
    app.run(debug=True)
