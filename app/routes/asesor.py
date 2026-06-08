from flask import Blueprint, render_template, session, redirect, url_for, request
from db import get_conexion
from psycopg2.extras import RealDictCursor

asesor_bp = Blueprint('asesor', __name__)


@asesor_bp.route('/asesor/dashboard')
def dashboard():
    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    return render_template('asesor/dashboard.html')

#  IMPLEMENTADA

@asesor_bp.route('/asesor/consulta-asociado')
def consultar_asociado():

    print("=== ENTRO A CONSULTAR ASOCIADO ===")

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    busqueda = request.args.get('busqueda')

    print("Busqueda:", busqueda)

    if not busqueda:
        return render_template(
            'asesor/consulta_asociado.html'
        )

    conn = None
    cur = None

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cedula_asesor = session.get('cedula')

        print("Cedula asesor:", cedula_asesor)

        # obtiene la agencia del asesor para limitar la busqueda a esa agencia
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (cedula_asesor,))

        asesor = cur.fetchone()

        print("Datos asesor:", asesor)

        if not asesor:
            return render_template(
                'asesor/consulta_asociado.html',
                error='No se encontró la información del asesor'
            )

        agencia = asesor['codigoagencia_fk']

        print("Agencia asesor:", agencia)

        # se busca el asociado por cédula, nombre o apellido, pero solo dentro de la agencia del asesor
        cur.execute("""
            SELECT DISTINCT a.*
            FROM ASOCIADO a
            JOIN CUENTA_AHORRO c
                ON c.cedula_asociado_fk = a.cedula_pk
            WHERE c.CodigoAgencia_fk = %s
            AND (
                a.cedula_pk = %s
                OR LOWER(a.nombres) LIKE LOWER(%s)
                OR LOWER(a.apellidos) LIKE LOWER(%s)
                OR LOWER(a.nombres || ' ' || a.apellidos) LIKE LOWER(%s)
            )
            LIMIT 1
        """, (
            agencia,
            busqueda,
            f'%{busqueda}%',
            f'%{busqueda}%',
            f'%{busqueda}%'
        ))

        asociado = cur.fetchone()

        print("Asociado encontrado:", asociado)

        if not asociado:
            return render_template(
                'asesor/consulta_asociado.html',
                error='Asociado no encontrado'
            )

        cedula_asociado = asociado['cedula_pk']

        # asociado si es fundador
        cur.execute("""
            SELECT *
            FROM ASOCIADO_FUND
            WHERE cedula_pk = %s
        """, (cedula_asociado,))

        fundador = cur.fetchone()

        print("Fundador:", fundador)

        # puede buscar beneficiarios asociados a ese asociado (si es fundador o no)
        cur.execute("""
            SELECT *
            FROM BENEFICIARIO
            WHERE cedulaAsociado_fk = %s
        """, (cedula_asociado,))

        beneficiarios = cur.fetchall()

        print("Beneficiarios:", beneficiarios)

        # cuentas del asociado, pero solo de la agencia del asesor
        cur.execute("""
            SELECT
                Numero_pk,
                Estado,
                CodigoAgencia_fk AS agencia
            FROM CUENTA_AHORRO
            WHERE cedula_asociado_fk = %s
        """, (cedula_asociado,))

        cuentas = cur.fetchall()

        print("Cuentas:", cuentas)

        # creditos del asociado, pero solo de la agencia del asesor
        cur.execute("""
            SELECT
                c.Num_radicado_pk AS num_radicado,
                c.Estado,
                c.Linea_credito
            FROM CREDITO c
            JOIN SOLICITA s
                ON s.Num_radicadoCredito_fk = c.Num_radicado_pk
            WHERE s.CedulaAsociado_fk = %s
        """, (cedula_asociado,))

        creditos = cur.fetchall()

        print("Creditos:", creditos)

        return render_template(
            'asesor/consulta_asociado.html',
            asociado=asociado,
            fundador=fundador,
            beneficiarios=beneficiarios,
            cuentas=cuentas,
            creditos=creditos
        )

    except Exception as e:

        print("ERROR:", str(e))

        return render_template(
            'asesor/consulta_asociado.html',
            error=f'Error al consultar: {str(e)}'
        )

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


