from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def dashboard():
    if session.get('perfil') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')