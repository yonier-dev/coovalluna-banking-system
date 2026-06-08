from flask import Blueprint, render_template, request, session, redirect, url_for
from db import get_conexion
from dateutil.relativedelta import relativedelta

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

#  IMPLEMENTADA
@asociado_bp.route('/asociado/cuentas')
def cuentas():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    cedula= session['cedula']
    
    #Aqui se leen los valores de los filtros puestos en la pagina
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    canal = request.args.get('canal')
    
    conn = get_conexion()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        Numero_pk,
        Estado,
        CodigoAgencia_fk
    FROM CUENTA_AHORRO
    WHERE cedula_asociado_fk = %s
""", (cedula,))

    cuentas = [
    {
        'numero_pk': c[0],
        'estado': c[1],
        'agencia': c[2]
    }
    for c in cur.fetchall()
    ]

    #Consulta SQL que muestra los movimientos de cuentas hechos por el asociado registrado
    sql = """
    SELECT M.NUM_TRANSACCION_PK,M.FECHA_HORA
    ,M.TIPO_MOVIMIENTO,M.VALOR,M.CANAL
    FROM REALIZA R 
    INNER JOIN movimiento M ON R.num_transaccionmov_fk = M.num_transaccion_pk
    WHERE R.cedulaasociado_fk = %s 
    """

    parametros = [cedula] #Variable que va capturar valores de los filtros
    #Logica que tiene que ver con el filtro
    if fecha_inicio:
        sql += " AND DATE(M.FECHA_HORA) >= %s" # %s captura valor seleccionado en pantalla
        parametros.append(fecha_inicio)   #Y agrega fragmentos de esas consultas dentro de la condicion where

    if fecha_fin:
        sql += " AND DATE(M.FECHA_HORA) <= %s"#DATE(M.FECHA_HORA) extrae solamente la fecha en este caso
        parametros.append(fecha_fin)

    if canal:
        sql += " AND M.CANAL = %s"
        parametros.append(canal)  #Se pone el append para garantizar que se arme la tupla(cedula,canal) en este caso 
                                  #se hace con el objetivo de que funcione adecuadamente la consulta porque se requieren dos valores para funcionar

    sql += " ORDER BY M.FECHA_HORA DESC"

    cur.execute(sql, tuple(parametros))

    filas = cur.fetchall()

    movimientos = [ #Diccionario para guardar los valores a mostrar en la interfaz
        {
            'num_transaccion': m[0],
            'fecha': m[1].date(),
            'hora': m[1].strftime('%H:%M:%S'),#El comando .strftime('%H:%M:%S') es para separar la hora de la fecha en este caso
            'tipo_movimiento': m[2],
            'valor': m[3],
            'canal': m[4]
        }
        for m in filas
    ]
    saldo=0#Declaro variable saldo
    for m in filas:     #str(m[2]).lower()  es una excepsion por si salen valores nulls
        tipoMovimiento= str(m[2]).lower()#tipo_movimiento  [3]valor
        if tipoMovimiento=='deposito':
            saldo=saldo+m[3]#Incrementa saldo
        elif tipoMovimiento=='retiro':
            saldo -= m[3]#Se le resta al saldo
        elif tipoMovimiento == 'transferencia entrante':
            saldo += m[3]#Incrementa saldo
        elif tipoMovimiento == 'transferencia saliente':
            saldo -= m[3]#Se le resta al saldo
    
    if saldo < 0:#Pequeña excepcion. Si saldo da numeros negativos es igual a 0
        saldo=0
    cur.close()
    conn.close()

    print("MOVIMIENTOS:", movimientos)

    return render_template('asociado/cuentas.html',
        movimientos=movimientos,
        cuentas=cuentas,
        saldo=saldo)

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
                'num_cuota': q[0],    #Se toma la fecha del primer vencimiento y se le suma la cuota . ejemplo si dice 4 cuotas seria en realidad 3 porque la primer cuota debe sumar 0 meses
                'fecha_vencimiento':  c[6] + relativedelta(months=q[0]-1),  # temporalmente uso la primera fecha de vencimiento mientras resuelvo un detalle con esto
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

    cur.close()
    conn.close()
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

#  IMPLEMENTADA

@asociado_bp.route('/asociado/actualizar-datos', methods=['GET', 'POST'])
def actualizar_datos():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    cedula= session['cedula']

    conn = get_conexion()
    cur = conn.cursor()
    #Consulta que busca algunos atributos de la tabla asociado
    cur.execute("""
      select cedula_pk,
      telefono,correo,direccion from asociado
      where cedula_pk= %s
                """,(cedula,))
     #Guardo datos en diccionario. 
    asociado=None
    for a in cur.fetchall():
        asociado = {
        'cedula_pk': a[0],
        'telefono': a[1],
        'correo': a[2],
        'direccion': a[3]
        }
    

    if request.method == 'POST':
        telefono = request.form['telefono']
        correo = request.form['correo']
        direccion = request.form['direccion']
     #Consulta SQL donde se insertan los datos ala tabla de solicitudes del asociado con respecto a la modificacion de unos datos personales
        cur.execute(""" 
        INSERT INTO SOLICITUD_ACTUALIZACION
        (
        cedula_asociado_fk,
        telefono_nuevo,
        correo_nuevo,
        direccion_nueva
        )
        VALUES (%s,%s,%s,%s)
        """,
        (
        cedula, 
        telefono,
        correo,
        direccion
        ))
        conn.commit()#Para guardar cambios en la nube de la base de datos
    
    cur.execute("""
    SELECT estado
    FROM SOLICITUD_ACTUALIZACION
    WHERE cedula_asociado_fk = %s
    LIMIT 1
     """ , (cedula,)) #LIMIT garantiza consultar la mas reciente
    
    solicitud = None
    for s in cur.fetchall():
        solicitud = { #Se guarda solicitud de la consulta hecha
        'estado': s[0]
        }
    
    cur.close()
    conn.close()

    return render_template('asociado/actualizar_datos.html',    
                         asociado=asociado,
                         solicitud=solicitud,
                         mensaje=None)