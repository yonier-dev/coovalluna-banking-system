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

@admin_bp.route('/admin/reportes/asociados-estado-agencia', methods=['GET'])
def asociados_estado_agencia():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    lista_agencias = []
    asociados = []

    # Capturar parámetros de filtrado
    filtro_estado = request.args.get('estado', '').strip()
    filtro_agencia = request.args.get('agencia', '').strip()

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # cargar agencias reales desde tu tabla AGENCIA
        cur.execute("SELECT Codigo_pk, Nombre FROM AGENCIA ORDER BY Nombre ASC")
        lista_agencias = cur.fetchall()

        # construir la consulta usando tus tablas reales (ASOCIADO, CUENTA_AHORRO y AGENCIA)
        query_base = """
            SELECT 
                a.cedula_pk,
                a.Nombres,
                a.Apellidos,
                a.Estado,
                a.Fech_afil,
                age.Nombre AS nombre_agencia,
                COUNT(c_ah.Numero_pk) AS productos_activos
            FROM ASOCIADO a
            INNER JOIN CUENTA_AHORRO c_ah ON a.cedula_pk = c_ah.cedula_asociado_fk
            INNER JOIN AGENCIA age ON c_ah.CodigoAgencia_fk = age.Codigo_pk
        """
        
        condiciones = []
        parametros = []

        # filtro por estado del asociado (activo, suspendido, retirado)
        if filtro_estado:
            condiciones.append("a.Estado = %s")
            parametros.append(filtro_estado)
        
        # filtro por el código de la agencia de la cuenta
        if filtro_agencia:
            condiciones.append("c_ah.CodigoAgencia_fk = %s")
            parametros.append(filtro_agencia)

        if condiciones:
            query_base += " WHERE " + " AND ".join(condiciones)

        # agrupamiento respetando tus columnas y ordenamiento alfabético por Apellido
        query_base += """
            GROUP BY a.cedula_pk, a.Nombres, a.Apellidos, a.Estado, a.Fech_afil, age.Nombre
            ORDER BY a.Apellidos ASC, a.Nombres ASC
        """

        # solo ejecuta si el usuario interactuó con los filtros
        if 'estado' in request.args or 'agencia' in request.args:
            cur.execute(query_base, tuple(parametros))
            asociados = cur.fetchall()

            # formatear la columna Fech_afil de tu base de datos
            for asoc in asociados:
                if asoc['fech_afil']:
                    asoc['fech_afil'] = asoc['fech_afil'].strftime('%Y-%m-%d')

    except Exception as e:
        print(f"Error en Reporte 1: {str(e)}")
        return render_template(
            'admin/reportes/asociados_estado_agencia.html',
            error=f"Error al generar el reporte: {str(e)}",
            lista_agencias=lista_agencias,
            asociados=[]
        )
    finally:
        if cur: cur.close()
        if conn: conn.close()

    return render_template(
        'admin/reportes/asociados_estado_agencia.html',
        lista_agencias=lista_agencias,
        asociados=asociados,
        filtro_estado=filtro_estado,
        filtro_agencia=filtro_agencia,
        busqueda_realizada=('estado' in request.args or 'agencia' in request.args)
    )

