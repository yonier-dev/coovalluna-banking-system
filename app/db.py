import psycopg2

#conexion con la base de datos

def get_conexion():
    conexion = psycopg2.connect(
        host="db.dluwuyuuewwipiztfgol.supabase.co",
        database="postgres",   
        user="postgres",             
        password="coovalluna2026",         
        port="5432"
    )
    return conexion
