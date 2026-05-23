import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv


def get_connection():
    """
    Establece y devuelve una conexión a la base de datos MySQL usando credenciales del archivo .env.

    Returns:
        mysql.connector.connection.MySQLConnection: Conexión activa a la base de datos
        None: Si la conexión falla
    """
    try:
        # Cargar variables de entorno desde .env
        load_dotenv()

        # Obtener credenciales desde variables de entorno
        db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME')
        }

        # Verificar que todas las credenciales estén presentes
        required_keys = ['host', 'user', 'password', 'database']
        if not all(db_config[key] for key in required_keys):
            print("Error: Faltan credenciales de base de datos en el archivo .env")
            return None

        # Establecer conexión
        connection = mysql.connector.connect(**db_config)
        print("Conexión exitosa a la base de datos MySQL")
        return connection

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado en la conexión: {e}")
        return None