@admin_bp.route('/admin/reportes/extracto-cuenta-ahorro', methods=['GET'])
def extracto_cuenta_ahorro():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    movimientos = []
    
    # estructura fija de datos para evitar errores en la plantilla
    resumen = {
        'total_entradas': 0.0,
        'total_salidas': 0.0,
        'saldo_neto': 0.0,
        'total_registros': 0
    }

    # Capturar parámetros desde la URL
    num_cuenta = request.args.get('num_cuenta', '').strip()
    fecha_inicio = request.args.get('fecha_inicio', '').strip()
    fecha_fin = request.args.get('fecha_fin', '').strip()

    busqueda_realizada = bool(num_cuenta)

    if busqueda_realizada:
        try:
            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # validar la existencia de la cuenta de ahorros
            cur.execute("""
                SELECT Numero_pk, Estado 
                FROM CUENTA_AHORRO 
                WHERE Numero_pk = %s
            """, (num_cuenta,))
            
            cuenta = cur.fetchone()
            
            if not cuenta:
                return render_template(
                    'admin/reportes/extracto_cuenta_ahorro.html',
                    error=f'La cuenta de ahorros número "{num_cuenta}" no existe en el sistema.',
                    movimientos=[],
                    resumen=resumen,
                    busqueda_realizada=busqueda_realizada,
                    num_cuenta=num_cuenta,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin
                )

            # consultar movimientos usando tu columna: cuenta_a_la_que_pertenece
            query = """
                SELECT 
                    num_transaccion_pk,
                    Saldo,
                    Tipo_Movimiento,
                    Canal,
                    Valor,
                    Fecha_Hora
                FROM MOVIMIENTO
                WHERE cuenta_a_la_que_pertenece = %s
            """
            parametros = [num_cuenta]

            if fecha_inicio:
                query += " AND Fecha_Hora >= %s"
                parametros.append(f"{fecha_inicio} 00:00:00")
            if fecha_fin:
                query += " AND Fecha_Hora <= %s"
                parametros.append(f"{fecha_fin} 23:59:59")

            query += " ORDER BY Fecha_Hora DESC"
            
            cur.execute(query, parametros)
            movimientos = cur.fetchall()

            # calcular los totales del extracto bancario
            for mov in movimientos:
                valor = float(mov['valor'])
                tipo = mov['tipo_movimiento'].upper()

                # clasificación estándar de transacciones financieras
                if tipo in ['CONSIGNACION', 'DEPOSITO', 'TRANSFERENCIA_ENTRANTE', 'INTERESES', 'CREDITO']:
                    resumen['total_entradas'] += valor
                else:
                    resumen['total_salidas'] += valor
                
                # formatear estampa de tiempo
                if mov['fecha_hora']:
                    mov['fecha_hora'] = mov['fecha_hora'].strftime('%Y-%m-%d %H:%M')

            resumen['saldo_neto'] = resumen['total_entradas'] - resumen['total_salidas']
            resumen['total_registros'] = len(movimientos)

        except Exception as e:
            print(f"Error en Reporte 2: {str(e)}")
            return render_template(
                'admin/reportes/extracto_cuenta_ahorro.html',
                error=f"Error al procesar el extracto: {str(e)}",
                movimientos=[],
                resumen=resumen,
                busqueda_realizada=busqueda_realizada,
                num_cuenta=num_cuenta,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template(
        'admin/reportes/extracto_cuenta_ahorro.html',
        movimientos=movimientos,
        resumen=resumen,
        busqueda_realizada=busqueda_realizada,
        num_cuenta=num_cuenta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@admin_bp.route('/admin/reportes/estado-cartera', methods=['GET'])
def estado_cartera():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    cartera = []
    
    # resumen para los KPI fijos
    resumen = {
        'total_creditos': 0,
        'monto_total_cartera': 0.0
    }

    # capturar filtros de la URL (GET)
    filtro_agencia = request.args.get('agencia', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()

    # bandera para saber si se interactuó con el formulario
    busqueda_realizada = ('agencia' in request.args or 'fecha_desde' in request.args)

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        #cargar las agencias reales para el select del formulario
        cur.execute("SELECT Codigo_pk, Nombre FROM AGENCIA ORDER BY Nombre ASC")
        lista_agencias = cur.fetchall()

        #construir la consulta con funciones de agregación y de ventana
        # Usamos SUM(valor_aprovado) OVER() para el total global de la consulta filtrada
        query = """
            SELECT 
                Linea_credito,
                Estado,
                COUNT(Num_radicado_pk) AS numero_creditos,
                SUM(COALESCE(valor_aprovado, 0)) AS total_aprobado,
                SUM(SUM(COALESCE(valor_aprovado, 0))) OVER() AS gran_total_cartera
            FROM CREDITO
        """
        
        condiciones = []
        parametros = []

        if filtro_agencia:
            condiciones.append("codigo_agencia_fk = %s")
            parametros.append(filtro_agencia)
        if fecha_desde:
            condiciones.append("Fecha_aprov >= %s")
            parametros.append(f"{fecha_desde} 00:00:00")
        if fecha_hasta:
            condiciones.append("Fecha_aprov <= %s")
            parametros.append(f"{fecha_hasta} 23:59:59")

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        # agrupamos por los campos clasificatorios requeridos
        query += " GROUP BY Linea_credito, Estado ORDER BY Linea_credito ASC, Estado ASC"

        # ejecuta si el usuario ya envio el formulario
        if busqueda_realizada:
            cur.execute(query, parametros)
            cartera = cur.fetchall()

            #calcula totales generales para las tarjetas fijas de resumen
            if cartera:
                resumen['monto_total_cartera'] = float(cartera[0]['gran_total_cartera'])
                resumen['total_creditos'] = sum(int(item['numero_creditos']) for item in cartera)
                
                # calculaa el porcentaje de participación individual por grupo
                for item in cartera:
                    if resumen['monto_total_cartera'] > 0:
                        item['porcentaje'] = (float(item['total_aprobado']) / resumen['monto_total_cartera']) * 100
                    else:
                        item['porcentaje'] = 0.0

    except Exception as e:
        print(f"Error en Reporte 3: {str(e)}")
        return render_template(
            'admin/reportes/estado_cartera.html',
            error=f"Error al compilar el estado de cartera: {str(e)}",
            lista_agencias=[],
            cartera=[],
            resumen=resumen,
            busqueda_realizada=busqueda_realizada
        )
    finally:
        if cur: cur.close()
        if conn: conn.close()

    return render_template(
        'admin/reportes/estado_cartera.html',
        lista_agencias=lista_agencias,
        cartera=cartera,
        resumen=resumen,
        filtro_agencia=filtro_agencia,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        busqueda_realizada=busqueda_realizada
    )

@admin_bp.route('/admin/reportes/asociados-en-mora', methods=['GET'])
def asociados_en_mora():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    mora_lista = []
    
    resumen = {
        'total_en_mora': 0,
        'monto_vencido_total': 0.0
    }

    filtro_dias = request.args.get('dias_mora', '').strip()
    busqueda_realizada = 'dias_mora' in request.args

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # consulta para buscar cuotas vencidas y calcular los dias de retraso de forma exacta
        query = """
            SELECT 
                a.cedula_pk,
                a.Nombres AS nombres_asoc,
                a.Apellidos AS apellidos_asoc,
                c.Num_radicado_pk,
                c.Linea_credito,
                cu.id_pago_pk,
                cu.Num_cuota,
                cu.Fech_pago AS fecha_vencimiento,
                cu.Valor_pagado AS valor_cuota,
                (CURRENT_DATE - cu.Fech_pago) AS dias_retraso,
                emp.Nombres AS nombre_asesor,
                emp.Apellidos AS apellido_asesor
            FROM ASOCIADO a
            INNER JOIN SOLICITA s ON a.cedula_pk = s.CedulaAsociado_fk
            INNER JOIN CREDITO c ON s.Num_radicadoCredito_fk = c.Num_radicado_pk
            INNER JOIN CUOTAS cu ON c.Num_radicado_pk = cu.Num_radicado_fk
            LEFT JOIN ATIENDE at ON a.cedula_pk = at.cedulaAsociado_fk
            LEFT JOIN EMPLEADO emp ON at.cedulaEmpleado_fk = emp.Cedula_pk
            WHERE cu.Estado_pago = 'PENDIENTE' 
              AND cu.Fech_pago < CURRENT_DATE
        """
        
        parametros = []
        
        # filtro dinamico para ver la gravedad de la cartera vencida
        if filtro_dias:
            query += " AND (CURRENT_DATE - cu.Fech_pago) >= %s"
            parametros.append(int(filtro_dias))
            
        query += " ORDER BY dias_retraso DESC, a.Apellidos ASC"

        if busqueda_realizada:
            cur.execute(query, parametros)
            mora_lista = cur.fetchall()

            if mora_lista:
                resumen['total_en_mora'] = len(mora_lista)
                resumen['monto_vencido_total'] = sum(float(item['valor_cuota']) for item in mora_lista)

                # formatear la fecha de vencimiento antes de mandar a la plantilla
                for item in mora_lista:
                    if item['fecha_vencimiento']:
                        item['fecha_vencimiento'] = item['fecha_vencimiento'].strftime('%Y-%m-%d')

    except Exception as e:
        print(f"error en reporte de mora: {str(e)}")
        return render_template(
            'admin/reportes/asociados_en_mora.html',
            error=f"error en el servidor al cargar datos: {str(e)}",
            mora_lista=[],
            resumen=resumen,
            busqueda_realizada=busqueda_realizada
        )
    finally:
        if cur: cur.close()
        if conn: conn.close()

    return render_template(
        'admin/reportes/asociados_en_mora.html',
        mora_lista=mora_lista,
        resumen=resumen,
        filtro_dias=filtro_dias,
        busqueda_realizada=busqueda_realizada
    )

@admin_bp.route('/admin/reportes/historial-pagos-credito', methods=['GET'])
def historial_pagos_credito():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    cuotas_lista = []
    
    resumen = {
        'total_cuotas': 0,
        'monto_pagado': 0.0,
        'monto_pendiente': 0.0
    }

    num_radicado = request.args.get('num_radicado', '').strip()
    busqueda_realizada = bool(num_radicado)

    if busqueda_realizada:
        try:
            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # validamos si el radicado del credito existe en la base de datos
            cur.execute("""
                SELECT Num_radicado_pk, Linea_credito, valor_aprovado 
                FROM CREDITO 
                WHERE Num_radicado_pk = %s
            """, (num_radicado,))
            
            credito = cur.fetchone()
            
            if not credito:
                return render_template(
                    'admin/reportes/historial_pagos_credito.html',
                    error=f'el credito con radicado "{num_radicado}" no existe en el sistema.',
                    cuotas_lista=[],
                    resumen=resumen,
                    busqueda_realizada=busqueda_realizada,
                    num_radicado=num_radicado
                )

            # buscamos el plan de cuotas ligado al radicado
            query = """
                SELECT 
                    id_pago_pk,
                    Valor_pagado,
                    Num_cuota,
                    Fech_pago AS fecha_vencimiento,
                    Estado_pago
                FROM CUOTAS
                WHERE Num_radicado_fk = %s
                ORDER BY Num_cuota ASC
            """
            
            cur.execute(query, (num_radicado,))
            cuotas_lista = cur.fetchall()

            # calculamos los acumulados segun el estado de cada cuota
            for c in cuotas_lista:
                valor = float(c['valor_pagado'])
                estado = c['estado_pago'].upper() if c['estado_pago'] else 'PENDIENTE'

                if estado == 'PAGADO':
                    resumen['monto_pagado'] += valor
                else:
                    resumen['monto_pendiente'] += valor
                
                if c['fecha_vencimiento']:
                    c['fecha_vencimiento'] = c['fecha_vencimiento'].strftime('%Y-%m-%d')

            resumen['total_cuotas'] = len(cuotas_lista)

        except Exception as e:
            print(f"error en historial de pagos: {str(e)}")
            return render_template(
                'admin/reportes/historial_pagos_credito.html',
                error=f"error interno al procesar el historial: {str(e)}",
                cuotas_lista=[],
                resumen=resumen,
                busqueda_realizada=busqueda_realizada,
                num_radicado=num_radicado
            )
        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template(
        'admin/reportes/historial_pagos_credito.html',
        cuotas_lista=cuotas_lista,
        resumen=resumen,
        busqueda_realizada=busqueda_realizada,
        num_radicado=num_radicado
    )

@admin_bp.route('/admin/reportes/productividad-asesores', methods=['GET'])
def productividad_asesores():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    asesores_lista = []
    
    resumen = {
        'total_asesores': 0,
        'total_atenciones': 0
    }

    filtro_mes = request.args.get('mes_busqueda', '').strip()
    busqueda_realizada = 'mes_busqueda' in request.args

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # consulta para agrupar las atenciones reales por cada empleado
        query = """
            SELECT 
                e.Cedula_pk,
                e.Nombres AS nombre_emp,
                e.Apellidos AS apellido_emp,
                e.Correo_corp,
                e.Estado_Laboral,
                COUNT(at.cedulaAsociado_fk) AS total_atendidos
            FROM EMPLEADO e
            LEFT JOIN ATIENDE at ON e.Cedula_pk = at.cedulaEmpleado_fk
        """
        
        condiciones = []
        parametros = []

        # filtro opcional para segmentar la productividad por mes
        if filtro_mes:
            condiciones.append("EXTRACT(MONTH FROM at.Fecha_atencion) = %s")
            parametros.append(int(filtro_mes))

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)
            
        query += """
            GROUP BY e.Cedula_pk, e.Nombres, e.Apellidos, e.Correo_corp, e.Estado_Laboral
            ORDER BY total_atendidos DESC, e.Apellidos ASC
        """

        if busqueda_realizada:
            cur.execute(query, parametros)
            asesores_lista = cur.fetchall()

            if asesores_lista:
                resumen['total_asesores'] = len(asesores_lista)
                resumen['total_atenciones'] = sum(int(item['total_atendidos']) for item in asesores_lista)

    except Exception as e:
        print(f"error en reporte de productividad: {str(e)}")
        return render_template(
            'admin/reportes/productividad_asesores.html',
            error=f"error al recopilar el rendimiento: {str(e)}",
            asesores_lista=[],
            resumen=resumen,
            busqueda_realizada=busqueda_realizada
        )
    finally:
        if cur: cur.close()
        if conn: conn.close()

    return render_template(
        'admin/reportes/productividad_asesores.html',
        asesores_lista=asesores_lista,
        resumen=resumen,
        filtro_mes=filtro_mes,
        busqueda_realizada=busqueda_realizada
    )

@admin_bp.route('/admin/reportes/codeudoria-activa', methods=['GET'])
def codeudoria_activa():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None
    respaldos_lista = []
    
    resumen = {
        'total_respaldados': 0,
        'monto_total_garantizado': 0.0
    }

    cedula_codeudor = request.args.get('cedula_codeudor', '').strip()
    busqueda_realizada = bool(cedula_codeudor)

    if busqueda_realizada:
        try:
            conn = get_conexion()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # validamos si el asociado que actua como codeudor existe
            cur.execute("""
                SELECT Cedula_pk, Nombres, Apellidos 
                FROM ASOCIADO 
                WHERE Cedula_pk = %s
            """, (cedula_codeudor,))
            
            codeudor = cur.fetchone()
            
            if not codeudor:
                return render_template(
                    'admin/reportes/acodeudoria_activa.html',
                    error=f'el asociado con cedula "{cedula_codeudor}" no existe en el sistema.',
                    respaldos_lista=[],
                    resumen=resumen,
                    busqueda_realizada=busqueda_realizada,
                    cedula_codeudor=cedula_codeudor
                )

            # cruza las tablas de codeudoria con credito y asociado para extraer 
            # los amparos activos y los titulares de las deudas
            query = """
                SELECT 
                    c.Num_radicado_pk,
                    c.Linea_credito,
                    c.valor_aprovado,
                    c.Estado,
                    deudor.cedula_pk AS cedula_deudor,
                    deudor.Nombres AS nombre_deudor,
                    deudor.Apellidos AS apellido_deudor
                FROM ES_CODEUDOR g
                INNER JOIN CREDITO c ON g.Num_radicadoCredito_fk = c.Num_radicado_pk
                INNER JOIN SOLICITA s ON c.Num_radicado_pk = s.Num_radicadoCredito_fk
                INNER JOIN ASOCIADO deudor ON s.CedulaAsociado_fk = deudor.cedula_pk
                WHERE g.CedulaAsociado_fk = %s AND c.Estado = 'ACTIVO'
                ORDER BY c.valor_aprovado DESC
            """
            
            cur.execute(query, (cedula_codeudor,))
            respaldos_lista = cur.fetchall()

            # acumulamos las metricas fijas financieras del codeudor
            if respaldos_lista:
                resumen['total_respaldados'] = len(respaldos_lista)
                resumen['monto_total_garantizado'] = sum(float(item['valor_aprovado']) for item in respaldos_lista)

        except Exception as e:
            print(f"error en reporte de codeudoria: {str(e)}")
            return render_template(
                'admin/reportes/acodeudoria_activa.html',
                error=f"error en el motor al compilar amparos: {str(e)}",
                respaldos_lista=[],
                resumen=resumen,
                busqueda_realizada=busqueda_realizada,
                cedula_codeudor=cedula_codeudor
            )
        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template(
        'admin/reportes/acodeudoria_activa.html',
        respaldos_lista=respaldos_lista,
        resumen=resumen,
        busqueda_realizada=busqueda_realizada,
        cedula_codeudor=cedula_codeudor
    )   

# SUPERVISION

@admin_bp.route('/admin/relaciones-supervision')
def relaciones_supervision():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/relaciones_supervision.html')