import psycopg2

#conexion con la base de datos

def get_conexion():
    conexion = psycopg2.connect(
        host="aws-1-us-east-1.pooler.supabase.com",
        database="postgres",   
        user="postgres.dluwuyuuewwipiztfgol",             
        password="coovalluna2026",         
        port="5432"
    )
    return conexion