# Implementada: actualiza unicamente los datos de contacto del asociado (teléfono, correo y dirección)
@asesor_bp.route('/asesor/actualizar-contacto', methods=['GET', 'POST'])
def actualizar_contacto():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/actualizar_contacto.html')

    conn = None
    cur = None

    try:

        cedula = request.form['cedula']
        telefono = request.form['telefono']
        correo = request.form['correo']
        direccion = request.form['direccion']

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cedula_asesor = session.get('cedula')

        # agencia del asesor para que no actualice datos de asociados que no sean de su agencia
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (cedula_asesor,))

        asesor = cur.fetchone()

        if not asesor:
            return render_template(
                'asesor/actualizar_contacto.html',
                error='No se encontró la información del asesor'
            )

        agencia = asesor['codigoagencia_fk']

        # verifica que el asociado pertenezca a la agencia del asesor antes de actualizar sus datos de contacto
        cur.execute("""
            SELECT DISTINCT a.cedula_pk
            FROM ASOCIADO a
            JOIN CUENTA_AHORRO c
                ON c.cedula_asociado_fk = a.cedula_pk
            WHERE a.cedula_pk = %s
              AND c.CodigoAgencia_fk = %s
        """, (cedula, agencia))

        asociado = cur.fetchone()

        if not asociado:
            return render_template(
                'asesor/actualizar_contacto.html',
                error='El asociado no existe o no pertenece a su agencia'
            )

        # actualiza unicamente los datos del contacto del asociado
        cur.execute("""
            UPDATE ASOCIADO
            SET
                Telefono = %s,
                correo = %s,
                Direccion = %s
            WHERE cedula_pk = %s
        """, (
            telefono,
            correo,
            direccion,
            cedula
        ))

        conn.commit()

        return render_template(
            'asesor/actualizar_contacto.html',
            mensaje='Datos actualizados correctamente'
        )

    except Exception as e:

        return render_template(
            'asesor/actualizar_contacto.html',
            error=f'Error al actualizar: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# Implementada
@asesor_bp.route('/asesor/beneficiarios', methods=['GET', 'POST'])
def beneficiarios():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/beneficiarios.html')

    conn = None
    cur = None

    try:

        print("\n========== POST RECIBIDO ==========")
        print(request.form)
        print("===================================\n")

        cedula_asociado = request.form.get('cedulaAsociado')
        cantidad = int(request.form.get('cantidad', 0))

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Agencia del asesor
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        asesor = cur.fetchone()

        if not asesor:
            return render_template(
                'asesor/beneficiarios.html',
                error='No se encontró la información del asesor'
            )

        agencia = asesor['codigoagencia_fk']

        # Verificar si el asociado existe y pertenece a la agencia del asesor
        cur.execute("""
            SELECT DISTINCT a.cedula_pk
            FROM ASOCIADO a
            JOIN CUENTA_AHORRO c
                ON c.cedula_asociado_fk = a.cedula_pk
            WHERE a.cedula_pk = %s
            AND c.CodigoAgencia_fk = %s
        """, (
            cedula_asociado,
            agencia
        ))

        asociado = cur.fetchone()

        if not asociado:
            return render_template(
                'asesor/beneficiarios.html',
                error='El asociado no existe o no pertenece a su agencia'
            )

        # la cantidad actual de beneficiarios del asociado no puede superar 4, incluyendo los nuevos que se quieren registrar
        cur.execute("""
            SELECT COUNT(*) AS total
            FROM BENEFICIARIO
            WHERE cedulaAsociado_fk = %s
        """, (cedula_asociado,))

        total_actual = cur.fetchone()['total']

        if total_actual + cantidad > 4:
            return render_template(
                'asesor/beneficiarios.html',
                error='No puede tener más de 4 beneficiarios'
            )

        # Validar porcentajes que no se pase del 100% en total entre todos los beneficiarios (incluyendo los ya registrados y los nuevos)
        suma_porcentajes = 0

        for i in range(1, cantidad + 1):

            porcentaje = float(
                request.form.get(f'porcentaje{i}', 0)
            )

            print(f"Porcentaje {i} =", porcentaje)

            suma_porcentajes += porcentaje

        print("SUMA TOTAL =", suma_porcentajes)

        if abs(suma_porcentajes - 100) > 0.01:
            return render_template(
                'asesor/beneficiarios.html',
                error='La suma de porcentajes debe ser exactamente 100%'
            )

        if suma_porcentajes != 100:
            return render_template(
                'asesor/beneficiarios.html',
                error='La suma de porcentajes debe ser exactamente 100%'
            )

        # Insertar beneficiarios en la base de datos
        for i in range(1, cantidad + 1):

            documento = request.form.get(f'doc{i}')
            nombre = request.form.get(f'nombre{i}')
            parentesco = request.form.get(f'parentesco{i}')
            porcentaje = request.form.get(f'porcentaje{i}')
            telefono = request.form.get(f'telefono{i}')

            print(
                documento,
                nombre,
                parentesco,
                porcentaje,
                telefono
            )

            cur.execute("""
                INSERT INTO BENEFICIARIO (
                    cedula_pk,
                    cedulaAsociado_fk,
                    Parentesco,
                    Nombre_Completo,
                    Porcentaje_participacion,
                    Telefono
                )
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                documento,
                cedula_asociado,
                parentesco,
                nombre,
                porcentaje,
                telefono
            ))

        conn.commit()

        return render_template(
            'asesor/beneficiarios.html',
            mensaje='Beneficiarios registrados correctamente'
        )

    except Exception as e:

        print("\n========== ERROR ==========")
        print(type(e))
        print(e)
        print("===========================\n")

        return render_template(
            'asesor/beneficiarios.html',
            error=f'Error: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

@asesor_bp.route('/asesor/registro-asociado', methods=['GET', 'POST'])
def registrar_asociado():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/registro_asociado.html')

    conn = None
    cur = None

    try:

        cedula = request.form.get('cedula')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        direccion = request.form.get('direccion')
        municipio = request.form.get('municipio')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        fecha_afiliacion = request.form.get('fecha_afiliacion')
        estado = request.form.get('estado')
        tipo = request.form.get('tipo')

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # verifica si ya existe un asociado con la misma cedula para evitar duplicados
        cur.execute("""
            SELECT cedula_pk
            FROM ASOCIADO
            WHERE cedula_pk = %s
        """, (cedula,))

        if cur.fetchone():
            return render_template(
                'asesor/registro_asociado.html',
                error='Ya existe un asociado con esa cédula'
            )

        # registra el asociado
        cur.execute("""
            INSERT INTO ASOCIADO (
                cedula_pk,
                nombres,
                apellidos,
                fecha_na,
                telefono,
                estado,
                fech_afil,
                municipio,
                correo,
                direccion,
                password,
                intentos_fallidos,
                bloqueado
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,0,FALSE
            )
        """, (
            cedula,
            nombres,
            apellidos,
            fecha_nacimiento,
            telefono,
            estado,
            fecha_afiliacion,
            municipio,
            correo,
            direccion,
            cedula  # contraseña inicial
        ))

        # Se registra info adicional si es fundador
        if tipo == 'fundador':

            acta = request.form.get('acta')
            anio = request.form.get('anio')
            beneficios = request.form.get('beneficios')

            cur.execute("""
                INSERT INTO ASOCIADO_FUND (
                    cedula_pk,
                    Num_acta_fundacional,
                    Ano_reconocimiento,
                    Descripcion_beneficios,
                    Fecha_firma
                )
                VALUES (
                    %s,%s,%s,%s,CURRENT_TIMESTAMP
                )
            """, (
                cedula,
                acta,
                anio,
                beneficios
            ))

        # Obtener agencia del asesor
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        asesor = cur.fetchone()

        if not asesor:
            return render_template(
                'asesor/registro_asociado.html',
                error='No se encontró la información del asesor'
            )

        agencia = asesor['codigoagencia_fk']

        # crear cuenta de ahorro automaticamente para el asociado, con un numero único generado a partir de su cedula y la agencia del asesor
        numero_cuenta = f"CA{cedula}"

        cur.execute("""
            INSERT INTO CUENTA_AHORRO (
                Numero_pk,
                CodigoAgencia_fk,
                cedula_asociado_fk,
                Fecha_apertura,
                Estado
            )
            VALUES (
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP,
                'ACTIVA'
            )
        """, (
            numero_cuenta,
            agencia,
            cedula
        ))

        conn.commit()

        return render_template(
            'asesor/registro_asociado.html',
            mensaje=(
                f'Asociado registrado correctamente. '
                f'Se creó la cuenta {numero_cuenta}.'
            )
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("\n========== ERROR ==========")
        print(type(e))
        print(e)
        print("===========================\n")

        return render_template(
            'asesor/registro_asociado.html',
            error=f'Error: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

# IMPLEMENTADA
@asesor_bp.route('/asesor/apertura-cuenta', methods=['GET', 'POST'])
def apertura_cuenta():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/apertura_cuenta.html')

    conn = None
    cur = None

    try:

        cedula = request.form.get('cedula')
        fecha = request.form.get('fecha')

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # la agencia del asesor
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        asesor = cur.fetchone()

        if not asesor:
            return render_template(
                'asesor/apertura_cuenta.html',
                error='No se encontró la información del asesor'
            )

        agencia = asesor['codigoagencia_fk']

        # mira si el asociado esta activo y existe para la agencia del asesor
        cur.execute("""
            SELECT cedula_pk, estado
            FROM ASOCIADO
            WHERE cedula_pk = %s
        """, (cedula,))

        asociado = cur.fetchone()

        if not asociado:
            return render_template(
                'asesor/apertura_cuenta.html',
                error='El asociado no existe'
            )

        if asociado['estado'].lower() != 'activo':
            return render_template(
                'asesor/apertura_cuenta.html',
                error='Solo se pueden abrir cuentas a asociados activos'
            )

        # crea un numero de cuenta unico 
        import uuid

        numero_cuenta = "CA" + uuid.uuid4().hex[:10].upper()

        cur.execute("""
            INSERT INTO CUENTA_AHORRO(
                Numero_pk,
                CodigoAgencia_fk,
                cedula_asociado_fk,
                Fecha_apertura,
                Estado
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                'ACTIVA'
            )
        """, (
            numero_cuenta,
            agencia,
            cedula,
            fecha
        ))

        conn.commit()

        return render_template(
            'asesor/apertura_cuenta.html',
            mensaje=f'Cuenta creada correctamente. Número: {numero_cuenta}'
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(e)

        return render_template(
            'asesor/apertura_cuenta.html',
            error=f'Error: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# IMPLEMENTADA
@asesor_bp.route('/asesor/deposito', methods=['GET', 'POST'])
def deposito():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/deposito.html')

    conn = None
    cur = None

    try:

        cedula = request.form.get('cedula')
        numero_cuenta = request.form.get('cuenta')
        valor = float(request.form.get('valor'))
        canal = request.form.get('canal')

        if valor <= 0:
            return render_template(
                'asesor/deposito.html',
                error='El valor debe ser mayor que cero'
            )

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Agencia del asesor
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        asesor = cur.fetchone()

        if not asesor:
            return render_template(
                'asesor/deposito.html',
                error='No se encontró el asesor'
            )

        agencia = asesor['codigoagencia_fk']

        # Verifica la cuenta
        cur.execute("""
            SELECT *
            FROM CUENTA_AHORRO
            WHERE Numero_pk = %s
            AND cedula_asociado_fk = %s
            AND CodigoAgencia_fk = %s
        """, (
            numero_cuenta,
            cedula,
            agencia
        ))

        cuenta = cur.fetchone()

        if not cuenta:
            return render_template(
                'asesor/deposito.html',
                error='La cuenta no existe o no pertenece a su agencia'
            )

        # obtiene el saldo actual de la cuenta a partir del ultimo movimiento registrado
        cur.execute("""
            SELECT Saldo
            FROM MOVIMIENTO
            WHERE cuenta_a_la_que_pertenece = %s
            ORDER BY Fecha_Hora DESC
            LIMIT 1
        """, (numero_cuenta,))

        ultimo_mov = cur.fetchone()

        saldo_actual = (
            float(ultimo_mov['saldo'])
            if ultimo_mov
            else 0
        )

        nuevo_saldo = saldo_actual + valor

        # genera un numero de transaccion unico
        import uuid

        num_transaccion = str(uuid.uuid4())[:20]

        # registra el movimiento
        cur.execute("""
            INSERT INTO MOVIMIENTO(
                num_transaccion_pk,
                saldo,
                tipo_movimiento,
                canal,
                valor,
                cuenta_a_la_que_pertenece
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            num_transaccion,
            nuevo_saldo,
            'DEPOSITO',
            canal,
            valor,
            numero_cuenta
        ))

        conn.commit()

        return render_template(
            'asesor/deposito.html',
            mensaje=f'Depósito registrado correctamente. Nuevo saldo: ${nuevo_saldo:,.0f}'
        )

    except Exception as e:

        return render_template(
            'asesor/deposito.html',
            error=f'Error: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# IMPLEMENTADA
@asesor_bp.route('/asesor/retiro', methods=['GET', 'POST'])
@asesor_bp.route('/asesor/retiro', methods=['GET', 'POST'])
def retiro():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/retiro.html')

    conn = None
    cur = None

    try:

        cedula = request.form.get('cedula')
        numero_cuenta = request.form.get('cuenta')
        valor = float(request.form.get('valor'))
        canal = request.form.get('canal')

        if valor <= 0:
            return render_template(
                'asesor/retiro.html',
                error='El valor debe ser mayor que cero'
            )

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Agencia del asesor
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        asesor = cur.fetchone()

        if not asesor:
            return render_template(
                'asesor/retiro.html',
                error='No se encontró la información del asesor'
            )

        agencia = asesor['codigoagencia_fk']

        # Verificar cuenta
        cur.execute("""
            SELECT *
            FROM CUENTA_AHORRO
            WHERE Numero_pk = %s
            AND cedula_asociado_fk = %s
            AND CodigoAgencia_fk = %s
        """, (
            numero_cuenta,
            cedula,
            agencia
        ))

        cuenta = cur.fetchone()

        if not cuenta:
            return render_template(
                'asesor/retiro.html',
                error='La cuenta no existe o no pertenece a su agencia'
            )

        # Mira el saldo actual
        cur.execute("""
            SELECT saldo
            FROM MOVIMIENTO
            WHERE cuenta_a_la_que_pertenece = %s
            ORDER BY fecha_hora DESC
            LIMIT 1
        """, (numero_cuenta,))

        ultimo_mov = cur.fetchone()

        saldo_actual = (
            float(ultimo_mov['saldo'])
            if ultimo_mov
            else 0
        )

        if saldo_actual < valor:
            return render_template(
                'asesor/retiro.html',
                error=f'Saldo insuficiente. Disponible: ${saldo_actual:,.0f}'
            )

        nuevo_saldo = saldo_actual - valor

        import uuid

        num_transaccion = str(uuid.uuid4())[:20]

        cur.execute("""
            INSERT INTO MOVIMIENTO(
                num_transaccion_pk,
                saldo,
                tipo_movimiento,
                canal,
                valor,
                cuenta_a_la_que_pertenece
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            num_transaccion,
            nuevo_saldo,
            'RETIRO',
            canal,
            valor,
            numero_cuenta
        ))

        conn.commit()

        return render_template(
            'asesor/retiro.html',
            mensaje=f'Retiro registrado correctamente. Nuevo saldo: ${nuevo_saldo:,.0f}'
        )

    except Exception as e:

        return render_template(
            'asesor/retiro.html',
            error=f'Error: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

# IMPLEMENTADA
@asesor_bp.route('/asesor/transferencia', methods=['GET', 'POST'])
def transferencia():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/transferencia.html')

    conn = None
    cur = None

    try:

        cedula = request.form['cedula'].strip()
        cuenta_origen = request.form['cuentaOrigen'].strip()
        cuenta_destino = request.form['cuentaDestino'].strip()
        valor = float(request.form['valor'])
        canal = request.form['canal']

        print("\n========== DATOS RECIBIDOS ==========")
        print("CEDULA =", repr(cedula))
        print("ORIGEN =", repr(cuenta_origen))
        print("DESTINO =", repr(cuenta_destino))
        print("=====================================\n")

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # VALIDAR CUENTA ORIGEN
        cur.execute("""
            SELECT *
            FROM CUENTA_AHORRO
            WHERE TRIM(Numero_pk) = %s
              AND TRIM(cedula_asociado_fk) = %s
              AND LOWER(TRIM(Estado)) IN ('activa','activo')
        """, (cuenta_origen, cedula))

        origen = cur.fetchone()

        print("\n========== DEBUG ORIGEN ==========")
        print("Cedula ingresada:", cedula)
        print("Cuenta origen ingresada:", cuenta_origen)
        print("Resultado consulta:", origen)
        print("==================================\n")

        if not origen:
            return render_template(
                'asesor/transferencia.html',
                error='La cuenta origen no existe, no está activa o no pertenece al asociado'
            )
        # VALIDAR CUENTA DESTINO
        cur.execute("""
            SELECT *
            FROM CUENTA_AHORRO
            WHERE TRIM(Numero_pk) = %s
              AND LOWER(TRIM(Estado)) IN ('activa','activo')
        """, (cuenta_destino,))

        destino = cur.fetchone()

        print("\n========== DEBUG DESTINO ==========")
        print(destino)
        print("===================================\n")

        if not destino:
            return render_template(
                'asesor/transferencia.html',
                error='La cuenta destino no existe o no está activa'
            )

        # MISMA CUENTA
        if cuenta_origen == cuenta_destino:
            return render_template(
                'asesor/transferencia.html',
                error='La cuenta origen y destino no pueden ser iguales'
            )


        # CALCULAR SALDO ORIGEN
        cur.execute("""
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN Tipo_Movimiento IN
                        ('DEPOSITO','TRANSFERENCIA_ENTRANTE')
                            THEN Valor

                        WHEN Tipo_Movimiento IN
                        ('RETIRO','TRANSFERENCIA_SALIENTE')
                            THEN -Valor

                        ELSE 0
                    END
                ),
                0
            ) AS saldo
            FROM MOVIMIENTO
            WHERE cuenta_a_la_que_pertenece = %s
        """, (cuenta_origen,))

        saldo_actual = float(cur.fetchone()['saldo'])

        print("SALDO ORIGEN =", saldo_actual)

        if saldo_actual < valor:
            return render_template(
                'asesor/transferencia.html',
                error=f'Saldo insuficiente. Disponible: ${saldo_actual:,.0f}'
            )

        nuevo_saldo_origen = saldo_actual - valor

        # CALCULAR SALDO DESTINp
        cur.execute("""
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN Tipo_Movimiento IN
                        ('DEPOSITO','TRANSFERENCIA_ENTRANTE')
                            THEN Valor

                        WHEN Tipo_Movimiento IN
                        ('RETIRO','TRANSFERENCIA_SALIENTE')
                            THEN -Valor

                        ELSE 0
                    END
                ),
                0
            ) AS saldo
            FROM MOVIMIENTO
            WHERE cuenta_a_la_que_pertenece = %s
        """, (cuenta_destino,))

        saldo_destino = float(cur.fetchone()['saldo'])

        print("SALDO DESTINO =", saldo_destino)

        nuevo_saldo_destino = saldo_destino + valor

        import uuid

        transaccion_salida = str(uuid.uuid4())[:30]
        transaccion_entrada = str(uuid.uuid4())[:30]

        # MOVIMIENTO SALIDA
        cur.execute("""
            INSERT INTO MOVIMIENTO(
                num_transaccion_pk,
                saldo,
                tipo_movimiento,
                canal,
                valor,
                cuenta_a_la_que_pertenece,
                cuenta_origen,
                cuenta_destino
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            transaccion_salida,
            nuevo_saldo_origen,
            'TRANSFERENCIA_SALIENTE',
            canal,
            valor,
            cuenta_origen,
            cuenta_origen,
            cuenta_destino
        ))

        # MOVIMIENTO ENTRADA
        cur.execute("""
            INSERT INTO MOVIMIENTO(
                num_transaccion_pk,
                saldo,
                tipo_movimiento,
                canal,
                valor,
                cuenta_a_la_que_pertenece,
                cuenta_origen,
                cuenta_destino
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            transaccion_entrada,
            nuevo_saldo_destino,
            'TRANSFERENCIA_ENTRANTE',
            canal,
            valor,
            cuenta_destino,
            cuenta_origen,
            cuenta_destino
        ))

        conn.commit()

        return render_template(
            'asesor/transferencia.html',
            mensaje='Transferencia registrada correctamente'
        )

    except Exception as e:

        print("\n========== ERROR ==========")
        print(e)
        print("===========================\n")

        return render_template(
            'asesor/transferencia.html',
            error=f'Error: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

# IMPLEMENTADA
@asesor_bp.route('/asesor/solicitud-credito', methods=['GET', 'POST'])
def solicitud_credito():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/solicitud_credito.html')
    
    print("Entró a solicitud_credito()")

    conn = None
    cur = None

    try:

        cedula = request.form['cedula']
        valor = float(request.form['valor'])
        plazo = int(request.form['plazo'])
        tasa = float(request.form['tasa'])
        linea = request.form['linea']

        codeudor = request.form.get('codeudor', '').strip()
        fecha_firma = request.form.get('fechaCodeudor', '').strip()

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        #obtiene agencia del asesor
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        asesor = cur.fetchone()

        if not asesor:
            return render_template(
                'asesor/solicitud_credito.html',
                error='No se encontró la agencia del asesor'
            )

        codigo_agencia = asesor['codigoagencia_fk']

        # verifica que el asociado este activo y que exista
        cur.execute("""
            SELECT *
            FROM ASOCIADO
            WHERE cedula_pk = %s
            AND LOWER(estado) = 'activo'
        """, (cedula,))

        asociado = cur.fetchone()

        if not asociado:
            return render_template(
                'asesor/solicitud_credito.html',
                error='El asociado no existe o no se encuentra activo'
            )

        # valida el valor solicitado
        if valor <= 0:
            return render_template(
                'asesor/solicitud_credito.html',
                error='El valor solicitado debe ser mayor a cero'
            )

        # valida el plazo en meses
        if plazo <= 0:
            return render_template(
                'asesor/solicitud_credito.html',
                error='El plazo debe ser mayor a cero'
            )

        # valida la tasa de intereses
        if tasa <= 0:
            return render_template(
                'asesor/solicitud_credito.html',
                error='La tasa debe ser mayor a cero'
            )

        # valida el codeudor si es que fue ingresado
        if codeudor:

            cur.execute("""
                SELECT *
                FROM ASOCIADO
                WHERE cedula_pk = %s
                AND LOWER(estado) = 'activo'
            """, (codeudor,))

            existe_codeudor = cur.fetchone()

            if not existe_codeudor:
                return render_template(
                    'asesor/solicitud_credito.html',
                    error='El codeudor no existe o no está activo'
                )

            if codeudor == cedula:
                return render_template(
                    'asesor/solicitud_credito.html',
                    error='El asociado no puede ser su propio codeudor'
                )

            if not fecha_firma:
                return render_template(
                    'asesor/solicitud_credito.html',
                    error='Debe registrar la fecha de firma del pagaré'
                )

        import uuid

        radicado = "CR-" + str(uuid.uuid4())[:12]

        # crea un credito
        cur.execute("""
            INSERT INTO CREDITO(
                Num_radicado_pk,
                Estado,
                valor_solicitado,
                plazo_meses,
                Tasa_interes_m,
                Linea_credito,
                codigo_agencia_fk
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            radicado,
            'PENDIENTE',
            valor,
            plazo,
            tasa,
            linea,
            codigo_agencia
        ))

        # relacion de asociado y credito
        cur.execute("""
            INSERT INTO SOLICITA(
                CedulaAsociado_fk,
                Num_radicadoCredito_fk
            )
            VALUES (%s,%s)
        """, (
            cedula,
            radicado
        ))

        # registra codeudor si fue ingresado
        if codeudor:

            cur.execute("""
                INSERT INTO ES_CODEUDOR(
                    CedulaAsociado_fk,
                    Num_radicadoCredito_fk,
                    Fecha_Firma
                )
                VALUES (%s,%s,%s)
            """, (
                codeudor,
                radicado,
                fecha_firma
            ))

        conn.commit()

        print("===================================")
        print("SOLICITUD REGISTRADA CORRECTAMENTE")
        print("Radicado:", radicado)
        print("Asociado:", cedula)
        print("Valor:", valor)
        print("===================================")

        return render_template(
            'asesor/solicitud_credito.html',
            mensaje=f'Solicitud registrada correctamente. Radicado: {radicado}'
        )

    except Exception as e:

        print("\n========== ERROR SOLICITUD CRÉDITO ==========")
        print(type(e))
        print(e)
        print("=============================================\n")

        return render_template(
            'asesor/solicitud_credito.html',
            error=f'Error: {str(e)}'
        )

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/pago-cuota', methods=['GET', 'POST'])
def pago_cuota():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('asesor/pago_cuota.html')

    conn = None
    cur = None

    try:
        cedula = request.form['cedula']
        credito = request.form['credito']
        cuota = int(request.form['cuota'])
        valor = float(request.form['valor'])
        fecha_pago = request.form['fecha']
        estado = request.form['estado']

        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Buscar la cuota existente
        cur.execute("""
            SELECT *
            FROM CUOTAS
            WHERE Num_radicado_fk = %s
            AND Num_cuota = %s
        """, (credito, cuota))

        cuota_db = cur.fetchone()

        if not cuota_db:
            return render_template(
                'asesor/pago_cuota.html',
                error="La cuota no existe para este crédito"
            )

        # 2. Actualizar cuota
        cur.execute("""
            UPDATE CUOTAS
            SET Valor_pagado = %s,
                Fech_pago = %s,
                Estado_pago = %s
            WHERE Num_radicado_fk = %s
            AND Num_cuota = %s
        """, (
            valor,
            fecha_pago,
            estado,
            credito,
            cuota
        ))

        # 3. Si no está pagada → marcar mora
        if estado.lower() != "pagada":
            cur.execute("""
                UPDATE CUOTAS
                SET Estado_pago = 'Mora'
                WHERE Num_radicado_fk = %s
                AND Num_cuota = %s
            """, (credito, cuota))

        # 4. Verificar si todas las cuotas están pagadas
        cur.execute("""
            SELECT COUNT(*) AS pendientes
            FROM CUOTAS
            WHERE Num_radicado_fk = %s
            AND Estado_pago != 'Pagada'
        """, (credito,))

        pendientes = cur.fetchone()['pendientes']

        if pendientes == 0:
            cur.execute("""
                UPDATE CREDITO
                SET Estado = 'PAGADO'
                WHERE Num_radicado_pk = %s
            """, (credito,))

        conn.commit()

        print("\n==============================")
        print("PAGO DE CUOTA REGISTRADO")
        print("Crédito:", credito)
        print("Cuota:", cuota)
        print("Valor:", valor)
        print("Estado:", estado)
        print("==============================\n")

        return render_template(
            'asesor/pago_cuota.html',
            mensaje="Pago registrado correctamente"
        )

    except Exception as e:
        print("ERROR PAGO CUOTA:", e)

        return render_template(
            'asesor/pago_cuota.html',
            error=str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


#IMPLEMENTADA
@asesor_bp.route('/asesor/creditos-activos')
def creditos_activos():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # los creditos que estan activos con los datos del asociado
        cur.execute("""
            SELECT 
                c.Num_radicado_pk,
                c.valor_solicitado,
                c.estado,
                c.linea_credito,
                c.plazo_meses,
                a.nombres,
                a.apellidos
            FROM CREDITO c
            INNER JOIN SOLICITA s 
                ON c.Num_radicado_pk = s.Num_radicadoCredito_fk
            INNER JOIN ASOCIADO a
                ON s.CedulaAsociado_fk = a.cedula_pk
            WHERE LOWER(c.estado) != 'pagado'
            ORDER BY c.Num_radicado_pk DESC
        """)

        creditos_db = cur.fetchall()

        creditos = []

        # procesa cada credito
        for c in creditos_db:

            radicado = c['num_radicado_pk']

            # trae las cuotas de cada credito 
            cur.execute("""
                SELECT 
                    Num_cuota,
                    Fech_pago,
                    Valor_pagado,
                    Estado_pago
                FROM CUOTAS
                WHERE Num_radicado_fk = %s
                ORDER BY Num_cuota
            """, (radicado,))

            cuotas = cur.fetchall()

            total_cuotas = len(cuotas)

            #  cuotas pagas
            cuotas_pagadas = sum(
                1 for q in cuotas 
                if q['estado_pago'] and q['estado_pago'].lower() == 'pagada'
            )

            # detectar si esta en mora
            en_mora = any(
                q['estado_pago'] and q['estado_pago'].lower() == 'mora'
                for q in cuotas
            )

            # estado automatico del credito segun lo anterior
            if cuotas_pagadas == total_cuotas and total_cuotas > 0:
                estado_credito = "PAGADO"

            elif en_mora:
                estado_credito = "EN MORA"

            else:
                estado_credito = "ACTIVO"

            # estructura final ya armandose completa con datos
            creditos.append({
                'num_radicado': radicado,
                'nombre_asociado': f"{c['nombres']} {c['apellidos']}",
                'valor_aprobado': c['valor_solicitado'],
                'estado': estado_credito,
                'estado_bd': c['estado'],
                'linea_credito': c['linea_credito'],
                'plazo_meses': c['plazo_meses'],
                'cuotas_pagadas': cuotas_pagadas,
                'total_cuotas': total_cuotas,
                'cuotas': [
                    {
                        'num_cuota': q['num_cuota'],
                        'fech_pago': q['fech_pago'],
                        'valor_pagado': q['valor_pagado'],
                        'estado_pago': q['estado_pago']
                    }
                    for q in cuotas
                ]
            })

        return render_template(
            'asesor/creditos_activos.html',
            creditos=creditos
        )

    except Exception as e:
        print("\n========== ERROR CREDITOS ACTIVOS ==========")
        print(e)
        print("===========================================\n")

        return render_template(
            'asesor/creditos_activos.html',
            creditos=[]
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# Implementada
from datetime import date

@asesor_bp.route('/asesor/mora')
def asociados_mora():

    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    conn = None
    cur = None

    try:
        conn = get_conexion()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Obtiene agencia del asesor logueado
        cur.execute("""
            SELECT CodigoAgencia_fk
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        asesor_agencia = cur.fetchone()

        if not asesor_agencia:
            return render_template('asesor/mora.html', mora=[])

        codigo_agencia = asesor_agencia['codigoagencia_fk']

        # Obtiene nombre del asesor
        cur.execute("""
            SELECT nombres, apellidos
            FROM EMPLEADO
            WHERE Cedula_pk = %s
        """, (session['cedula'],))

        emp = cur.fetchone()

        nombre_asesor = "Desconocido"

        if emp:
            nombre_asesor = f"{emp['nombres']} {emp['apellidos']}"

        # trae los que estan en mora unicamente de la agencia del asesor logueado
        cur.execute("""
            SELECT 
                a.nombres,
                a.apellidos,
                c.Num_radicado_pk,
                cu.Num_cuota,
                cu.Fech_pago,
                cu.Estado_pago
            FROM CUOTAS cu
            INNER JOIN CREDITO c 
                ON cu.Num_radicado_fk = c.Num_radicado_pk
            INNER JOIN SOLICITA s
                ON c.Num_radicado_pk = s.Num_radicadoCredito_fk
            INNER JOIN ASOCIADO a
                ON s.CedulaAsociado_fk = a.cedula_pk
            WHERE cu.Estado_pago = 'Mora'
            AND c.codigo_agencia_fk = %s
            ORDER BY c.Num_radicado_pk, cu.Num_cuota
        """, (codigo_agencia,))

        resultados = cur.fetchall()

        morosos = []

        hoy = date.today()

        for r in resultados:

            if r['fech_pago']:
                dias_mora = (hoy - r['fech_pago']).days
            else:
                dias_mora = 0

            morosos.append({
                'nombre_asociado': f"{r['nombres']} {r['apellidos']}",
                'num_radicado': r['num_radicado_pk'],
                'num_cuota': r['num_cuota'],
                'dias_mora': dias_mora,
                'asesor': nombre_asesor
            })

        return render_template(
            'asesor/mora.html',
            mora=morosos
        )

    except Exception as e:
        print("\n========== ERROR MORA ==========")
        print(e)
        print("================================\n")

        return render_template(
            'asesor/mora.html',
            mora=[]
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

