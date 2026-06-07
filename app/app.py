from flask import Flask, redirect, url_for
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.asesor import asesor_bp
from routes.asociado import asociado_bp

app = Flask(__name__) # iniciamos la instancia
app.secret_key = 'coovalluna2026'

# usamos register_blueprint para conectar un modulo con la aplicacion principal
app.register_blueprint(auth_bp) 
app.register_blueprint(admin_bp)
app.register_blueprint(asesor_bp)
app.register_blueprint(asociado_bp)

# cuando alguien entra a la url raiz, se ejecutara la funcion index
@app.route('/')
def index():
    # aqui se redirige automaticamente a la pagina login
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)