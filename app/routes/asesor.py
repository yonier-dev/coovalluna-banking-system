from flask import Blueprint, render_template, session, redirect, url_for, request
from db import get_conexion
from psycopg2.extras import RealDictCursor

asesor_bp = Blueprint('asesor', __name__)


@asesor_bp.route('/asesor/dashboard')
def dashboard():
    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))

    return render_template('asesor/dashboard.html')


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