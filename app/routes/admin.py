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

@admin_bp.route('/admin/empleados/buscar-empleado', methods=['GET'])
def buscar_empleado():

    #verificación de sesión de Administrador
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    # capturar la cédula que viene desde el input del buscador
    cedula_buscar = request.args.get('cedula')
    empleado_encontrado = None

    conn = None
    cur = None

    # solo ejecutamos la consulta si el usuario envió una cédula
    if cedula_buscar:
        try:
            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # consultamos los datos uniendo la tabla empleado con cargo y agencia para traer los nombres reales
            cur.execute("""
                SELECT 
                    e.Cedula_pk,
                    e.Nombres,
                    e.Apellidos,
                    e.Correo_corp,
                    e.Tipo_labor,
                    e.Estado_laboral,
                    e.Salario_base,
                    e.Fecha_ingreso,
                    e.Bloqueado,
                    c.Nombre AS nombre_cargo,
                    a.Nombre AS nombre_agencia
                FROM EMPLEADO e
                LEFT JOIN CARGO c ON e.cod_cargo_fk = c.cod_cargo_pk
                LEFT JOIN AGENCIA a ON e.CodigoAgencia_fk = a.Codigo_pk
                WHERE e.Cedula_pk = %s
            """, (cedula_buscar.strip(),))

            fila = cur.fetchone()

            if fila:
                empleado_encontrado = {
                    'cedula': fila['cedula_pk'],
                    'nombres': fila['nombres'],
                    'apellidos': fila['apellidos'],
                    'correo_corp': fila['correo_corp'],
                    'tipo_labor': fila['tipo_labor'],
                    'estado_laboral': fila['estado_laboral'],
                    'salario_base': f"{fila['salario_base']:,}" if fila['salario_base'] else '0.00',
                    # Formateamos la fecha de ingreso 
                    'fecha_ingreso': fila['fecha_ingreso'].strftime('%Y-%m-%d') if fila['fecha_ingreso'] else 'No registrada',
                    'bloqueado': fila['bloqueado'],
                    'cargo': fila['nombre_cargo'] if fila['nombre_cargo'] else 'No asignado',
                    'agencia': fila['nombre_agencia'] if fila['nombre_agencia'] else 'No asignada'
                }
            else:
                return render_template(
                    'admin/empleados/buscar_empleado.html',
                    error='No se encontró ningún empleado registrado con esa cédula.',
                    empleado=None
                )

        except Exception as e:
            print("\n========== ERROR EN BUSQUEDA ==========")
            print(type(e))
            print(e)
            print("=======================================\n")
            
            return render_template(
                'admin/empleados/buscar_empleado.html',
                error=f'Error interno al consultar la base de datos: {str(e)}',
                empleado=None
            )

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template('admin/empleados/buscar_empleado.html', empleado=empleado_encontrado)

@admin_bp.route('/admin/empleados/cambiar-agencia', methods=['GET', 'POST'])
def cambiar_agencia():

    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    if request.method == 'POST':
        try:
            cedula = request.form['cedula']
            nuevo_codigo_agencia = request.form['nueva_agencia'].strip().upper()

            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            #verificar que la nueva agencia realmente exista
            cur.execute("""
                SELECT Codigo_pk, Nombre 
                FROM AGENCIA 
                WHERE Codigo_pk = %s
            """, (nuevo_codigo_agencia,))
            
            nueva_agencia = cur.fetchone()
            if not nueva_agencia:
                return render_template(
                    'admin/empleados/cambiar_agencia.html',
                    error=f'La agencia con código "{nuevo_codigo_agencia}" no existe en el sistema.'
                )

            #actualizar la agencia del empleado
            cur.execute("""
                UPDATE EMPLEADO
                SET CodigoAgencia_fk = %s
                WHERE Cedula_pk = %s
            """, (nuevo_codigo_agencia, cedula))

            conn.commit()

            return render_template(
                'admin/empleados/cambiar_agencia.html',
                mensaje=f'Agencia actualizada con éxito. El empleado ahora pertenece a: {nueva_agencia["nombre"]}'
            )

        except Exception as e:
            if conn:
                conn.rollback()
            return render_template(
                'admin/empleados/cambiar_agencia.html',
                error=f'Error al cambiar de agencia: {str(e)}'
            )
        finally:
            if cur: cur.close()
            if conn: conn.close()

    cedula_buscar = request.args.get('cedula')
    empleado_encontrado = None

    if not cedula_buscar:
        return render_template('admin/empleados/cambiar_agencia.html')

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # buscamos al empleado y traemos el nombre de su agencia actual haciendo un JOIN
        cur.execute("""
            SELECT 
                e.Cedula_pk,
                e.Nombres,
                e.Apellidos,
                e.CodigoAgencia_fk,
                a.Nombre AS nombre_agencia_actual
            FROM EMPLEADO e
            LEFT JOIN AGENCIA a ON e.CodigoAgencia_fk = a.Codigo_pk
            WHERE e.Cedula_pk = %s
        """, (cedula_buscar,))

        fila = cur.fetchone()

        if not fila:
            return render_template(
                'admin/empleados/cambiar_agencia.html',
                error='No se encontró ningún empleado con esa cédula'
            )

        # mapeamos los datos para el HTML
        empleado_encontrado = {
            'cedula': fila['cedula_pk'],
            'nombre_completo': f"{fila['nombres']} {fila['apellidos']}",
            'codigo_agencia_actual': fila['codigoagencia_fk'],
            'nombre_agencia_actual': fila['nombre_agencia_actual'] if fila['nombre_agencia_actual'] else 'Ninguna asignada'
        }

        return render_template(
            'admin/empleados/cambiar_agencia.html',
            empleado=empleado_encontrado
        )

    except Exception as e:
        return render_template(
            'admin/empleados/cambiar_agencia.html',
            error=f'Error al consultar: {str(e)}'
        )
    finally:
        if cur: cur.close()
        if conn: conn.close()

