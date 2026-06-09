from flask import Blueprint, Response, render_template, request, session, redirect, url_for #Conexion con la pagina en HTML
from db import get_conexion#Conexion con la base de datos remota
from dateutil.relativedelta import relativedelta#Para calcular la fecha fin
import csv #Para generar el archivo cvs
from io import StringIO#Para poder que se pueda escribir correctamente las cadenas en el archivo
#Importando Librerias que me permiten generar el archivo PDF
from io import BytesIO
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

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
    cuenta = request.args.get('cuenta')#Guarda cuenta seleccionada

    conn = get_conexion()
    cur = conn.cursor()
     #Consulta  que me muestra el numero de la cuenta de ahorros, su estado y la agencia a la que pertence.Todo esto perteneciente al asociado loguiado
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
    if cuenta:
        sql += " AND M.cuenta_a_la_que_pertenece = %s"
        parametros.append(cuenta)
    
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

    sql += " ORDER BY M.FECHA_HORA DESC" #Ordena las fechas-hora de forma descendente

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

#  IMPLEMENTADA
@asociado_bp.route('/asociado/descargas')
def descargas():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    # obtener cedula del asociado desde la sesion
    cedula = session['cedula']
    
    conn = get_conexion()
    cur = conn.cursor()
    #Consulta queme muestra el numero de la cuenta de ahorro y del estado de esa cuenta perteneciente al asociado loguiado
    cur.execute("""
    SELECT numero_pk,estado FROM cuenta_ahorro
     where cedula_asociado_fk=%s

                """,(cedula,))
    
    cuentas=[{
        'numero_pk': c[0],
        'estado': c[1]
    }
    for c in cur.fetchall()
    ]
    #Consulta que me relaciona credito con solicita. Ademas muestra el numero de radicado y estado de la cuenta especificamente del asociado loguiado
    cur.execute("""
        SELECT C.num_radicado_pk,C.estado FROM credito C
        INNER JOIN solicita S ON S.num_radicadocredito_fk = C.num_radicado_pk
        WHERE S.cedulaasociado_fk = %s
                """,(cedula,))
    creditos = [{
        'num_radicado': d[0],
        'estado': d[1]
    }
    for d in cur.fetchall()
    ]
    
    cur.close()
    conn.close()
    return render_template('asociado/descargas.html',cuentas=cuentas,
                           creditos=creditos)

