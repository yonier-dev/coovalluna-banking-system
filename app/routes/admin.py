from flask import Blueprint, render_template, session, redirect, url_for, request
from db import get_conexion
from psycopg2.extras import RealDictCursor
import uuid

admin_bp = Blueprint('admin', __name__)

# PANTALLAS DE INICIO
@admin_bp.route('/admin/dashboard')
def dashboard():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')


#GESTION - CRUD AGENCIAS

@admin_bp.route('/admin/gestion-agencias')
def gestion_agencias():

    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    lista_agencias = []

    try:

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # consultmaos las agencias por nombre
        cur.execute("""
            SELECT 
                Codigo_pk,
                Nombre,
                Direccion,
                Municipio,
                Telefono,
                Fecha_apertura
            FROM AGENCIA
            ORDER BY Nombre ASC
        """)

        filas = cur.fetchall()

        # se recorren los resultados y se adaptan para el html
        for fila in filas:
            lista_agencias.append({
                'codigo': fila['codigo_pk'],
                'nombre': fila['nombre'],
                'direccion': fila['direccion'],
                'municipio': fila['municipio'],
                'telefono': fila['telefono'],
                # Si la fecha existe, la dejamos bonita. Si no, ponemos un guion.
                'fecha_apertura': fila['fecha_apertura'].strftime('%Y-%m-%d %H:%M') if fila['fecha_apertura'] else '-'
            })

        return render_template(
            'admin/gestion_agencias.html', 
            agencias=lista_agencias
        )

    except Exception as e:

        print("\n========== ERROR ==========")
        print(type(e))
        print(e)
        print("===========================\n")

        return render_template(
            'admin/gestion_agencias.html',
            error=f'Error al cargar el listado de agencias: {str(e)}',
            agencias=[]
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

@admin_bp.route('/admin/agencias/buscar-agencia', methods=['GET'])
def buscar_agencia():
    

    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))


    codigo_buscar = request.args.get('codigo')
    agencia_encontrada = None
    
    conn = None
    cur = None

    if codigo_buscar:
        try:
            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # cosnultamos por llave primaria
            cur.execute("""
                SELECT 
                    Codigo_pk, 
                    Nombre, 
                    Direccion, 
                    Municipio, 
                    Telefono, 
                    Fecha_apertura 
                FROM AGENCIA 
                WHERE Codigo_pk = %s
            """, (codigo_buscar,))

            fila = cur.fetchone()

            # se mapea la fila si se encuetra
            if fila:
                agencia_encontrada = {
                    'codigo': fila['codigo_pk'],
                    'nombre': fila['nombre'],
                    'direccion': fila['direccion'],
                    'municipio': fila['municipio'],
                    'telefono': fila['telefono'],
                    # formateamos la fecha para que se vea bonita 
                    'fecha_apertura': fila['fecha_apertura'].strftime('%Y-%m-%d %H:%M') if fila['fecha_apertura'] else 'No registrada'
                }

        except Exception as e:
            print("\n========== ERROR ==========")
            print(type(e))
            print(e)
            print("===========================\n")
            
            return render_template(
                'admin/agencias/buscar_agencia.html', 
                error=f'Error al consultar la base de datos: {str(e)}',
                agencia=None
            )

        finally:

            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template('admin/agencias/buscar_agencia.html', agencia=agencia_encontrada)

