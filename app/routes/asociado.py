from flask import Blueprint, render_template, session, redirect, url_for
from db import get_conexion

asociado_bp = Blueprint('asociado', __name__)

@asociado_bp.route('/asociado/dashboard')
def dashboard():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    return render_template('asociado/dashboard.html')

# IMPLEMENTADA
@asociado_bp.route('/asociado/datos-personales')
def datos_personales():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    
    cedula = session['cedula']
    conn = get_conexion()
    cur = conn.cursor()

    # datos básicos
    cur.execute("SELECT * FROM ASOCIADO WHERE cedula_pk = %s", (cedula,))
    fila = cur.fetchone()
    asociado = {
        'cedula_pk': fila[0],
        'nombres': fila[1],
        'apellidos': fila[2],
        'fecha_na': fila[3],
        'telefono': fila[4],
        'estado': fila[5],
        'fech_afil': fila[6],
        'municipio': fila[7],
        'correo': fila[8],
        'direccion': fila[9]
    }

    # se verifica si es fundador
    cur.execute("SELECT * FROM ASOCIADO_FUND WHERE cedula_pk = %s", (cedula,))
    fila_fund = cur.fetchone()
    fundador = None
    if fila_fund:
        fundador = {
            'num_acta': fila_fund[1],
            'ano_reconocimiento': fila_fund[2],
            'descripcion_beneficios': fila_fund[3],
            'fecha_firma': fila_fund[4]
        }

    # beneficiarios
    cur.execute("SELECT * FROM BENEFICIARIO WHERE cedulaAsociado_fk = %s", (cedula,))
    beneficiarios = [
        {
            'cedula_pk': b[0],
            'parentesco': b[2],
            'nombre_completo': b[3],
            'porcentaje_participacion': b[4],
            'telefono': b[5]
        } for b in cur.fetchall()
    ]

    cur.close()
    conn.close()
    return render_template('asociado/datos_personales.html', 
                         asociado=asociado, 
                         fundador=fundador,
                         beneficiarios=beneficiarios)

# NO IMPLEMENTADA
@asociado_bp.route('/asociado/cuentas')
def cuentas():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    # listar las cuentas de ahorro del asociado
    # el saldo se calcula sumando depositos y restando retiros y transferencias salientes
    # mostrar extracto con fecha, valor, tipo y canal de cada movimiento
    # permitir filtrar por rango de fechas y por canal (presencial, app movil, cajero automatico)
    # solo puede ver sus propias cuentas
    # tener en cuenta variables del .html
    return render_template('asociado/cuentas.html')

#  IMPLEMENTADA
@asociado_bp.route('/asociado/creditos')
def creditos():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    
    cedula = session['cedula']
    conn = get_conexion()
    cur = conn.cursor()
     #Consulta SQL  que obtiene los creditos del asociado
    cur.execute("""
               SELECT
            C.num_radicado_pk,
            C.valor_aprovado,
            C.linea_credito,
            C.estado,
            C.plazo_meses,
            C.tasa_interes_m,
            C.fech_prim_ven
        FROM CREDITO C
        INNER JOIN SOLICITA S
            ON S.num_radicadoCredito_fk = C.num_radicado_pk
        WHERE S.cedulaAsociado_fk = %s 
          AND C.estado <> 'cancelado';
                """, (cedula,)) # el comando %s  permite ver la cedula obtenida anteriormente
    
    filas_creditos = cur.fetchall()
    creditos = []# Se crea Lista de creditos
    for c in filas_creditos:
        num_radicado = c[0]

     # Esta consulta es para obtener las cuotas asociadas al credito
        cur.execute("""
           SELECT
        Num_cuota,
        Fech_pago,
        Valor_pagado,
        Estado_pago
    FROM CUOTAS
    WHERE Num_radicado_fk = %s
    ORDER BY Num_cuota
        """, (num_radicado,))

    filas_cuotas = cur.fetchall()

    cuotas = [
            {
                'num_cuota': q[0],
                'fecha_vencimiento': c[6],  # temporalmente uso la primera fecha de vencimiento mientras resuelvo un detalle con esto
                'fech_pago': q[1],
                'valor_pagado': q[2],
                'estado_pago': q[3]
            }
            for q in filas_cuotas
        ]

    cuotas_pagadas = len([
            q for q in cuotas
            if q['estado_pago'] and q['estado_pago'].lower() != 'pendiente'
        ])

    creditos.append({
            'num_radicado': c[0],
            'valor_aprobado': c[1],
            'linea_credito': c[2],
            'estado': c[3],
            'plazo_meses': c[4],
            'tasa_interes': c[5],
            'cuotas_pagadas': cuotas_pagadas,
            'cuotas': cuotas
        })

    print("CEDULA:", cedula)#Outputs para saber que en efecto funciona correctamente
    cur.close()
    print("RADICADO:", num_radicado)
    conn.close()
    
    print("CREDITOS:", creditos)
   
    return render_template('asociado/creditos.html',creditos=creditos)

# NO IMPLEMENTADA
@asociado_bp.route('/asociado/descargas')
def descargas():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    # obtener cedula del asociado desde la sesion
    # cedula = session['cedula']

    # permitir elegir entre formato PDF o CSV antes de descargar
    # el extracto debe contener los movimientos del filtro aplicado
    # mas el saldo calculado al final del periodo
    # el estado de cuenta del credito debe contener cuotas, fechas de vencimiento,
    # fechas de pago y montos abonados
    
    # mandar cuentas y creditos al html para llenar los selectores
    # return render_template('asociado/descargas.html', cuentas=cuentas, creditos=creditos)
    return render_template('asociado/descargas.html')

@asociado_bp.route('/asociado/descargas/cuenta')
def descargar_cuenta():
    # recibir cuenta, fecha_inicio, fecha_fin y formato (pdf o csv) por GET
    # consultar movimientos filtrados de esa cuenta
    # calcular saldo dinamico
    # si formato == 'pdf': generar PDF con reportlab o weasyprint
    # si formato == 'csv': generar CSV con el modulo csv de python
    # retornar el archivo como descarga con send_file
    pass


@asociado_bp.route('/asociado/descargas/credito')
def descargar_credito():
    # recibir credito y formato (pdf o csv) por GET
    # consultar cuotas del credito con fechas de vencimiento, pago y montos
    # si formato == 'pdf': generar PDF
    # si formato == 'csv': generar CSV
    # retornar el archivo como descarga con send_file
    pass

# NO IMPLEMENTADA

@asociado_bp.route('/asociado/actualizar-datos', methods=['GET', 'POST'])
def actualizar_datos():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))

    # GET: mostrar formulario con telefono, correo y direccion actuales
    # POST: registrar solicitud como pendiente, no aplicar cambio de inmediato
    # un asesor es quien aprueba o rechaza la solicitud
    # mostrar el estado actual de la solicitud: pendiente, aprobada o rechazada
    # tener en cuenta variables del .html

    # mandar al html: datos del asociado, solicitud con su estado si existe

    # datos vacios mientras el backend no esta listo
    asociado = {
        'cedula_pk': '',
        'nombres': '',
        'apellidos': '',
        'telefono': '',
        'correo': '',
        'direccion': ''
    }

    return render_template('asociado/actualizar_datos.html',    
                         asociado=asociado,
                         solicitud=None,
                         mensaje=None)