# 🏦 COOVALLUNA Banking System
 
Sistema de información para la **Cooperativa de Ahorro y Crédito COOVALLUNA Ltda.**  
Desarrollado como proyecto final del curso de Bases de Datos — Universidad del Valle.
 
---
 
## 📋 Descripción
 
Sistema web que permite gestionar asociados, productos financieros y reportes operativos
de la cooperativa. Cuenta con tres perfiles de acceso: **Administrador**, **Asesor/Cajero**
y **Asociado (autoservicio)**.
 
---
 
## 🛠️ Tecnologías utilizadas
 
| Componente | Tecnología |
|---|---|
| Backend | Python 3 + Flask |
| Base de datos | PostgreSQL |
| Conector BD | psycopg2-binary |
| Frontend | HTML5 + CSS3 + Jinja2 |
 
---
 
## 📁 Estructura del proyecto
 
```
coovalluna-banking-system/
├── app/
│   ├── routes/
│   │   ├── auth.py          # login y sesiones
│   │   ├── admin.py         # rutas del administrador
│   │   ├── asesor.py        # rutas del asesor/cajero
│   │   └── asociado.py      # rutas del asociado
│   ├── templates/
│   │   ├── base.html        # plantilla madre
│   │   ├── login.html
│   │   ├── admin/
│   │   ├── asesor/
│   │   └── asociado/
│   ├── app.py               # punto de entrada
│   └── db.py                # conexión a PostgreSQL
├── sql/
│   ├── DDL.sql              # creación de tablas
│   └── DML.sql              # datos de prueba
├── requirements.txt
└── README.md
```
 
---
 
## ⚙️ Instalación y configuración
 
### 1️⃣ Clonar el repositorio
 
```bash
git clone git@github.com:yonier-dev/coovalluna-banking-system.git
cd coovalluna-banking-system
```
 
### 2️⃣ Crear el entorno virtual
 
```bash
# crear entorno virtual
python3 -m venv env
 
# activar en Linux/Mac
source env/bin/activate
 
# activar en Windows
env\Scripts\activate
```
 
### 3️⃣ Instalar dependencias
 
```bash
pip install -r requirements.txt
```
 
### 4️⃣ Configurar la base de datos
 
Abre PostgreSQL y crea la base de datos:
 
```sql
CREATE DATABASE coovalluna;
```
 
Luego ejecuta los scripts en orden:
 
```bash
psql -U postgres -d coovalluna -f sql/DDL.sql
psql -U postgres -d coovalluna -f sql/DML.sql
```
 
### 5️⃣ Configurar la conexión
 
Abre `app/db.py` y actualiza con tus credenciales:
 
```python
def get_conexion():
    conn = psycopg2.connect(
        host="localhost",
        database="coovalluna",
        user="postgres",
        password="tu_password",
        port="5432"
    )
    return conn
```
 
### 6️⃣ Ejecutar el proyecto
 
```bash
python app/app.py
```
 
Abre el navegador en:
 
```
http://127.0.0.1:5000
```
 
---
 
## 👥 Usuarios de prueba
 
| Cédula | Perfil | Contraseña |
|---|---|---|
| 1000001 | Administrador | 1234 |
| 1000004 | Asesor/Cajero | 1234 |
| 2000001 | Asociado | 1234 |
 
---
 
## 📌 Funcionalidades implementadas
 
### 🔑 Autenticación
- Login con tres perfiles
- Control de intentos fallidos
- Bloqueo automático tras 3 intentos
### 👨‍💼 Asesor/Cajero
- Registro y consulta de asociados
- Gestión de cuentas de ahorro
- Registro de movimientos (depósitos, retiros, transferencias)
- Solicitud y seguimiento de créditos
- Reporte de asociados en mora
### 👤 Asociado (autoservicio)
- Consulta de datos personales y beneficiarios
- Extracto de cuentas de ahorro con saldo dinámico
- Consulta de créditos activos
- Descarga de extractos en PDF/CSV
- Solicitud de actualización de datos
### 🛠️ Administrador
- Gestión completa de agencias
- Gestión de empleados y jerarquía de supervisión
- Gestión de asociados y fundadores
- 7 reportes operativos
---
 
## 👨‍💻 Equipo de desarrollo
 
| Nombre | Codigo | Rol | 
|---|---|---|
| Andrés Felipe Quiceno Gil | 2477362 | Backend |
| Yonier Alejandro Vega Rojas | 2477056 | Frontend, Backend |
| Nicolas Cardona Garcia | 2477349 | Backend |
| Daniela Franco Ibarra | 2477154 | Frontend |
 
---
 
## 📄 Licencia
 
Proyecto final — Bases De Datos — Universidad del Valle · 2026
 
