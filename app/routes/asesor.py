from flask import Blueprint, render_template, session, redirect, url_for

asesor_bp = Blueprint('asesor', __name__)

@asesor_bp.route('/asesor/dashboard')
def dashboard():
    if session.get('perfil') != 'asesor':
        return redirect(url_for('auth.login'))
    return render_template('asesor/dashboard.html')