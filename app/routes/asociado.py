from flask import Blueprint, render_template, session, redirect, url_for

asociado_bp = Blueprint('asociado', __name__)

@asociado_bp.route('/asociado/dashboard')
def dashboard():
    if session.get('perfil') != 'asociado':
        return redirect(url_for('auth.login'))
    return render_template('asociado/dashboard.html')