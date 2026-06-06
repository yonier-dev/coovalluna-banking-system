from flask import Blueprint, render_template, session, redirect, url_for
from db import get_conexion

asociado_bp = Blueprint('asociado', __name__)

@asociado_bp.route('/asociado/dashboard')
def dashboard():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    return render_template('asociado/dashboard.html')

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