@admin_bp.route('/admin/empleados/desactivar-empleado', methods=['GET', 'POST'])
def desactivar_empleado():

    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    if request.method == 'POST':
        try:
            cedula = request.form['cedula']
            accion = request.form['accion'] # Puede ser 'bloquear' o 'desbloquear'
            nuevo_estado = True if accion == 'bloquear' else False

            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # actualizamos la columna 'Bloqueado' del empleado
            cur.execute("""
                UPDATE EMPLEADO
                SET Bloqueado = %s
                WHERE Cedula_pk = %s
            """, (nuevo_estado, cedula))

            conn.commit()

            msg_exito = 'Empleado BLOQUEADO (Acceso Restringido)' if nuevo_estado else 'Empleado ACTIVADO (Acceso Concedido)'
            return render_template(
                'admin/empleados/desactivar_empleado.html',
                mensaje=f'{msg_exito} correctamente.'
            )

        except Exception as e:
            if conn:
                conn.rollback()
            return render_template(
                'admin/empleados/desactivar_empleado.html',
                error=f'Error al cambiar el estado del empleado: {str(e)}'
            )
        finally:
            if cur: cur.close()
            if conn: conn.close()

    cedula_buscar = request.args.get('cedula')
    empleado_encontrado = None

    if not cedula_buscar:
        return render_template('admin/empleados/desactivar_empleado.html')

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # buscamos los datos esenciales del empleado para confirmar a quién se va a cambiar el estado
        cur.execute("""
            SELECT 
                e.Cedula_pk,
                e.Nombres,
                e.Apellidos,
                e.Bloqueado,
                c.Nombre AS nombre_cargo
            FROM EMPLEADO e
            LEFT JOIN CARGO c ON e.cod_cargo_fk = c.cod_cargo_pk
            WHERE e.Cedula_pk = %s
        """, (cedula_buscar.strip(),))

        fila = cur.fetchone()

        if not fila:
            return render_template(
                'admin/empleados/desactivar_empleado.html',
                error='No existe ningún empleado registrado con esa cédula.'
            )

        # empaquetamos los datos del empleado encontrado
        empleado_encontrado = {
            'cedula': fila['cedula_pk'],
            'nombre_completo': f"{fila['nombres']} {fila['apellidos']}",
            'cargo': fila['nombre_cargo'] if fila['nombre_cargo'] else 'Sin cargo',
            'bloqueado': fila['bloqueado']
        }

        return render_template(
            'admin/empleados/desactivar_empleado.html',
            empleado=empleado_encontrado
        )

    except Exception as e:
        return render_template(
            'admin/empleados/desactivar_empleado.html',
            error=f'Error al consultar el empleado: {str(e)}'
        )
    finally:
        if cur: cur.close()
        if conn: conn.close()