@asociado_bp.route('/asociado/descargas/cuenta')
def descargar_cuenta():
    
    cedula = session['cedula']

    cuenta = request.args.get('cuenta')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    formato = request.args.get('formato')
    
    conn = get_conexion()
    cur = conn.cursor()
    
    if fecha_inicio and fecha_fin:
        #Consulta que me haya los movimientos de la cuenta dependiendo de los filtor aplicados
        cur.execute("""
    SELECT
        M.num_transaccion_pk,
        M.fecha_hora,
        M.tipo_movimiento,
        M.valor,
        M.canal
    FROM MOVIMIENTO M
    INNER JOIN REALIZA R
        ON R.num_transaccionmov_fk = M.num_transaccion_pk
    WHERE R.cedulaasociado_fk = %s
      AND M.cuenta_a_la_que_pertenece = %s
      AND DATE(M.fecha_hora) BETWEEN %s AND %s
    ORDER BY M.fecha_hora
    """, (cedula, cuenta, fecha_inicio, fecha_fin))#Variables que van en los %s
    else:
        #Misma consulta pero en este caso funciona sin esperar los valores de las fechas
        cur.execute("""
    SELECT
        M.num_transaccion_pk,
        M.fecha_hora,
        M.tipo_movimiento,
        M.valor,
        M.canal
    FROM MOVIMIENTO M
    INNER JOIN REALIZA R
        ON R.num_transaccionmov_fk = M.num_transaccion_pk
    WHERE R.cedulaasociado_fk = %s
      AND M.cuenta_a_la_que_pertenece = %s
    ORDER BY M.fecha_hora
    """, (cedula, cuenta)) #Variables que van en los %s
    
    filas = cur.fetchall()
    saldo=0#Declaro variable saldo  
    for m in filas:  #Calculo del saldo
                       #str(m[2]).lower()  es una excepsion por si salen valores nulls
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

    if formato == 'csv':    
        archivo = StringIO()
        writer = csv.writer(archivo)

        writer.writerow([  #Nombre de cada columna del archivo
        "Transaccion",
        "Fecha",
        "Tipo",
        "Valor",
        "Canal"
        ])

        for f in filas:   #Informacion que va en cada columna
            writer.writerow([
            f[0],
            f[1],
            f[2],
            f[3],
            f[4]
            ])

        writer.writerow([])
        writer.writerow(["Saldo final", saldo])
    
        cur.close()
        conn.close()
    
        salida = archivo.getvalue()
        archivo.close()

        return Response(
        salida,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=extracto_{cuenta}.csv"
            }
        )
    elif formato=='pdf':
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer)
        estilos = getSampleStyleSheet()
        elementos = []
        elementos.append(
        Paragraph(f"Estado de Cuenta Crédito {cuenta}", estilos['Title'])
        )
        elementos.append(Spacer(1, 12))
        elementos.append(
            Paragraph(
            f"<b>Saldo Final:</b> ${saldo:,.2f}",
            estilos['Heading2']
        )
        )
        datos = [
         ["Transacción", "Fecha", "Tipo", "Valor", "Canal"]
        ]
        for f in filas:
            datos.append([
            str(f[0]),
            str(f[1]),
            str(f[2]),
            str(f[3]),
            str(f[4])
            ])
        tabla = Table(datos)
        tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        elementos.append(tabla)
        pdf.build(elementos)
        buffer.seek(0)

        cur.close()
        conn.close()

        return send_file(
        buffer,
        as_attachment=True,
        download_name=f"credito_{cuenta}.pdf",
        mimetype="application/pdf"
        )


@asociado_bp.route('/asociado/descargas/credito')
def descargar_credito():
    
    conn = get_conexion()
    cur = conn.cursor()
    
    credito = request.args.get('credito')
    formato = request.args.get('formato')
    #Consulta que me permite ver el la fecha,valor y estado de pago del credito.El captura el credito del asociado que este registrado
    cur.execute("""
    SELECT
    Num_cuota,
    Fech_pago,
    Valor_pagado,
    Estado_pago
    FROM CUOTAS
    WHERE Num_radicado_fk = %s
    ORDER BY Num_cuota
    """, (credito,))
    filas = cur.fetchall()

    if formato == 'csv':
        archivo = StringIO()
        writer = csv.writer(archivo)
        writer.writerow([
        'Numero Cuota',
        'Fecha Pago',
        'Valor Pagado',
        'Estado Pago'
        ])
    
        for f in filas:
            writer.writerow([
            f[0],
            f[1],
            f[2],
            f[3]
            ])

        writer.writerow(["Credito", credito])
        writer.writerow([])
    
        cur.close()
        conn.close()

        salida = archivo.getvalue()
        archivo.close()
        return Response(
        salida,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=extracto_{credito}.csv"
            }
        )
    
    elif formato=='pdf':
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer)
        estilos = getSampleStyleSheet()
        elementos = []
        elementos.append(
        Paragraph(f"Estado de Cuenta Crédito {credito}", estilos['Title'])
        )
        elementos.append(Spacer(1, 12))
        datos = [
        ["Cuota", "Fecha Pago", "Valor Pagado", "Estado"]
        ]
        for f in filas:
            datos.append([
            str(f[0]),
            str(f[1]),
            str(f[2]),
            str(f[3])
            ])
        tabla = Table(datos)
        tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        elementos.append(tabla)
        pdf.build(elementos)
        buffer.seek(0)

        cur.close()
        conn.close()

        return send_file(
        buffer,
        as_attachment=True,
        download_name=f"credito_{credito}.pdf",
        mimetype="application/pdf"
        )
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