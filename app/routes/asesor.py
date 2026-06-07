from flask import Blueprint, render_template, session, redirect, url_for

asesor_bp = Blueprint('asesor', __name__)

@asesor_bp.route('/asesor/dashboard')
def dashboard():
    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))
    return render_template('asesor/dashboard.html')

# NO IMPLEMENTADA
@asesor_bp.route('/asesor/registro-asociado', methods=['GET', 'POST'])
def registro_asociado():
    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))
    # GET: mostrar formulario vacio
    # POST: verificar si cedula ya existe, si no insertar en ASOCIADO
    # si tipo es fundador, insertar tambien en ASOCIADO_FUND
    # mandar error o mensaje segun resultado
    return render_template('asesor/registro_asociado.html')


# NO IMPLEMENTADA
@asesor_bp.route('/asesor/consulta-asociado')
def consultar_asociado():
    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))
    # recibir busqueda por GET (cedula o nombre)
    # solo buscar asociados de la agencia del asesor en sesion
    # si encuentra: consultar tambien fundador, beneficiarios, cuentas y creditos
    # mandar todo al html o mandar error si no encuentra
    return render_template('asesor/consulta_asociado.html')