@admin_bp.route('/admin/empleados/registrar-empleado', methods=['GET', 'POST'])
def registrar_empleado():
    # Verificacin de sesión de Administrador
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    # Cargar formularios desplegables (GET)
    if request.method == 'GET':
        try:
            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Traer agencias y cargos reales de la BD para los select
            cur.execute("SELECT Codigo_pk, Nombre FROM AGENCIA ORDER BY Nombre ASC")
            agencias = cur.fetchall()
            
            cur.execute("SELECT cod_cargo_pk, Nombre FROM CARGO ORDER BY Nombre ASC")
            cargos = cur.fetchall()
            
            return render_template('admin/empleados/registrar_empleado.html', agencias=agencias, cargos=cargos)
        except Exception as e:
            print(f"Error cargando datos de registro: {str(e)}")
            return render_template('admin/empleados/registrar_empleado.html', error="Error al cargar agencias o cargos.", agencias=[], cargos=[])
        finally:
            if cur: cur.close()
            if conn: conn.close()

    # procesar la inserción (POST)
    try:
        cedula = request.form.get('cedula')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        correo = request.form.get('correo')
        salario = request.form.get('salario')
        tipo_labor = request.form.get('tipo_labor') # 'admin' o 'asesor'
        agencia_id = request.form.get('codigo_agencia_fk')
        cargo_id = request.form.get('cod_cargo_fk')

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Validar duplicados de cédula
        cur.execute("SELECT Cedula_pk FROM EMPLEADO WHERE Cedula_pk = %s", (cedula.strip(),))
        if cur.fetchone():
            # Si falla, toca recargar agencias y cargos para no romper la vista
            cur.execute("SELECT Codigo_pk, Nombre FROM AGENCIA ORDER BY Nombre ASC")
            agencias = [cur.fetchall()]
            cur.execute("SELECT cod_cargo_pk, Nombre FROM CARGO ORDER BY Nombre ASC")
            cargos = [cur.fetchall()]
            return render_template('admin/empleados/registrar_empleado.html', error='Ya existe un empleado registrado con esa cédula.', agencias=agencias, cargos=cargos)

        # Insertar el nuevo empleado
        cur.execute("""
            INSERT INTO EMPLEADO (
                Cedula_pk, 
                CodigoAgencia_fk, 
                Tipo_labor, 
                Correo_corp, 
                Nombres, 
                Apellidos, 
                cod_cargo_fk, 
                Fecha_ingreso, -- Guardará la fecha/hora del servidor automáticamente
                Salario_base, 
                Estado_laboral, 
                password, 
                Bloqueado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, 'activo', %s, FALSE)
        """, (
            cedula.strip(),          # 1 -> Cedula_pk
            agencia_id,              # 2 -> CodigoAgencia_fk
            tipo_labor,              # 3 -> Tipo_labor
            correo.strip(),          # 4 -> Correo_corp
            nombres.strip(),          # 5 -> Nombres
            apellidos.strip(),        # 6 -> Apellidos
            cargo_id,                # 7 -> cod_cargo_fk
            float(salario) if salario else 0.0, # 8 -> Salario_base
            cedula.strip()           # 9 -> password
        ))

        conn.commit()

        # Recargar listas para el siguiente registro limpio
        cur.execute("SELECT Codigo_pk, Nombre FROM AGENCIA ORDER BY Nombre ASC")
        agencias = cur.fetchall()
        cur.execute("SELECT cod_cargo_pk, Nombre FROM CARGO ORDER BY Nombre ASC")
        cargos = cur.fetchall()

        return render_template(
            'admin/empleados/registrar_empleado.html',
            mensaje=f'Empleado {nombres} {apellidos} registrado exitosamente en el sistema.',
            agencias=agencias, cargos=cargos
        )

    except Exception as e:
        if conn: conn.rollback()
        print("\n========== ERROR EN REGISTRO EMPLEADO ==========")
        print(type(e))
        print(e)
        print("================================================\n")
        return render_template('admin/empleados/registrar_empleado.html', error=f'Error de base de datos: {str(e)}', agencias=[], cargos=[])
    finally:
        if cur: cur.close()
        if conn: conn.close()

