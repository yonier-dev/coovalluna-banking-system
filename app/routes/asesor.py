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


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/actualizar-contacto', methods=['GET', 'POST'])
def actualizar_contacto():
    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))
    # GET → muestra los datos actuales del asociado (teléfono, correo, dirección).
    # POST → actualiza esos datos de contacto en la base de datos. mirar html
    # No se permite modificar estado de vinculación ni datos personales (cédula, fecha de nacimiento).
    # El asesor solo puede actualizar asociados de su agencia.
    return render_template('asesor/actualizar_contacto.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/beneficiarios', methods=['GET', 'POST'])
def beneficiarios():
    # GET → muestra los beneficiarios actuales del asociado.
    # POST → permite agregar nuevos beneficiarios (máximo 4 por asociado).
    # Antes de guardar, validar que el porcentaje total de participación sea exactamente 100%.
    # Registrar documento, nombre, parentesco, porcentaje y teléfono.
    return render_template('asesor/beneficiarios.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/apertura-cuenta', methods=['GET', 'POST'])
def apertura_cuenta():
    # GET → muestra formulario para abrir cuenta de ahorro.
    # POST → inserta nueva cuenta vinculada al asociado y agencia del asesor.
    # El sistema debe generar automáticamente un número único de cuenta.
    # Solo se permite abrir cuentas para asociados en estado “activo”.
    return render_template('asesor/apertura_cuenta.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/deposito', methods=['GET', 'POST'])
def deposito():
    # GET → muestra formulario para registrar depósito.
    # POST → inserta movimiento tipo “depósito” con valor, fecha, hora y canal.
    # El saldo no se guarda como campo fijo, se calcula dinámicamente.
    # No se pueden eliminar movimientos históricos.
    return render_template('asesor/deposito.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/retiro', methods=['GET', 'POST'])
def retiro():
    # GET → muestra formulario para registrar retiro.
    # POST → valida que el saldo calculado sea suficiente antes de realizar el retiro.
    # Si el saldo es insuficiente, mostrar mensaje de error y no registrar el movimiento.
    return render_template('asesor/retiro.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/transferencia', methods=['GET', 'POST'])
def transferencia():
    # GET → muestra formulario con cuentas origen y destino.
    # POST → registra dos movimientos simultáneos:
    #   - En cuenta origen: “transferencia saliente”
    #   - En cuenta destino: “transferencia entrante”
    # Ambos movimientos deben tener misma fecha, hora y valor.
    return render_template('asesor/transferencia.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/solicitud-credito', methods=['GET', 'POST'])
def solicitud_credito():
    # GET → muestra formulario para radicar crédito.
    # POST → inserta nuevo crédito con valor solicitado, plazo, tasa y línea de crédito.
    # El sistema genera automáticamente el número de radicado.
    # Si hay codeudor, registrar su cédula y fecha de firma del pagaré.
    return render_template('asesor/solicitud_credito.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/pago-cuota', methods=['GET', 'POST'])
def pago_cuota():
    # GET → muestra formulario con créditos activos.
    # POST → registra número de cuota, fecha de pago y valor pagado.
    # Si la fecha de pago es posterior al vencimiento, marcar como “pagado con mora”.
    # Actualizar el estado general del crédito si todas las cuotas están pagadas.
    return render_template('asesor/pago_cuota.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/creditos-activos')
def creditos_activos():
    # GET → muestra los créditos activos o desembolsados del asociado.
    # Debe mostrar: valor de cuota, fecha de próximo vencimiento, número de cuotas pagadas y estado general.
    # El asesor solo puede ver créditos de asociados de su agencia.
    return render_template('asesor/creditos_activos.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/mora')
def asociados_mora():
    # GET → lista los asociados con cuotas vencidas o en mora.
    # Debe mostrar: nombre del asociado, número de crédito, número de cuota vencida, días de mora y asesor responsable.
    # Calcular días de mora desde la fecha de vencimiento hasta la actual.
    # Mostrar solo asociados en mora de la agencia del asesor.
    return render_template('asesor/mora.html')

