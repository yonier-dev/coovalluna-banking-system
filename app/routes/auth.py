from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_conexion

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

        # aqui se extraen los valores digitados por el usuario
        cedula = request.form['usuario']
        password = request.form['password']
        perfil = request.form['perfil']
        
        # iniciamos conexion con la base de datos y un cursor para hacer consultas
        conn = get_conexion()
        cur = conn.cursor()

        # buscar segun el perfil
        if perfil == 'asociado':
            cur.execute("SELECT cedula_pk, password, bloqueado, intentos_fallidos FROM ASOCIADO WHERE cedula_pk = %s", (cedula,))
        else:
            cur.execute("SELECT cedula_pk, password, bloqueado, intentos_fallidos, tipo_labor FROM EMPLEADO WHERE cedula_pk = %s", (cedula,))

        # devuelve la fila encontrada o valor vacio
        usuario = cur.fetchone()

        if usuario is None:
            error = 'Usuario no encontrado'

        elif usuario[2]:  # bloqueado
            error = 'Cuenta bloqueada. Contacte al administrador'

        elif usuario[1] != password:
            # si la contraseña es incorrecta se aumenta 1 a los intentos fallidos, si tiene mas de tres se bloquea el perfil
            cur.execute(
                "UPDATE ASOCIADO SET intentos_fallidos = intentos_fallidos + 1 WHERE cedula_pk = %s" if perfil == 'asociado'
                else "UPDATE EMPLEADO SET intentos_fallidos = intentos_fallidos + 1 WHERE cedula_pk = %s",
                (cedula,)
            )
            if perfil == 'asociado':
                cur.execute("UPDATE ASOCIADO SET bloqueado = TRUE WHERE cedula_pk = %s AND intentos_fallidos >= 2", (cedula,))
            else:
                cur.execute("UPDATE EMPLEADO SET bloqueado = TRUE WHERE cedula_pk = %s AND intentos_fallidos >= 2", (cedula,))
            # para guardar los datos commit()
            conn.commit()
            error = 'Contraseña incorrecta'

        elif perfil != 'asociado' and usuario[4] != perfil:
            error = 'El perfil seleccionado no corresponde a este usuario'

        else:
            # login exitoso
            if perfil == 'asociado':
                # reinicio de valores
                cur.execute("UPDATE ASOCIADO SET intentos_fallidos = 0 WHERE cedula_pk = %s", (cedula,))
            else:
                cur.execute("UPDATE EMPLEADO SET intentos_fallidos = 0 WHERE cedula_pk = %s", (cedula,))
            conn.commit()

            session['cedula'] = cedula
            session['perfil'] = perfil

            # cerramos la conexion con el cursor y la base de datos
            cur.close()
            conn.close()

            # se redirecciona al dashboard (menu de cada perfil)
            if perfil == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif perfil == 'asesor':
                return redirect(url_for('asesor.dashboard'))
            else:
                return redirect(url_for('asociado.dashboard'))

        cur.close()
        conn.close()

    # si hay algun error se vuelve a cargar la pagina
    return render_template('login.html', error=error)



# cuando se cierra sesion, vuelve a login
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))