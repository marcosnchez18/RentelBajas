import mariadb

# Configura la conexión
config = {
    "user": "bajas",
    "password": "bajas",
    "host": "localhost",
    "port": 3306,
    "database": "bajas",
}

try:
    conn = mariadb.connect(**config)
    print("Conexión exitosa a MariaDB")
    conn.close()
except mariadb.Error as e:
    print(f"Error al conectar a MariaDB: {e}")
