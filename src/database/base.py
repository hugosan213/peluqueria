import mysql.connector
from mysql.connector import Error

class BaseDatabase:
    def __init__(self):
        self.config = {
            'host': '127.0.0.1',
            'user': 'root', 
            'password': '17032003Hsanti', 
            'database': 'peluqueria'
        }

    def conectar(self):
        try:
            conexion = mysql.connector.connect(**self.config)
            if conexion.is_connected():
                return conexion
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None