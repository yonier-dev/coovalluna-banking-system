import psycopg2

#conexion con la base de datos

def get_conexion():
    conexion = psycopg2.connect(
        host="localhost",
        database="coovalluna",    # este sera el nombre para poner en la base de datos
        user="root",              # el usuario predeterminado para el proyecto
        password="1234",          # la contraseña del usuario predeterminado
        port="5432"
    )
    return conexion

# crear el usuario en pgadmin4 con el mismo nombre y contraseña
# crear la base de datos con el mismo nombre