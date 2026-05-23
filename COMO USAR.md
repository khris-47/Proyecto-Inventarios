# COMO USAR

## Requisitos

- Python 3.11+ (o una versión compatible con las dependencias del proyecto)
- MySQL instalado y accesible desde el equipo
- Si ya tienen instalado Mysql en el proyecto hay una carpeta con el nombre Datos
 ahi se encuentra tanto la base de datos como el excel, van a Mysql en la parte de arriba buscan donde dice `Server` > `Data Import` > `Import from Self-Contained File` y suben la base de datos

1. En caso de que les pida entorno virtual:

```powershell
.venv\Scripts\Activate.ps1
```

2. Instala las dependencias:

```powershell
pip install -r requirements.txt
```

## Crear el archivo `.env`

En la carpeta del proyecto crea un archivo llamado `.env` con el siguiente contenido:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu user
DB_PASSWORD=tu contra
DB_NAME=ferreteria_simkin
```


## Ejecutar la aplicacion

Ejecuta el archivo principal del proyecto:

```powershell
python inventario_app.py
```