@admin_bp.route('/admin/empleados/modificar-cargo', methods=['GET', 'POST'])
def modificar_cargo():
    # Verificación de sesión de Administrador
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    cedula_buscar = request.args.get('cedula')
    empleado_encontrado = None
    cargos_disponibles = []

    conn = None
    cur = None

    #procesar la actualización del cargo (POST)
    if request.method == 'POST':
        cedula_empleado = request.form.get('cedula_empleado')
        nuevo_cargo_cod = request.form.get('cod_cargo_fk')

        if cedula_empleado and nuevo_cargo_cod:
            try:
                conn = get_conexion()
                cur = conn.cursor(cursor_factory=RealDictCursor)

                # Verificar primero que el nuevo cargo realmente exista en la tabla CARGO
                cur.execute("SELECT cod_cargo_pk FROM CARGO WHERE cod_cargo_pk = %s", (nuevo_cargo_cod,))
                if not cur.fetchone():
                    return render_template(
                        'admin/empleados/modificar_cargo.html',
                        error='El cargo seleccionado no es válido o no existe.',
                        empleado=None,
                        cargos=[]
                    )

                # Ejecutar la actualización en la tabla EMPLEADO
                cur.execute("""
                    UPDATE EMPLEADO 
                    SET cod_cargo_fk = %s 
                    WHERE Cedula_pk = %s
                """, (nuevo_cargo_cod, cedula_empleado.strip()))
                
                conn.commit()
                
                # redireccionamos pasándole la cédula por GET para mostrar el cambio reflejado inmediatamente
                return redirect(url_for('admin.modificar_cargo', cedula=cedula_empleado, exito='El cargo del empleado ha sido actualizado correctamente.'))

            except Exception as e:
                if conn:
                    conn.rollback()
                print("\n========== ERROR EN MODIFICAR CARGO (POST) ==========")
                print(type(e))
                print(e)
                print("=====================================================\n")
                return render_template(
                    'admin/empleados/modificar_cargo.html',
                    error=f'Error interno al actualizar el cargo: {str(e)}',
                    empleado=None,
                    cargos=[]
                )
            finally:
                if cur: cur.close()
                if conn: conn.close()

    # buscar empleado y cargar cargos disponibles (GET)
    if cedula_buscar:
        try:
            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # traer todos los cargos disponibles para el select ordenados alfabéticamente
            cur.execute("SELECT cod_cargo_pk, Nombre FROM CARGO ORDER BY Nombre ASC")
            cargos_disponibles = cur.fetchall()

            # consultar los datos actuales del empleado
            cur.execute("""
                SELECT 
                    e.Cedula_pk,
                    e.Nombres,
                    e.Apellidos,
                    c.cod_cargo_pk,
                    c.Nombre AS nombre_cargo,
                    a.Nombre AS nombre_agencia
                FROM EMPLEADO e
                LEFT JOIN CARGO c ON e.cod_cargo_fk = c.cod_cargo_pk
                LEFT JOIN AGENCIA a ON e.CodigoAgencia_fk = a.Codigo_pk
                WHERE e.Cedula_pk = %s
            """, (cedula_buscar.strip(),))

            fila = cur.fetchone()

            if fila:
                empleado_encontrado = {
                    'cedula': fila['cedula_pk'],
                    'nombres': fila['nombres'],
                    'apellidos': fila['apellidos'],
                    'cod_cargo_actual': fila['cod_cargo_pk'],
                    'cargo_actual': fila['nombre_cargo'] if fila['nombre_cargo'] else 'No asignado',
                    'agencia': fila['nombre_agencia'] if fila['nombre_agencia'] else 'No asignada'
                }
            else:
                return render_template(
                    'admin/empleados/modificar_cargo.html',
                    error='No se encontró ningún empleado registrado con esa cédula.',
                    empleado=None,
                    cargos=[]
                )

        except Exception as e:
            print("\n========== ERROR EN MODIFICAR CARGO (GET) ==========")
            print(type(e))
            print(e)
            print("====================================================\n")
            return render_template(
                'admin/empleados/modificar_cargo.html',
                error=f'Error interno al consultar datos: {str(e)}',
                empleado=None,
                cargos=[]
            )
        finally:
            if cur: cur.close()
            if conn: conn.close()

    # Capturar mensaje de éxito si viene de la redirección
    mensaje_exito = request.args.get('exito')

    return render_template(
        'admin/empleados/modificar_cargo.html', 
        empleado=empleado_encontrado, 
        cargos=cargos_disponibles,
        exito=mensaje_exito
    )

#GESTION - CRUD ASOCIADOS

@admin_bp.route('/admin/gestion-asociados')
def gestion_asociados():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_asociados.html')

# REPORTES 

@admin_bp.route('/admin/reportes')
def reportes():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes.html')

@admin_bp.route('/admin/reportes/asociados-estado-agencia')
def asociados_estado_agencia():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes/asociados_estado_agencia.html')

@admin_bp.route('/admin/reportes/extracto-cuenta-ahorro')
def extracto_cuenta_ahorro():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes/extracto_cuenta_ahorro.html')

@admin_bp.route('/admin/reportes/estado-cartera')
def estado_cartera():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes/estado_cartera.html')

@admin_bp.route('/admin/reportes/asociados-en-mora')
def asociados_en_mora():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes/asociados_en_mora.html')

@admin_bp.route('/admin/reportes/historial-pagos-credito')
def historial_pagos_credito():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes/historial_pagos_credito.html')

@admin_bp.route('/admin/reportes/productividad-asesores')
def productividad_asesores():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes/productividad_asesores.html')

@admin_bp.route('/admin/reportes/codeudoria-activa')
def codeudoria_activa():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes/acodeudoria_activa.html')

# SUPERVISION

@admin_bp.route('/admin/relaciones-supervision')
def relaciones_supervision():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/relaciones_supervision.html')