@admin_bp.route('/admin/agencias/crear-agencia', methods=['GET', 'POST'])
def crear_agencia():

    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('admin/agencias/crear_agencia.html')

    conn = None
    cur = None

    try:
        #recibe los datos que manda el formulario (nombre, direccion, municipio, telefono)
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        municipio = request.form.get('municipio')
        telefono = request.form.get('telefono')

        #genera el código automáticamente 
        codigo_pk = f"AG-{str(uuid.uuid4().hex)[:6].upper()}"

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # verifica si ya existe una agencia con el mismo nombre
        cur.execute("""
            SELECT Codigo_pk
            FROM AGENCIA
            WHERE Nombre = %s
        """, (nombre,))

        if cur.fetchone():
            return render_template(
                'admin/agencias/crear_agencia.html',
                error='Ya existe una agencia registrada con ese nombre'
            )

        cur.execute("""
            INSERT INTO AGENCIA (
                Codigo_pk,
                Telefono,
                Municipio,
                Nombre,
                Fecha_apertura,
                Direccion
            )
            VALUES (
                %s, %s, %s, %s, CURRENT_TIMESTAMP, %s
            )
        """, (
            codigo_pk,
            telefono,
            municipio,
            nombre,
            direccion
        ))

        #onfirmar los cambios en la base de datos
        conn.commit()

        #retorna a la vista mandando el mensaje de éxito
        return render_template(
            'admin/agencias/crear_agencia.html',
            mensaje=(f'Agencia registrada correctamente. Código asignado: {codigo_pk}')
        )

    except Exception as e:
        
        if conn:
            conn.rollback()

        print("\n========== ERROR ==========")
        print(type(e))
        print(e)
        print("===========================\n")

        return render_template(
            'admin/agencias/crear_agencia.html',
            error=f'Error: {str(e)}'
        )

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


@admin_bp.route('/admin/agencias/modificar-agencia', methods=['GET', 'POST'])
def modificar_agencia():

    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    # procesa el formulario de edicion cuando ya se guardan los cambios
    if request.method == 'POST':

        try:

            codigo = request.form['codigo']
            nombre = request.form['nombre']
            direccion = request.form['direccion']
            telefono = request.form['telefono']

            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # actualiza unicamente los datos permitidos de la agencia
            cur.execute("""
                UPDATE AGENCIA
                SET
                    Nombre = %s,
                    Direccion = %s,
                    Telefono = %s
                WHERE Codigo_pk = %s
            """, (
                nombre,
                direccion,
                telefono,
                codigo
            ))

            conn.commit()

            return render_template(
                'admin/agencias/modificar_agencia.html',
                mensaje='Datos de la agencia actualizados correctamente'
            )

        except Exception as e:

            if conn:
                conn.rollback()

            return render_template(
                'admin/agencias/modificar_agencia.html',
                error=f'Error al actualizar: {str(e)}'
            )

        finally:

            if cur:
                cur.close()

            if conn:
                conn.close()

    # maneja la busqueda inicial por codigo para verificar si existe
    codigo_buscar = request.args.get('codigo')

    if not codigo_buscar:
        return render_template('admin/agencias/modificar_agencia.html')

    try:

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # verifica si la agencia existe para traer sus datos actuales
        cur.execute("""
            SELECT 
                Codigo_pk,
                Nombre,
                Direccion,
                Telefono
            FROM AGENCIA
            WHERE Codigo_pk = %s
        """, (codigo_buscar,))

        fila = cur.fetchone()

        if not fila:
            return render_template(
                'admin/agencias/modificar_agencia.html',
                error='La agencia no existe o el código es incorrecto'
            )

        # empaqueta los datos para que el HTML los pinte en los inputs correspondientes
        agencia_encontrada = {
            'codigo': fila['codigo_pk'],
            'nombre': fila['nombre'],
            'direccion': fila['direccion'],
            'telefono': fila['telefono']
        }

        return render_template(
            'admin/agencias/modificar_agencia.html',
            agencia=agencia_encontrada
        )

    except Exception as e:

        return render_template(
            'admin/agencias/modificar_agencia.html',
            error=f'Error al consultar: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


#GESTION - CRUD USUARIOS
@admin_bp.route('/admin/gestion-usuarios')
def gestion_usuarios():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_usuarios.html')

#GESTION - CRUD EMPLEADOS
@admin_bp.route('/admin/gestion-empleados')
def gestion_empleados():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_empleados.html')

#GESTION - CRUD     ASOCIADOS
@admin_bp.route('/admin/gestion-asociados')
def gestion_asociados():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_asociados.html')

# REPORTES Y BITACORA

@admin_bp.route('/admin/reportes')
def reportes():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes.html')

@admin_bp.route('/admin/bitacora')
def bitacora():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/bitacora.html')

# SUPERVISION

@admin_bp.route('/admin/relaciones-supervision')
def relaciones_supervision():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/relaciones_supervision.html')