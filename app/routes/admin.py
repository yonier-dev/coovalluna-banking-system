from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint('admin', __name__)

# PANTALLAS DE INICIO
@admin_bp.route('/admin/dashboard')
def dashboard():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')


#GESTION - CRUD AGENCIAS, USUARIOS, EMPLEADOS, ASOCIADOS.

@admin_bp.route('/admin/gestion-agencias')
def gestion_agencias():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_agencias.html')

@admin_bp.route('/admin/gestion-usuarios')
def gestion_usuarios():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_usuarios.html')

@admin_bp.route('/admin/gestion-empleados')
def gestion_empleados():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_empleados.html')

@admin_bp.route('/admin/gestion-asociados')
def gestion_asociados():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/gestion_asociados.html')

# REPORTES Y BITACORA

@admin_bp.route('/admin/reportes')
def reportes():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/reportes.html')

@admin_bp.route('/admin/bitacora')
def bitacora():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/bitacora.html')

# SUPERVISION

@admin_bp.route('/admin/relaciones-supervision')
def relaciones_supervision():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/relaciones_supervision.html')



